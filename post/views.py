from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

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
    """

    queryset = Post.objects.all()
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
