from rest_framework import serializers

from post.models import Post, Like


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "post", "created_at")


class LikeDetailSerializer(LikeSerializer):
    like = serializers.ReadOnlyField(source="owner.email")

    class Meta:
        model = Like
        fields = ("id", "post", "like", "created_at")


class PostSerializer(serializers.ModelSerializer):
    likes = LikeDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ("id", "text", "likes", "created_at")


class PostListSerializer(PostSerializer):
    owner = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")
    likes = serializers.IntegerField(source="likes.count")

    class Meta:
        model = Post
        fields = ("id", "owner", "text", "likes", "created_at")
