from django.shortcuts import render
from rest_framework import viewsets

from post.models import Post
from post.serializers import PostSerializer


# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
