from django.contrib import admin

from .models import Comment, Genre, Movie, MovieList, MovieListItem, Review, UserMovie


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["title", "year", "director", "created_at"]
    list_filter = ["genres", "year"]
    search_fields = ["title", "original_title", "director"]
    filter_horizontal = ["genres"]
    readonly_fields = ["tmdb_id", "tmdb_votes"]


class ReviewCommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["movie", "user", "rating", "created_at"]
    list_filter = ["rating"]
    search_fields = ["movie__title", "user__username", "text"]
    inlines = [ReviewCommentInline]


@admin.register(UserMovie)
class UserMovieAdmin(admin.ModelAdmin):
    list_display = ["user", "movie", "is_favorite", "in_watchlist", "is_watched"]
    list_filter = ["is_favorite", "in_watchlist", "is_watched"]


class MovieListItemInline(admin.TabularInline):
    model = MovieListItem
    extra = 0


@admin.register(MovieList)
class MovieListAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "is_public", "updated_at"]
    list_filter = ["is_public"]
    inlines = [MovieListItemInline]
