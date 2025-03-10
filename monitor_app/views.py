from django.shortcuts import render
from django.http import HttpResponse
from .models import Location, Collected, CongestionLevel
from django.utils import timezone
from datetime import timedelta
import random

def initial(request):
    return HttpResponse("Hello, World!")

def make_random_data(request):
    repeat = 10
    for _ in range(repeat):
        collected = Collected.objects.create(
            location=random.choice(Location.objects.all()),
            congestion_level=random.randint(0,100),
            published_at=timezone.now()
            )
        collected.save()
    return HttpResponse(f"Created {repeat} random data")

def aggregates_data(request): # 一定時間ごとに集計して、データベースに保存する。各端末が計算するわけではない
    # aglegation of all the data
    collected_data = Collected.objects.all()
    location_data = Location.objects.all()
    congestion_level_data = CongestionLevel.objects.all()
    valid_time = 30 # minutes

    # aglegation of all the data
    collected_data_filltered = collected_data.filter(published_at__gte=timezone.now() - timedelta(minutes=valid_time))
    
    for loc in location_data:
        filltered_data_filltered_by_loc = collected_data_filltered.filter(location=loc)
        if filltered_data_filltered_by_loc:
            weighted_sum = 0
            total_weight = 0
            for congestion_level in filltered_data_filltered_by_loc:
                time_diff = (timezone.now() - congestion_level.published_at).total_seconds() / 60
                weight = max(0, valid_time - time_diff) / valid_time
                weighted_sum += congestion_level.congestion_level * weight
                total_weight += weight
            if total_weight > 0:
                weighted_average = weighted_sum / total_weight
                congestion_level_obj, created = CongestionLevel.objects.get_or_create(location=loc)
                congestion_level_obj.level = weighted_average
                congestion_level_obj.save()

def display(request):
    congestion_levels = CongestionLevel.objects.select_related('location').all()
    # templates/display/index.htmlなら
    # 'display.index.html
    return render(request, 'display.html', {'congestion_level': congestion_levels})