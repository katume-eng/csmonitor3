import secrets
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from .models import Location, Collected, CongestionLevel
from django.utils import timezone
from datetime import timedelta
import random
from django.views.generic import CreateView
from .forms import CongestionForm
from django.urls import reverse_lazy
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CongestionLevelItemSerializer, CongestionLevelCreateSerializer
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_control

def index(request):
    return render(request, 'index.html')

@staff_member_required
def make_random_data(request):
    repeat = 100
    for _ in range(repeat):
        collected = Collected.objects.create(
            location=random.choice(Location.objects.all()),
            congestion_level=random.randint(1,5),
            published_at=timezone.now()
            )
        collected.save()
    return HttpResponse(f"Created {repeat} random data")

def weighted_average_congestion(queryset, valid_time):
    """
    混雑度の重み付き平均を計算する。新しいデータほど重みが大きい。
    :param queryset: 対象のCollectedクエリセット
    :param valid_time: 有効時間（分）
    :return: 重み付き平均値（float）
    """
    weighted_sum = 0
    total_weight = 0
    now = timezone.now()
    for congestion in queryset:
        time_diff = (now - congestion.published_at).total_seconds() / 60
        weight = max(0, valid_time - (time_diff**(1.25))) / valid_time  # 分単位で重みを計算 重みは1.25乗にしよう
        weighted_sum += congestion.congestion_level * weight
        total_weight += weight
    if total_weight > 0:
        return weighted_sum / total_weight
    return None

@staff_member_required
def aggregates_data(request):
    """
    一定時間ごとに集計して、データベースに保存する。各端末が計算するわけではない
    """
    collected_data = Collected.objects.all()
    location_data = Location.objects.all()
    valid_time = 15  # minutes
    collected_data_filtered = collected_data.filter(published_at__gte=timezone.now() - timedelta(minutes=valid_time))

    for loc in location_data:
        filtered_by_loc = collected_data_filtered.filter(location=loc)
        num_filtered_by_loc = filtered_by_loc.count()
        if filtered_by_loc.exists():
            avg = weighted_average_congestion(filtered_by_loc, valid_time)
            if avg is not None:
                congestion_level_obj, created = CongestionLevel.objects.get_or_create(location=loc)
                congestion_level_obj.level = avg
                congestion_level_obj.reliability = num_filtered_by_loc
                congestion_level_obj.save()
    return render(request, 'aggre.html', {})

def display(request,floor_given):
    congestion_levels_each_floor = {}
    for floor in range(1,5):
        congestion_levels_each_floor[floor] = CongestionLevel.objects.filter(location__floor=floor)

    if floor_given == 1729:
        return render(request, 'display_user.html',{'congestion_level': congestion_levels_each_floor,'floor_given':0})
 
    return render(request, 'display.html', {'congestion_level': congestion_levels_each_floor,'floor_given':floor_given})

@api_view(['GET', 'POST'])
def display_json_api(request):
    if request.method == 'GET':
        qs = (CongestionLevel.objects
              .select_related('location')
              .order_by('location__floor', 'location__room_name'))
        data = CongestionLevelItemSerializer(qs, many=True).data

        # 目的の形（floorごとの配列）に組み立て直す
        floors = {}
        for it in data:
            key = str(it['floor'])
            floors.setdefault(key, []).append({
                "program_name": it["program_name"],
                "room_name": it["room_name"],
                "level": it["level"],
                "reliability": it["reliability"],
            })

        return Response({"data": floors})
    
    elif request.method == 'POST':
        serializer = CongestionLevelCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@require_http_methods(["GET", "POST"])
@cache_control(no_store=True)  # 戻る時の履歴キャッシュを抑止（保険）
def con_form_view(request):
    qs = Location.objects.all().order_by('floor', 'room_name')

    if request.method == 'GET':
        # 1) ワンタイムnonceを発行→セッションへ保存
        nonce = secrets.token_urlsafe(24)
        request.session['form_nonce'] = nonce

        form = CongestionForm()
        form.fields['location'].queryset = qs
        return render(request, 'con_form.html', {'form': form, 'nonce': nonce})

    # POST ----------------------------------------------------
    # 2) nonce照合（使い捨て：popで取り出して破棄）
    posted = request.POST.get('nonce')
    saved = request.session.pop('form_nonce', None)
    if not posted or posted != saved:
        # 二重送信/戻る→再送/別タブ再送 などを検知
        # 新しいnonceを再発行してフォームを再表示
        nonce = secrets.token_urlsafe(24)
        request.session['form_nonce'] = nonce

        form = CongestionForm()  # 直前入力を保持したいなら CongestionForm(request.POST) に
        form.fields['location'].queryset = qs
        return render(
            request,
            'con_form.html',
            {'form': form, 'nonce': nonce, 'error': 'データの送信をやり直してください'},
            status=409
        )

    # 3) 通常バリデーション
    form = CongestionForm(request.POST)
    form.fields['location'].queryset = qs
    if not form.is_valid():
        # 失敗時も新しいnonceを配布
        nonce = secrets.token_urlsafe(24)
        request.session['form_nonce'] = nonce
        return render(request, 'con_form.html', {'form': form, 'nonce': nonce}, status=400)

    # 4) 保存→PRG（Post → Redirect → Get）
    congestion = form.save(commit=False)
    congestion.published_at = timezone.now()
    # try:
    congestion.save()
    # except IntegrityError:
    #     # （任意）ユニーク制約違反時のハンドリング
    #     pass

    return redirect('display', floor_given=1729)

@api_view(['GET', 'POST'])
def zero_api(request):
    if request.method == 'GET':
        # 0階の CongestionLevel だけ取得
        qs = (CongestionLevel.objects
              .select_related('location')
              .filter(location__floor=0)
              .order_by('location__floor_local_id'))

        data = CongestionLevelItemSerializer(qs, many=True).data

        # floor_local_id をキーにした辞書に組み直す
        result = {}
        for it in data:
            fid = str(it["floor_local_id"])  # JSON のキーは文字列
            result[fid] = {
                "program_name": it["program_name"],
                "room_name": it["room_name"],
                "level": it["level"],
                "reliability": it["reliability"],
            }

        return Response({"data": result})
    
    elif request.method == 'POST':
        serializer = CongestionLevelCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
