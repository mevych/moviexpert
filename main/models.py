from django.conf import settings
from django.db import models
from django.urls import reverse


class Genre(models.Model):
    name = models.CharField("Название", max_length=60, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "жанр"
        verbose_name_plural = "жанры"

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField("Название", max_length=200)
    original_title = models.CharField("Оригинальное название", max_length=200, blank=True)
    year = models.PositiveSmallIntegerField("Год")
    director = models.CharField("Режиссёр", max_length=150, blank=True)
    duration = models.PositiveSmallIntegerField("Длительность, мин", null=True, blank=True)
    description = models.TextField("Описание", blank=True)
    poster = models.ImageField("Постер (файл)", upload_to="posters/", blank=True)
    poster_url = models.URLField("Или ссылка на постер", blank=True)
    genres = models.ManyToManyField(Genre, verbose_name="Жанры", related_name="movies", blank=True)

    tmdb_id = models.PositiveIntegerField(null=True, blank=True, unique=True, editable=False)
    tmdb_votes = models.PositiveIntegerField("Голосов на TMDB", default=0, editable=False)

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="added_movies",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "фильм"
        verbose_name_plural = "фильмы"

    def __str__(self):
        return f"{self.title} ({self.year})"

    def get_absolute_url(self):
        return reverse("movie_detail", args=[self.pk])

    @property
    def poster_src(self):
        if self.poster:
            return self.poster.url
        return self.poster_url

    @property
    def hue(self):
        return ((self.pk or 0) * 47) % 360


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField("Оценка (1–10)")
    text = models.TextField("Обзор", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "movie"], name="one_review_per_user_movie"),
        ]
        verbose_name = "обзор"
        verbose_name_plural = "обзоры"

    def __str__(self):
        return f"{self.user} → {self.movie}: {self.rating}"

    def get_absolute_url(self):
        return reverse("review_detail", args=[self.pk])


class ReviewLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_likes")
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "review"], name="one_like_per_user_review"),
        ]
        verbose_name = "лайк обзора"
        verbose_name_plural = "лайки обзоров"


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField("Комментарий", max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"

    def __str__(self):
        return f"{self.user}: {self.text[:30]}"


class UserMovie(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="movie_states")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="user_states")
    is_favorite = models.BooleanField(default=False)
    in_watchlist = models.BooleanField(default=False)
    is_watched = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "movie"], name="one_state_per_user_movie"),
        ]
        verbose_name = "отметка пользователя"
        verbose_name_plural = "отметки пользователей"

    def __str__(self):
        return f"{self.user} — {self.movie}"


class MovieList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lists")
    title = models.CharField("Название", max_length=120)
    description = models.TextField("Описание", blank=True, max_length=1000)
    is_public = models.BooleanField("Видна всем", default=True)
    movies = models.ManyToManyField(Movie, through="MovieListItem", related_name="in_lists")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "список"
        verbose_name_plural = "списки"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("list_detail", args=[self.pk])


class MovieListItem(models.Model):
    movie_list = models.ForeignKey(MovieList, on_delete=models.CASCADE, related_name="items")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="list_items")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["added_at"]
        constraints = [
            models.UniqueConstraint(fields=["movie_list", "movie"], name="movie_once_per_list"),
        ]
