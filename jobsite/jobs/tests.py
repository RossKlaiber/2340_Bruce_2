from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse

from jobs.models import Job
from jobs.utils import filter_jobs_by_distance, calculate_distance
from accounts.models import UserProfile, JobSeekerProfile
from jobs.views import job_list


class CommuteRadiusTests(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		# Create a job seeker user and related profiles
		self.user = User.objects.create_user(
			username="seeker", email="seeker@example.com", password="pass1234"
		)
		self.user_profile = UserProfile.objects.create(user=self.user, user_type='job_seeker')
		self.job_seeker_profile = JobSeekerProfile.objects.create(
			user_profile=self.user_profile,
			commute_radius=10  # miles
		)

		# Another user to be the job poster
		self.poster = User.objects.create_user(
			username="poster", email="poster@example.com", password="pass1234"
		)

		# Coordinates
		# User location: San Francisco
		self.user_lat = 37.7749
		self.user_lon = -122.4194

		# Close job: Oakland (~8-9 miles from SF)
		self.job_close = Job.objects.create(
			title="Backend Engineer",
			company="CloseCo",
			location="Oakland, CA",
			latitude=37.8044,
			longitude=-122.2711,
			job_type='full-time',
			experience_level='mid',
			work_type='onsite',
			skills="Python, Django",
			description="Work on APIs",
			requirements="3+ years Python",
			benefits="",
			posted_by=self.poster,
			is_active=True,
		)

		# Far job: San Jose (~40+ miles from SF)
		self.job_far = Job.objects.create(
			title="Frontend Engineer",
			company="FarCo",
			location="San Jose, CA",
			latitude=37.3382,
			longitude=-121.8863,
			job_type='full-time',
			experience_level='mid',
			work_type='onsite',
			skills="React, JS",
			description="Work on UI",
			requirements="3+ years React",
			benefits="",
			posted_by=self.poster,
			is_active=True,
		)

	def test_calculate_distance_basic(self):
		# San Francisco to Oakland should be under ~15 miles (driving is longer; straight-line is less)
		d = calculate_distance(self.user_lat, self.user_lon, 37.8044, -122.2711)
		self.assertGreater(d, 5)
		self.assertLess(d, 15)

	def test_filter_jobs_by_distance_utils(self):
		jobs_qs = Job.objects.filter(is_active=True)
		filtered = filter_jobs_by_distance(jobs_qs, self.user_lat, self.user_lon, 10)
		filtered_ids = {j.id for j in filtered}
		self.assertIn(self.job_close.id, filtered_ids)
		self.assertNotIn(self.job_far.id, filtered_ids)

	def test_job_list_auto_applies_commute_radius(self):
		# Log in the job seeker
		self.client.login(username="seeker", password="pass1234")
		url = reverse('jobs.list')
		response = self.client.get(url, {
			'user_latitude': str(self.user_lat),
			'user_longitude': str(self.user_lon),
		})
		self.assertEqual(response.status_code, 200)
		template_data = response.context['template_data']
		page_obj = template_data['page_obj']
		job_titles = {job.title for job in page_obj}
		# Only the close job should be present with a 10-mile preference
		self.assertIn('Backend Engineer', job_titles)
		self.assertNotIn('Frontend Engineer', job_titles)

