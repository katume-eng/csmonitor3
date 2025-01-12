from django.db import models
from django.utils import timezone

class Location(models.Model):
    program_name = models.CharField(max_length=255, default="default program")
    room_name = models.CharField(max_length=255, default="default room")
    floor = models.IntegerField(default=0)
    comment = models.TextField(default="default comment")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.program_name} - {self.room_name} - {self.floor}"

class Collected(models.Model):
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    congestion_level = models.IntegerField()
    published_at = models.DateTimeField()

    def __str__(self):
        return f"{self.location.name} - {self.congestion_level.level} - {self.published_at}"

    
class CongestionLevel(models.Model):
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    level = models.IntegerField(default=0)