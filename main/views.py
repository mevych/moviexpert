from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MovieForm, RegisterForm, ReviewForm
from .models import Genre, Movie, Review, UserMovie

SORT_FIELDS = {
    "new": "created_at",
    "year": "year",
    "rating": "avg_rating",
    "title": "title",
}

DEFAULT_DIRECTION = {
    "new": "desc",
    "year": "desc",
    "rating": "desc",
    "title": "asc",
}


def rated(queryset):
    return queryset.annotate(avg_rating=Avg("reviews__rating"), reviews_count=Count("reviews"))


def catalog():
    return rated(Movie.objects.prefetch_related("genres"))


def sort_order(sort, direction):
    field = SORT_FIELDS[sort]
    descending = direction == "desc"
    if sort == "rating":
        primary = F(field).desc(nulls_last=True) if descending else F(field).asc(nulls_last=True)
    else:
        primary = f"-{field}" if descending else field
    if sort in ("new", "title"):
        return (primary,)
    return (primary, "title")


def reviews_qs():
    return Review.objects.select_related("user", "movie").annotate(
        likes_count=Count("likes", distinct=True),
        comments_count=Count("comments", distinct=True),
    )


def mark_watched(user, movie):
    state, _ = UserMovie.objects.get_or_create(user=user, movie=movie)
    if not state.is_watched:
        state.is_watched = True
        state.in_watchlist = False
        state.save()


def home(request):
    movies = catalog()
    return render(request, "main/home.html", {
        "top": movies.filter(reviews_count__gt=0).order_by(
            F("avg_rating").desc(nulls_last=True), "-reviews_count")[:6],
        "latest": movies.order_by("-created_at")[:6],
        "movies_total": Movie.objects.count(),
    })


def movie_list(request):
    qs = catalog()
    q = request.GET.get("q", "").strip()
    genre_id = request.GET.get("genre", "")
    sort = request.GET.get("sort", "new")
    if sort not in SORT_FIELDS:
        sort = "new"
    direction = request.GET.get("dir", "")
    if direction not in ("asc", "desc"):
        direction = DEFAULT_DIRECTION[sort]

    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(original_title__icontains=q) | Q(director__icontains=q)
        )
    if genre_id.isdigit():
        qs = qs.filter(genres__id=int(genre_id))

    qs = qs.order_by(*sort_order(sort, direction))
    page = Paginator(qs, 12).get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)

    return render(request, "main/movie_list.html", {
        "page": page,
        "genres": Genre.objects.all(),
        "q": q,
        "genre_id": genre_id,
        "sort": sort,
        "direction": direction,
        "querystring": params.urlencode(),
    })


def _detail_context(request, movie, form=None):
    my_review = None
    if request.user.is_authenticated:
        my_review = Review.objects.filter(user=request.user, movie=movie).first()
    if form is None:
        form = ReviewForm(instance=my_review)
    reviews = list(reviews_qs().filter(movie=movie))
    return {
        "movie": movie,
        "my_review": my_review,
        "form": form,
        "reviews": reviews,
    }


def movie_detail(request, pk):
    movie = get_object_or_404(catalog(), pk=pk)
    return render(request, "main/movie_detail.html", _detail_context(request, movie))


@login_required
def movie_create(request):
    form = MovieForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        movie = form.save(commit=False)
        movie.added_by = request.user
        movie.save()
        form.save_m2m()
        messages.success(request, "Фильм добавлен в каталог.")
        return redirect(movie)
    return render(request, "main/movie_form.html", {"form": form})


@login_required
@require_POST
def review_save(request, pk):
    movie = get_object_or_404(catalog(), pk=pk)
    review = Review.objects.filter(user=request.user, movie=movie).first()
    form = ReviewForm(request.POST, instance=review)
    if not form.is_valid():
        return render(request, "main/movie_detail.html", _detail_context(request, movie, form))
    obj = form.save(commit=False)
    obj.user = request.user
    obj.movie = movie
    obj.save()
    mark_watched(request.user, movie)
    messages.success(request, "Обзор сохранён.")
    return redirect(movie)


@login_required
@require_POST
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    movie = review.movie
    review.delete()
    messages.success(request, "Обзор удалён.")
    return redirect(movie)


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Аккаунт создан. Добро пожаловать!")
        return redirect("home")
    return render(request, "registration/register.html", {"form": form})
