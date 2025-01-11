from django.db import models

class Monitor(models.Model):
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    congestion_level = models.IntegerField()
    published_at = models.DateTimeField()

    def __str__(self):
        return f"{self.location.name} - {self.congestion_level.level} - {self.published_at}"

class Location(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

