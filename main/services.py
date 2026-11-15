import json
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG = "https://image.tmdb.org/t/p"


class ServiceError(Exception):
    pass


def _get_json(url, headers=None):
    request = urllib.request.Request(url, headers=headers or {"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise ServiceError("Сервис отклонил ключ API. Проверьте ключ.") from exc
        if exc.code == 404:
            raise ServiceError("Ничего не найдено.") from exc
        raise ServiceError(f"Сервис ответил ошибкой {exc.code}.") from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise ServiceError("Не удалось связаться с внешним сервисом. Попробуйте позже.") from exc


def _tmdb(path, **params):
    key = settings.TMDB_API_KEY
    if not key:
        raise ServiceError("Не задан TMDB_API_KEY: импорт из TMDB отключён.")
    headers = {"Accept": "application/json"}
    params.setdefault("language", "ru-RU")
    if key.startswith("eyJ"):
        headers["Authorization"] = f"Bearer {key}"
    else:
        params["api_key"] = key
    return _get_json(f"{TMDB_BASE}{path}?{urllib.parse.urlencode(params)}", headers)


def _poster(path, size):
    return f"{TMDB_IMG}/{size}{path}" if path else ""


def tmdb_search(query):
    data = _tmdb("/search/movie", query=query, include_adult="false")
    return [
        {
            "tmdb_id": item["id"],
            "title": item.get("title") or item.get("original_title") or "",
            "original_title": item.get("original_title") or "",
            "year": (item.get("release_date") or "")[:4],
            "overview": item.get("overview") or "",
            "poster_url": _poster(item.get("poster_path"), "w185"),
        }
        for item in data.get("results", [])[:12]
    ]


def import_from_tmdb(tmdb_id, user=None):
    from .models import Genre, Movie

    existing = Movie.objects.filter(tmdb_id=tmdb_id).first()
    if existing:
        return existing, False

    data = _tmdb(f"/movie/{tmdb_id}", append_to_response="credits")
    year_str = (data.get("release_date") or "")[:4]
    if not year_str.isdigit():
        raise ServiceError("У этого фильма не указан год выхода, импортировать его нельзя.")
    year = int(year_str)

    title = data.get("title") or data.get("original_title") or "Без названия"
    original = data.get("original_title") or ""
    director = next(
        (c.get("name", "") for c in (data.get("credits") or {}).get("crew", [])
         if c.get("job") == "Director"),
        "",
    )
    poster = _poster(data.get("poster_path"), "w500")

    overview = data.get("overview") or ""
    if not overview:
        try:
            overview = _tmdb(f"/movie/{tmdb_id}", language="en-US").get("overview") or ""
        except ServiceError:
            overview = ""

    movie = Movie.objects.filter(title=title, year=year, tmdb_id__isnull=True).first()
    created = movie is None
    if created:
        movie = Movie(title=title, year=year, added_by=user)
    movie.tmdb_id = tmdb_id
    movie.tmdb_votes = data.get("vote_count") or 0
    movie.tmdb_rating = round(data.get("vote_average") or 0, 1)
    movie.original_title = movie.original_title or (original if original != title else "")
    movie.director = movie.director or director
    movie.duration = movie.duration or data.get("runtime") or None
    movie.description = movie.description or overview
    if not movie.poster and not movie.poster_url:
        movie.poster_url = poster
    movie.save()

    for g in data.get("genres", []):
        name = (g.get("name") or "").strip()
        if name:
            genre, _ = Genre.objects.get_or_create(name=name[:1].upper() + name[1:])
            movie.genres.add(genre)

    return movie, created
