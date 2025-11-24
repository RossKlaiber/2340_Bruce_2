# Generated manually because Django is not available in the execution environment.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0002_savedcandidatesearch_last_match_results_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationCoordinate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_term', models.CharField(max_length=255)),
                ('normalized_name', models.CharField(max_length=255, unique=True)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('display_name', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
