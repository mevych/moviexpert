import time

from django.core.management.base import BaseCommand, CommandError

from main import services


class Command(BaseCommand):
    help = "Массово импортирует фильмы из TMDB (популярные или лучшие по рейтингу)"

    def add_arguments(self, parser):
        parser.add_argument("--source", choices=["popular", "top_rated"], default="top_rated",
                            help="Откуда брать фильмы (по умолчанию top_rated)")
        parser.add_argument("--pages", type=int, default=5,
                            help="Сколько страниц брать, на странице 20 фильмов (по умолчанию 5 = 100 фильмов)")
        parser.add_argument("--start-page", type=int, default=1, help="С какой страницы начать")

    def handle(self, *args, **options):
        created = skipped = failed = 0
        first = options["start_page"]
        last = first + options["pages"] - 1

        for page in range(first, last + 1):
            try:
                data = services._tmdb(f"/movie/{options['source']}", page=page)
            except services.ServiceError as exc:
                raise CommandError(f"Страница {page}: {exc}")

            for item in data.get("results", []):
                try:
                    movie, was_created = services.import_from_tmdb(item["id"])
                except services.ServiceError as exc:
                    failed += 1
                    self.stderr.write(f"  ! {item.get('title')}: {exc}")
                    continue
                votes = item.get("vote_count") or 0
                rating = round(item.get("vote_average") or 0, 1)
                if movie.tmdb_votes != votes or movie.tmdb_rating != rating:
                    movie.tmdb_votes = votes
                    movie.tmdb_rating = rating
                    movie.save(update_fields=["tmdb_votes", "tmdb_rating"])
                if was_created:
                    created += 1
                    self.stdout.write(f"  + {movie}")
                else:
                    skipped += 1
                time.sleep(0.05)

            self.stdout.write(f"Страница {page}/{last} готова")

        self.stdout.write(self.style.SUCCESS(
            f"Добавлено: {created}, уже были: {skipped}, ошибок: {failed}"))
