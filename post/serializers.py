from rest_framework import serializers

from post.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "text", "created_at")


class PostListSerializer(PostSerializer):
    owner = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")

    class Meta:
        model = Post
        fields = ("id", "owner", "text", "created_at")
