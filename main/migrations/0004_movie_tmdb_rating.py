from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_movie_tmdb_votes'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='tmdb_rating',
            field=models.FloatField(default=0, editable=False, verbose_name='Оценка TMDB'),
        ),
    ]
