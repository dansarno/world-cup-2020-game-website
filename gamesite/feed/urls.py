from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, PostDeleteView, PostUpdateView, landing
from . import views

app_name = "feed"
urlpatterns = [
    path("", landing, name="landing"),
    path("home", PostListView.as_view(), name="home"),
    path("post/<int:pk>/", PostDetailView.as_view(), name="detail"),
    path("post/new/", PostCreateView.as_view(), name="create"),
    path("post/<int:pk>/update/", PostUpdateView.as_view(), name="update"),
    path("post/<int:pk>/delete/", PostDeleteView.as_view(), name="delete"),
]
