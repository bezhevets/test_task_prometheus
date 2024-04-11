from datetime import datetime

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from post.models import Post, Like
from post.permissions import IsOwnerOrIfAuthenticatedReadOnly
from post.serializers import PostSerializer, PostListSerializer, LikeSerializer


class PostViewSet(viewsets.ModelViewSet):
    """API endpoint for managing post.

    list:
    Retrieve a list of posts.

    retrieve:
    Retrieve details of a specific post.

    create:
    Create a new post.

    update:
    Only post owners can update.

    delete:
    Only post owners can delete.
    """

    queryset = Post.objects.all().select_related("owner").prefetch_related("likes")
    serializer_class = PostSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsOwnerOrIfAuthenticatedReadOnly,
    )

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "like":
            return LikeSerializer
        return PostSerializer

    def create(self, request, *args, **kwargs):
        """Creating a new post, only by registered and authenticated users."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["GET"],
        url_path="like",
        permission_classes=[IsAuthenticated],
    )
    def create_like(self, request, pk=None):
        """Like or unlike a post."""

        post = self.get_object()
        user = self.request.user

        likes = Like.objects.filter(owner=user, post=post)
        if likes:
            likes.delete()
            return Response(
                {"detail": "You have removed the like."},
                status=status.HTTP_200_OK,
            )
        else:
            serializer = LikeSerializer(data={"post": post.pk})
            serializer.is_valid(raise_exception=True)
            serializer.save(owner=user, post=post)
            return Response(
                {"detail": "You've liked it."},
                status=status.HTTP_200_OK,
            )


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="date_from",
            required=True,
            description="Start date for analytics (YYYY-MM-DD)",
            type=str,
        ),
        OpenApiParameter(
            name="date_to",
            required=True,
            description="End date for analytics (YYYY-MM-DD)",
            type=str,
        ),
    ],
    responses={200: OpenApiResponse(description="Analytics data")},
)
class AnalyticsLikeView(APIView):
    """Analytics by the number of likes by date"""

    def get(self, request):
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if date_to is None or date_from is None:
            return Response(
                {
                    "detail": (
                        "date_from and date_to are required parameters. "
                        "Ex: /?date_from=2024-04-01&date_to=2024-04-11"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date_from = datetime.strptime(date_from, "%Y-%m-%d").replace(
                hour=0, minute=0, second=0
            )
            date_to = datetime.strptime(date_to, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59
            )
        except ValueError:
            return Response(
                {
                    "error": "Incorrect format date. Ex: /?date_from=2024-04-01&date_to=2024-04-11"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        likes_data = Like.objects.filter(created_at__range=[date_from, date_to])
        likes_aggregated = {}

        for like in likes_data:
            date = like.created_at.date()
            date = str(date)
            if date in likes_aggregated:
                likes_aggregated[date] += 1
            else:
                likes_aggregated[date] = 1

        return Response(likes_aggregated, status=status.HTTP_200_OK)
