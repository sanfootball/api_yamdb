# Generated by Django 3.2 on 2023-05-24 17:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_alter_title_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titlegenre',
            name='genre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genres', to='reviews.genre', verbose_name='Жанр'),
        ),
        migrations.AlterField(
            model_name='titlegenre',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='titles', to='reviews.title', verbose_name='Произведение'),
        ),
    ]