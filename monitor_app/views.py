from django.shortcuts import render
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
from .serializers import CongestionLevelItemSerializer

def index(request):
    return render(request, 'index.html')

class DataCreate(CreateView):
    model = Collected
    form_class = CongestionForm
    template_name = "con_form.html"  # 任意のテンプレート名でOK
    success_url = "display/0/"  # 登録完了後の遷移先（URL名は適宜変更）

def initial(request):
    return HttpResponse("Hello, World!")

def make_random_data(request):
    repeat = 1000  # 生成するデータの数
    for _ in range(repeat):
        collected = Collected.objects.create(
            location=random.choice(Location.objects.all()),
            congestion_level=random.randint(0,100),
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
        # time_diffを「分」単位で計算
        time_diff = (now - congestion.published_at).total_seconds() / 60  # ここはそのままでOK
        weight = max(0, valid_time - (time_diff**(1.25))) / valid_time  # 分単位で重みを計算 重みは1.25乗にしよう
        weighted_sum += congestion.congestion_level * weight
        total_weight += weight
    if total_weight > 0:
        return weighted_sum / total_weight
    return None


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
        if filtered_by_loc.exists():
            avg = weighted_average_congestion(filtered_by_loc, valid_time)
            if avg is not None:
                congestion_level_obj, created = CongestionLevel.objects.get_or_create(location=loc)
                congestion_level_obj.level = avg
                congestion_level_obj.save()
    return render(request, 'aggre.html', {})

def display(request,floor_given):
    congestion_levels_each_floor = {}
    for floor in range(1,5):
        congestion_levels_each_floor[floor] = CongestionLevel.objects.filter(location__floor=floor)
 
    return render(request, 'display.html', {'congestion_level': congestion_levels_each_floor,'floor_given':floor_given})

def display_json(request):
    congestion_level_each_floor_json = {}
    for floor in range(1,5):
        congestion_levels = CongestionLevel.objects.filter(location__floor=floor)
        congestion_level_each_floor_json[str(floor)] = [
            {
                "program_name": cl.location.program_name,
                "room_name": cl.location.room_name,
                "level": cl.level,
                "reliability": cl.reliability,
                "comment":cl.location.comment,
            }
            for cl in congestion_levels
        ]
    return JsonResponse({"data":congestion_level_each_floor_json})


@api_view(['GET'])
def display_json_api(request):
    # N+1回避
    qs = (CongestionLevel.objects
          .select_related('location')
          .order_by('location__floor', 'location__room_name'))

    # まず「1件＝1行」形式にシリアライズ
    items = CongestionLevelItemSerializer(qs, many=True).data

    # 目的の形（floorごとの配列）に組み立て直す
    floors = {}
    for it in items:
        key = str(it['floor'])
        floors.setdefault(key, []).append({
            "program_name": it["program_name"],
            "room_name": it["room_name"],
            "level": it["level"],
            "reliability": it["reliability"],
            "comment": it["comment"],
        })

    return Response({"data": floors})