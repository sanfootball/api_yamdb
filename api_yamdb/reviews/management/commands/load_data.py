
import csv
import random
import string
import os
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from reviews.models import (
    User,
    Category,
    Genre,
    Title,
    Comment,
    Review,
    TitleGenre,
)
from datetime import datetime


datetime_str = "2020-01-13T23:20:02.422Z"
datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")


class Command(BaseCommand):
    help = 'Load data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            'path', type=str, help='Path to the directory containing CSV files'
        )

    def handle(self, *args, **options):
        path = options['path']
        self.load_category(path)
        self.load_genres(path)
        self.load_titles(path)
        self.load_genre_titles(path)
        self.load_users(path)
        self.load_reviews(path)
        self.load_comments(path)

    def load_category(self, path):
        file_path = os.path.join(path, 'category.csv')
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category, created = Category.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Category "{category.name}" created'))

    def load_genres(self, path):
        genre_file = os.path.join(path, 'genre.csv')
        with open(genre_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for idx, row in enumerate(reader):
                if idx == 0:
                    continue
                name = row[1]
                slug = slugify(name) + '-' + ''.join(random.choices(
                    string.ascii_lowercase + string.digits, k=6))
                genre = Genre(name=name, slug=slug)
                genre.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Genre "{genre.name}" created'))

    def load_titles(self, path):
        title_file = os.path.join(path, 'titles.csv')
        with open(title_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row['name']
                year = int(row['year'])
                category_id = int(row['category'])
                category = Category.objects.get(pk=category_id)
                title = Title(name=name, year=year, category=category)
                title.save()
                self.stdout.write(self.style.SUCCESS(
                    f'Title "{title.name}" created'))

    def load_genre_titles(self, path):
        genre_title_file = os.path.join(path, 'genre_title.csv')
        with open(genre_title_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    genre = Genre.objects.get(pk=row['genre_id'])
                    title = Title.objects.get(pk=row['title_id'])
                    genre_titles = TitleGenre(title=title, genre=genre)
                    genre_titles.save()
                except Genre.DoesNotExist:
                    self.stderr.write(self.style.ERROR(
                        f'Genre with ID "{genre}" does not exist'))

    def load_users(self, path):
        user_file = os.path.join(path, 'users.csv')
        with open(user_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user = User(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    role=row['role'],
                    bio=row['bio'])
                user.save()
                self.stdout.write(self.style.SUCCESS(
                    f'User "{user.username}" created'))

    def load_reviews(self, path):
        reviews_file = os.path.join(path, 'review.csv')
        try:
            with open(reviews_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        review = Review.objects.create(
                            title=Title.objects.get(id=row['title_id']),
                            text=row['text'],
                            author=User.objects.get(id=row['author']),
                            score=row['score'],
                            pub_date=row['pub_date']
                        )

                        self.stdout.write(
                            self.style.SUCCESS(f"Review {row['id']} created"))
                    except ObjectDoesNotExist:
                        self.stderr.write(
                            self.style.ERROR('Error creating review:'
                                             'Title or User not found'))
        except FileNotFoundError:
            raise CommandError(f'The file "{reviews_file}" does not exist')

    def load_comments(self, path):
        comments_file = os.path.join(path, 'comments.csv')
        try:
            with open(comments_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        comment = Comment.objects.create(
                            review=Review.objects.get(id=row['review_id']),
                            text=row['text'],
                            author=User.objects.get(id=row['author']),
                            pub_date=row['pub_date']
                        )
                        self.stdout.write(self.style.SUCCESS(
                            f'Comment "{comment.id}" created'))
                    except ObjectDoesNotExist:
                        self.stderr.write(self.style.ERROR(
                            'Error creating comment: Review or User not found')
                        )
        except FileNotFoundError:
            raise CommandError(f'The file "{comments_file}" does not exist')
