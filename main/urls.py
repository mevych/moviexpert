from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("movies/", views.movie_list, name="movie_list"),
    path("case/", views.case_page, name="case"),
    path("movies/add/", views.movie_create, name="movie_create"),
    path("movies/import/", views.tmdb_search, name="tmdb_search"),
    path("movies/import/run/", views.tmdb_import, name="tmdb_import"),
    path("movies/<int:pk>/", views.movie_detail, name="movie_detail"),
    path("movies/<int:pk>/mark/<str:action>/", views.toggle_state, name="toggle_state"),
    path("movies/<int:pk>/review/", views.review_save, name="review_save"),
    path("movies/<int:pk>/add-to-list/", views.list_add_movie, name="list_add_movie"),

    path("reviews/<int:pk>/", views.review_detail, name="review_detail"),
    path("reviews/<int:pk>/delete/", views.review_delete, name="review_delete"),
    path("reviews/<int:pk>/like/", views.review_like, name="review_like"),
    path("reviews/<int:pk>/comment/", views.comment_create, name="comment_create"),
    path("comments/<int:pk>/delete/", views.comment_delete, name="comment_delete"),

    path("lists/", views.list_index, name="list_index"),
    path("lists/new/", views.list_create, name="list_create"),
    path("lists/<int:pk>/", views.list_detail, name="list_detail"),
    path("lists/<int:pk>/edit/", views.list_edit, name="list_edit"),
    path("lists/<int:pk>/delete/", views.list_delete, name="list_delete"),
    path("lists/<int:pk>/remove/<int:movie_pk>/", views.list_remove_movie, name="list_remove_movie"),

    path("team/", views.team, name="team"),
    path("support/", views.support, name="support"),
    path("support/thanks/", views.support_thanks, name="support_thanks"),

    path("u/<str:username>/", views.profile, name="profile"),
    path("accounts/register/", views.register, name="register"),
]
