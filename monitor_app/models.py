from django.db import models

class Location(models.Model):
    program_name = models.CharField(max_length=255)
    room_name = models.CharField(max_length=255)
    floor = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

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