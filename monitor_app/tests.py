from django.test import TestCase, Client
from django.urls import reverse
from .models import Location, Collected, CongestionLevel
from .views import weighted_average_congestion
from django.utils import timezone
from datetime import timedelta

class MakeRandomDataTest(TestCase):
    def setUp(self):
        Location.objects.create(program_name="Test Program", room_name="Test Room", floor=1)

    def test_make_random_data_creates_10_records(self):
        url = reverse('make_random_data')
        before_count = Collected.objects.count()
        self.client.get(url)
        after_count = Collected.objects.count()
        self.assertEqual(after_count - before_count, 10)

class WeightedAverageCongestionTest(TestCase):
    def setUp(self):
        self.loc = Location.objects.create(program_name="Test", room_name="A", floor=1)
        self.valid_time = 30
        now = timezone.now()
        # 新しいデータ
        Collected.objects.create(location=self.loc, congestion_level=80, published_at=now)
        # 古いデータ
        Collected.objects.create(location=self.loc, congestion_level=20, published_at=now - timedelta(minutes=29))

    def test_weighted_average_gives_more_weight_to_newer(self):
        qs = Collected.objects.filter(location=self.loc)
        avg = weighted_average_congestion(qs, self.valid_time)
        self.assertTrue(avg > 50 and avg < 80)

    def test_weighted_average_all_same(self):
        Collected.objects.all().delete()
        for _ in range(5):
            Collected.objects.create(location=self.loc, congestion_level=42, published_at=timezone.now())
        qs = Collected.objects.filter(location=self.loc)
        avg = weighted_average_congestion(qs, self.valid_time)
        self.assertEqual(avg, 42)

    def test_weighted_average_none(self):
        Collected.objects.all().delete()
        qs = Collected.objects.filter(location=self.loc)
        avg = weighted_average_congestion(qs, self.valid_time)
        self.assertIsNone(avg)

class AggregatesDataTest(TestCase):
    def setUp(self):
        self.loc = Location.objects.create(program_name="Test", room_name="B", floor=2)
        self.client = Client()
        self.valid_time = 30
        Collected.objects.create(location=self.loc, congestion_level=60, published_at=timezone.now())

    def test_aggregates_data_creates_congestionlevel(self):
        url = reverse('aggregates_data')
        self.client.get(url)
        self.assertTrue(CongestionLevel.objects.filter(location=self.loc).exists())

    def test_aggregates_data_overwrites(self):
        CongestionLevel.objects.create(location=self.loc, level=10)
        url = reverse('aggregates_data')
        self.client.get(url)
        cl = CongestionLevel.objects.get(location=self.loc)
        self.assertNotEqual(cl.level, 10)

class DisplayViewsTest(TestCase):
    def setUp(self):
        self.loc = Location.objects.create(program_name="Test", room_name="C", floor=3)
        CongestionLevel.objects.create(location=self.loc, level=55, reliability=1.0)
        self.client = Client()

    def test_display_returns_200(self):
        url = reverse('display', args=[3])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_display_json_returns_data(self):
        url = reverse('display_json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.json())

class EdgeCaseTest(TestCase):
    def test_no_location_no_error(self):
        client = Client()
        url = reverse('aggregates_data')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_no_collected_no_error(self):
        loc = Location.objects.create(program_name="Test", room_name="D", floor=4)
        client = Client()
        url = reverse('aggregates_data')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
