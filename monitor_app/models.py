from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# Defining locations' data
class Location(models.Model):
    program_name = models.CharField(max_length=255, default="default program")
    room_name = models.CharField(max_length=255, default="default room")
    floor = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_at = models.DateTimeField(default=timezone.now)
    floor_local_id = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.program_name} at {self.room_name} on {self.floor} floor, id={self.id}"

class Collected(models.Model):
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    congestion_level = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    published_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.location.program_name} - {self.congestion_level} - {self.published_at}"

# saving location's congestion level 
class CongestionLevel(models.Model):
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    level = models.IntegerField(default=0)
    last_update_at = models.DateTimeField(default=timezone.now)
    reliability = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.location.program_name} - {self.level}level - {self.reliability}のデータ数"