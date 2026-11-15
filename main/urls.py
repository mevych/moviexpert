from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("movies/", views.movie_list, name="movie_list"),
    path("movies/add/", views.movie_create, name="movie_create"),
    path("movies/<int:pk>/", views.movie_detail, name="movie_detail"),
    path("movies/<int:pk>/review/", views.review_save, name="review_save"),

    path("reviews/<int:pk>/", views.review_detail, name="review_detail"),
    path("reviews/<int:pk>/delete/", views.review_delete, name="review_delete"),
    path("reviews/<int:pk>/like/", views.review_like, name="review_like"),
    path("reviews/<int:pk>/comment/", views.comment_create, name="comment_create"),
    path("comments/<int:pk>/delete/", views.comment_delete, name="comment_delete"),

    path("accounts/register/", views.register, name="register"),
]
