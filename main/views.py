from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import (
    CommentForm, MovieForm, MovieListForm, RegisterForm, ReviewForm,
)
from .models import (
    Comment, Genre, Movie, MovieList, MovieListItem, Review, ReviewLike,
    UserMovie,
)

User = get_user_model()

STATE_FIELDS = {
    "favorite": "is_favorite",
    "watchlist": "in_watchlist",
    "watched": "is_watched",
}

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

PROFILE_TABS = {
    "favorites": ("Избранное", "is_favorite"),
    "watchlist": ("Смотреть позже", "in_watchlist"),
    "watched": ("Просмотрено", "is_watched"),
    "reviews": ("Обзоры", None),
    "lists": ("Списки", None),
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


def liked_ids(user, reviews):
    if not user.is_authenticated:
        return set()
    ids = [r.pk for r in reviews]
    return set(ReviewLike.objects.filter(user=user, review_id__in=ids).values_list("review_id", flat=True))


def safe_next(request, default):
    target = request.POST.get("next", "")
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        return target
    return default


def mark_watched(user, movie):
    state, _ = UserMovie.objects.get_or_create(user=user, movie=movie)
    if not state.is_watched:
        state.is_watched = True
        state.in_watchlist = False
        state.save()


def home(request):
    movies = catalog()
    recent_reviews = list(reviews_qs().exclude(text="")[:6])
    return render(request, "main/home.html", {
        "top": movies.filter(reviews_count__gt=0).order_by(
            F("avg_rating").desc(nulls_last=True), "-reviews_count")[:6],
        "latest": movies.order_by("-created_at")[:6],
        "recent_reviews": recent_reviews,
        "liked": liked_ids(request.user, recent_reviews),
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
    state = my_review = None
    addable_lists = []
    if request.user.is_authenticated:
        state = UserMovie.objects.filter(user=request.user, movie=movie).first()
        my_review = Review.objects.filter(user=request.user, movie=movie).first()
        addable_lists = request.user.lists.exclude(items__movie=movie)
    if form is None:
        form = ReviewForm(instance=my_review)
    reviews = list(reviews_qs().filter(movie=movie))
    return {
        "movie": movie,
        "state": state,
        "my_review": my_review,
        "form": form,
        "reviews": reviews,
        "liked": liked_ids(request.user, reviews),
        "addable_lists": addable_lists,
        "public_lists": movie.in_lists.filter(is_public=True).select_related("user")[:6],
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
def toggle_state(request, pk, action):
    field = STATE_FIELDS.get(action)
    if field is None:
        raise Http404
    movie = get_object_or_404(Movie, pk=pk)
    state, _ = UserMovie.objects.get_or_create(user=request.user, movie=movie)
    new_value = not getattr(state, field)
    setattr(state, field, new_value)
    if field == "is_watched" and new_value:
        state.in_watchlist = False
    state.save()
    return redirect(safe_next(request, movie.get_absolute_url()))


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


def review_detail(request, pk, comment_form=None):
    review = get_object_or_404(reviews_qs(), pk=pk)
    return render(request, "main/review_detail.html", {
        "review": review,
        "comments": review.comments.select_related("user"),
        "comment_form": comment_form or CommentForm(),
        "liked": liked_ids(request.user, [review]),
    })


@login_required
@require_POST
def review_like(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user_id == request.user.pk:
        messages.error(request, "Нельзя лайкать собственный обзор.")
    else:
        like, created = ReviewLike.objects.get_or_create(user=request.user, review=review)
        if not created:
            like.delete()
    return redirect(safe_next(request, review.get_absolute_url()))


@login_required
@require_POST
def comment_create(request, pk):
    review = get_object_or_404(Review, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.review = review
        comment.user = request.user
        comment.save()
        messages.success(request, "Комментарий опубликован.")
    else:
        return review_detail(request, pk, comment_form=form)
    return redirect(review)


@login_required
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user_id != request.user.pk and not request.user.is_staff:
        raise PermissionDenied
    review = comment.review
    comment.delete()
    messages.success(request, "Комментарий удалён.")
    return redirect(review)


def list_index(request):
    lists = (MovieList.objects.filter(is_public=True)
             .select_related("user").annotate(items_count=Count("items")))
    page = Paginator(lists, 20).get_page(request.GET.get("page"))
    return render(request, "main/list_index.html", {"page": page, "querystring": ""})


def list_detail(request, pk):
    movie_list = get_object_or_404(MovieList.objects.select_related("user"), pk=pk)
    is_owner = request.user.is_authenticated and movie_list.user_id == request.user.pk
    if not movie_list.is_public and not is_owner:
        raise Http404
    ids = list(movie_list.items.values_list("movie_id", flat=True))
    by_id = {m.pk: m for m in catalog().filter(pk__in=ids)}
    return render(request, "main/list_detail.html", {
        "movie_list": movie_list,
        "is_owner": is_owner,
        "movies": [by_id[i] for i in ids if i in by_id],
    })


@login_required
def list_create(request):
    form = MovieListForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        movie_list = form.save(commit=False)
        movie_list.user = request.user
        movie_list.save()
        messages.success(request, "Список создан.")
        return redirect(movie_list)
    return render(request, "main/list_form.html", {"form": form, "heading": "Новый список"})


@login_required
def list_edit(request, pk):
    movie_list = get_object_or_404(MovieList, pk=pk, user=request.user)
    form = MovieListForm(request.POST or None, instance=movie_list)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Изменения сохранены.")
        return redirect(movie_list)
    return render(request, "main/list_form.html", {"form": form, "heading": "Изменить список"})


@login_required
@require_POST
def list_delete(request, pk):
    movie_list = get_object_or_404(MovieList, pk=pk, user=request.user)
    movie_list.delete()
    messages.success(request, "Список удалён.")
    return redirect("profile", username=request.user.username)


@login_required
@require_POST
def list_add_movie(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    list_id = request.POST.get("list_id", "")
    if not list_id.isdigit():
        messages.error(request, "Выберите список.")
        return redirect(movie)
    movie_list = get_object_or_404(MovieList, pk=int(list_id), user=request.user)
    _, created = MovieListItem.objects.get_or_create(movie_list=movie_list, movie=movie)
    if created:
        movie_list.save()
        messages.success(request, f"Фильм добавлен в список «{movie_list.title}».")
    else:
        messages.error(request, "Фильм уже есть в этом списке.")
    return redirect(movie)


@login_required
@require_POST
def list_remove_movie(request, pk, movie_pk):
    movie_list = get_object_or_404(MovieList, pk=pk, user=request.user)
    MovieListItem.objects.filter(movie_list=movie_list, movie_id=movie_pk).delete()
    messages.success(request, "Фильм убран из списка.")
    return redirect(movie_list)


def profile(request, username):
    owner = get_object_or_404(User, username=username)
    is_self = request.user.is_authenticated and request.user.pk == owner.pk
    tab = request.GET.get("tab", "favorites")
    if tab not in PROFILE_TABS:
        tab = "favorites"

    owner_lists = MovieList.objects.filter(user=owner)
    if not is_self:
        owner_lists = owner_lists.filter(is_public=True)

    counts = {}
    for key, (_, field) in PROFILE_TABS.items():
        if field:
            counts[key] = UserMovie.objects.filter(user=owner, **{field: True}).count()
        elif key == "reviews":
            counts[key] = Review.objects.filter(user=owner).count()
        else:
            counts[key] = owner_lists.count()

    movies = reviews = lists = None
    liked = set()
    field = PROFILE_TABS[tab][1]
    if field:
        ids = list(
            UserMovie.objects.filter(user=owner, **{field: True})
            .order_by("-updated_at").values_list("movie_id", flat=True)
        )
        by_id = {m.pk: m for m in catalog().filter(pk__in=ids)}
        movies = [by_id[i] for i in ids if i in by_id]
    elif tab == "reviews":
        reviews = list(reviews_qs().filter(user=owner))
        liked = liked_ids(request.user, reviews)
    else:
        lists = owner_lists.annotate(items_count=Count("items"))

    return render(request, "main/profile.html", {
        "owner": owner,
        "is_self": is_self,
        "tab": tab,
        "tabs": [(key, label, counts[key]) for key, (label, _) in PROFILE_TABS.items()],
        "movies": movies,
        "reviews": reviews,
        "lists": lists,
        "liked": liked,
    })


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
