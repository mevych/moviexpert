from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_remove_movie_imdb_id_remove_movie_imdb_rating_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='tmdb_votes',
            field=models.PositiveIntegerField(default=0, editable=False, verbose_name='Голосов на TMDB'),
        ),
    ]
