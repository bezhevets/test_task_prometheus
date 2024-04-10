from django.urls import path, include
from rest_framework import routers

from post.views import PostViewSet, AnalyticsLikeView

router = routers.DefaultRouter()
router.register("posts", PostViewSet)


urlpatterns = [
    path("analytics/", AnalyticsLikeView.as_view(), name="analytics"),
    path("", include(router.urls)),
]

app_name = "post"
