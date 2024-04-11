from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from post.models import Post, Like
from post.serializers import PostSerializer

POST_URL = reverse("post:post-list")
ANALYTICS_LIKE_URL = reverse("post:analytics")


def detail_url(post_id: int):
    return reverse("post:post-detail", args=[post_id])


def sample_user():
    user = get_user_model().objects.create_user(
        email="testfortest@test.com", password="Test122345"
    )
    return user


def sample_post(**params):
    defaults = {"text": "Test"}
    defaults.update(params)
    return Post.objects.create(**defaults)


def sample_like(user, post):
    return Like.objects.create(owner=user, post=post)


class UnauthenticatedPostApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_read(self):
        res = self.client.get(POST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unauthenticated_creat(self):
        data = {"text": "Test Post", "owner": sample_user()}
        res = self.client.post(POST_URL, data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_update(self):
        sample_post(owner=sample_user())
        sample_post(
            owner=get_user_model().objects.create_user(
                email="testfortest1@test.com", password="Test122345"
            )
        )
        data = {"text": "Test Post"}
        res = self.client.put(detail_url(1), data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_delete(self):
        sample_post(owner=sample_user())
        res = self.client.put(detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPostApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@testfor.com", password="Test122345"
        )
        self.client.force_authenticate(self.user)

    def test_authenticated_creat(self):
        data = {"text": "Test Post"}
        res = self.client.post(POST_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_authenticated_like_post(self):
        post = sample_post(owner=sample_user())
        url = detail_url(post.id) + "like/"
        serializer = PostSerializer(post)
        res = self.client.get(url)
        res_detail = self.client.get(detail_url(post.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res_detail.data, serializer.data)

    def test_authenticated_unlike_post(self):
        post = sample_post(owner=sample_user())
        url = detail_url(post.id) + "like/"
        res = self.client.get(url)
        self.assertEqual(res.data["detail"], "You've liked it.")
        res2 = self.client.get(url)
        self.assertEqual(res2.data["detail"], "You have removed the like.")


class AnalyticsLikeViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@testfor.com", password="Test122345"
        )
        self.user2 = sample_user()
        self.client.force_authenticate(self.user)
        self.post = sample_post(owner=self.user)
        self.post2 = sample_post(owner=self.user2)

    def test_analytics_like_valid_dates(self):
        date_from = datetime.now().date()
        date_to = datetime.now().date() + timedelta(days=1)

        sample_like(self.user, self.post)
        sample_like(self.user, self.post2)
        sample_like(self.user2, self.post)
        url = ANALYTICS_LIKE_URL + f"?date_from={date_from}&date_to={date_to}"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_data = {
            f"{date_from}": 3,
        }
        self.assertEqual(res.data, expected_data)

    def test_analytics_like_invalid_dates(self):
        res = self.client.get(ANALYTICS_LIKE_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.get(ANALYTICS_LIKE_URL, {"date_from": "2024-04-01"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.get(ANALYTICS_LIKE_URL, {"date_to": "2024-04-01"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.get(
            ANALYTICS_LIKE_URL, {"date_from": "2024-04-01", "date_to": "2024-04-"}
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
