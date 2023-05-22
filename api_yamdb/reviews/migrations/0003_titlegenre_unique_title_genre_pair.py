# Generated by Django 3.2 on 2023-05-21 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20230521_1912'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='titlegenre',
            constraint=models.UniqueConstraint(fields=('title', 'genre'), name='unique_title_genre_pair'),
        ),
    ]
