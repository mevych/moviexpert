from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='imdb_id',
        ),
        migrations.RemoveField(
            model_name='movie',
            name='imdb_rating',
        ),
        migrations.RemoveField(
            model_name='movie',
            name='imdb_updated',
        ),
        migrations.RemoveField(
            model_name='movie',
            name='imdb_votes',
        ),
    ]
