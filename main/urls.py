from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("movies/", views.movie_list, name="movie_list"),
    path("movies/add/", views.movie_create, name="movie_create"),
    path("movies/<int:pk>/", views.movie_detail, name="movie_detail"),
    path("movies/<int:pk>/review/", views.review_save, name="review_save"),

    path("reviews/<int:pk>/delete/", views.review_delete, name="review_delete"),

    path("accounts/register/", views.register, name="register"),
]
