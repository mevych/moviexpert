import time

from django.core.management.base import BaseCommand

from main import services
from main.models import Movie


class Command(BaseCommand):
    help = "Обновляет оценки и число голосов TMDB у всех фильмов, импортированных из TMDB"

    def handle(self, *args, **options):
        updated = failed = 0
        movies = Movie.objects.filter(tmdb_id__isnull=False)
        total = movies.count()
        for movie in movies:
            try:
                data = services._tmdb(f"/movie/{movie.tmdb_id}")
            except services.ServiceError as exc:
                failed += 1
                self.stderr.write(f"  ! {movie}: {exc}")
                continue
            movie.tmdb_votes = data.get("vote_count") or 0
            movie.tmdb_rating = round(data.get("vote_average") or 0, 1)
            movie.save(update_fields=["tmdb_votes", "tmdb_rating"])
            updated += 1
            time.sleep(0.05)
        self.stdout.write(self.style.SUCCESS(f"Обновлено: {updated} из {total}, ошибок: {failed}"))
