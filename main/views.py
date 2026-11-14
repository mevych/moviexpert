from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Q
from django.shortcuts import get_object_or_404, render

from .models import Genre, Movie

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


def movie_detail(request, pk):
    movie = get_object_or_404(catalog(), pk=pk)
    return render(request, "main/movie_detail.html", {"movie": movie})
