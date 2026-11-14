import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'жанр',
                'verbose_name_plural': 'жанры',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('original_title', models.CharField(blank=True, max_length=200, verbose_name='Оригинальное название')),
                ('year', models.PositiveSmallIntegerField(verbose_name='Год')),
                ('director', models.CharField(blank=True, max_length=150, verbose_name='Режиссёр')),
                ('duration', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Длительность, мин')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('poster', models.ImageField(blank=True, upload_to='posters/', verbose_name='Постер (файл)')),
                ('poster_url', models.URLField(blank=True, verbose_name='Или ссылка на постер')),
                ('tmdb_id', models.PositiveIntegerField(blank=True, editable=False, null=True, unique=True)),
                ('imdb_id', models.CharField(blank=True, help_text='Например, tt0111161', max_length=15, verbose_name='IMDb ID')),
                ('imdb_rating', models.DecimalField(blank=True, decimal_places=1, editable=False, max_digits=3, null=True)),
                ('imdb_votes', models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ('imdb_updated', models.DateTimeField(blank=True, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='added_movies', to=settings.AUTH_USER_MODEL)),
                ('genres', models.ManyToManyField(blank=True, related_name='movies', to='main.genre', verbose_name='Жанры')),
            ],
            options={
                'verbose_name': 'фильм',
                'verbose_name_plural': 'фильмы',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MovieList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='Название')),
                ('description', models.TextField(blank=True, max_length=1000, verbose_name='Описание')),
                ('is_public', models.BooleanField(default=True, verbose_name='Видна всем')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lists', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'список',
                'verbose_name_plural': 'списки',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='MovieListItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='list_items', to='main.movie')),
                ('movie_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='main.movielist')),
            ],
            options={
                'ordering': ['added_at'],
            },
        ),
        migrations.AddField(
            model_name='movielist',
            name='movies',
            field=models.ManyToManyField(related_name='in_lists', through='main.MovieListItem', to='main.movie'),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(verbose_name='Оценка (1–10)')),
                ('text', models.TextField(blank=True, verbose_name='Обзор')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='main.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'обзор',
                'verbose_name_plural': 'обзоры',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=2000, verbose_name='Комментарий')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='main.review')),
            ],
            options={
                'verbose_name': 'комментарий',
                'verbose_name_plural': 'комментарии',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='ReviewLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='main.review')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'лайк обзора',
                'verbose_name_plural': 'лайки обзоров',
            },
        ),
        migrations.CreateModel(
            name='UserMovie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_favorite', models.BooleanField(default=False)),
                ('in_watchlist', models.BooleanField(default=False)),
                ('is_watched', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_states', to='main.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movie_states', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'отметка пользователя',
                'verbose_name_plural': 'отметки пользователей',
            },
        ),
        migrations.AddConstraint(
            model_name='movielistitem',
            constraint=models.UniqueConstraint(fields=('movie_list', 'movie'), name='movie_once_per_list'),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('user', 'movie'), name='one_review_per_user_movie'),
        ),
        migrations.AddConstraint(
            model_name='reviewlike',
            constraint=models.UniqueConstraint(fields=('user', 'review'), name='one_like_per_user_review'),
        ),
        migrations.AddConstraint(
            model_name='usermovie',
            constraint=models.UniqueConstraint(fields=('user', 'movie'), name='one_state_per_user_movie'),
        ),
    ]
