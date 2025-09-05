import secrets, statistics
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
from django.db import transaction

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

def _robust_filter_by_mad(objs, get_value=lambda o: o.congestion_level, k=3):
    """
    objs: Collected の iterable
    get_value: 値の取り出し関数（デフォ: congestion_level 1..5）
    k: しきい値の強さ（一般に 2.5〜3 が無難）
    戻り値: 外れ値を除いた objs の list
    """
    vals = [get_value(o) for o in objs]
    if len(vals) < 10:
        return list(objs)  # サンプル少ない時は弾かない

    med = statistics.median(vals)
    abs_dev = [abs(v - med) for v in vals]
    mad = statistics.median(abs_dev)
    if mad == 0:
        return list(objs)  # 全部ほぼ同じ → 弾かない

    # 正規分布換算のスケーリング係数
    s = 1.4826 * mad
    keep = []
    for o, v in zip(objs, vals):
        if abs(v - med) <= k * s:
            keep.append(o)
    return keep

def weighted_average_congestion(queryset, valid_time_minutes: int):
    """
    新しいデータほど重みが大きい重み付き平均。外れ値除去は事前にやる想定。
    """
    now = timezone.now()
    weighted_sum = 0.0
    total_weight = 0.0
    for c in queryset:
        # 分単位の経過時間
        dt_min = (now - c.published_at).total_seconds() / 60.0
        # あなたの元ロジック：1.25乗で減衰、0未満は切り捨て
        weight = max(0.0, valid_time_minutes - (dt_min ** 1.25)) / valid_time_minutes
        if weight <= 0:
            continue
        weighted_sum += c.congestion_level * weight
        total_weight += weight

    if total_weight > 0:
        # 1..5 にクランプ（任意）
        avg = weighted_sum / total_weight
        return max(1.0, min(5.0, avg))
    return None

@staff_member_required
def aggregates_data(request):
    """
    Collected を一定時間で集計し CongestionLevel に保存。
    外れ値は MAD で除外してから重み付き平均。
    データが無い場合は計算せず level=0 として保存。
    """
    valid_time = 15  # minutes
    now = timezone.now()
    cutoff = now - timedelta(minutes=valid_time)

    # 事前に最近データをまとめて引く
    location_qs = Location.objects.all()
    collected_recent = (
        Collected.objects
        .filter(published_at__gte=cutoff)
        .select_related("location")
    )

    # まとめて更新するが、個別に upsert する
    with transaction.atomic():
        for loc in location_qs:
            # 該当ロケーションの最近データ
            samples = list(
                collected_recent
                .filter(location=loc)
                .order_by("-published_at")
            )

            # 1) 最近データが 0 件 → 計算せず level=0 で保存
            if not samples:
                CongestionLevel.objects.update_or_create(
                    location=loc,
                    defaults={
                        "level": 0.0,
                        "reliability": 0,
                        "last_update_at": now,
                    },
                )
                continue

            # 2) 外れ値除去（中央値+MAD, k=3）
            samples_robust = _robust_filter_by_mad(samples, k=3)
            num_used = len(samples_robust)

            # 3) 除外後に 0 件 → 計算せず level=0 で保存
            if num_used == 0:
                CongestionLevel.objects.update_or_create(
                    location=loc,
                    defaults={
                        "level": 0.0,
                        "reliability": 0,
                        "last_update_at": now,
                    },
                )
                continue

            # 4) 重み付き平均を計算（戻り値 None なら level=0 扱い）
            avg = weighted_average_congestion(
                samples_robust,
                valid_time_minutes=valid_time
            )

            if avg is None:
                # 計算不能時も 0 として保存
                CongestionLevel.objects.update_or_create(
                    location=loc,
                    defaults={
                        "level": 0.0,
                        "reliability": num_used,
                        "last_update_at": now,
                    },
                )
                continue

            # 5) 正常計算できたときはその値で保存
            CongestionLevel.objects.update_or_create(
                location=loc,
                defaults={
                    "level": float(avg),
                    "reliability": num_used,   # 除外後に使った点の数
                    "last_update_at": now,
                },
            )

    return render(request, "aggre.html", {})

def display(request,floor_given):
    congestion_levels_each_floor = {}
    for floor in range(1,5):
        congestion_levels_each_floor[floor] = CongestionLevel.objects.filter(location__floor=floor)

    if floor_given == 1729:
        time_now = timezone.now()
        return render(request, 'display_user.html',{'congestion_level': congestion_levels_each_floor,'floor_given':0, 'time_now':time_now})
 
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
def food_cs_api(request):
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
