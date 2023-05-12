import csv
import random
import string
import os
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from reviews.models import User, Category, Genre, Title, Comment, Review


class Command(BaseCommand):
    help = 'Load data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            'path', type=str, help='Path to the directory containing CSV files')

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
                    continue  # skip the header row
                name = row[0]
                slug = slugify(name) + '-' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                genre = Genre(name=name, slug=slug)
                genre.save()
                self.stdout.write(self.style.SUCCESS(f'Genre "{genre.name}" created'))

    def load_titles(self, path):
        title_file = os.path.join(path, 'titles.csv')
        with open(title_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row['name']
                year = int(row['year'])
                category_id = int(row['id'])
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
                title_id = int(row['title_id'])
                genre_id = int(row['genre_id'])
                try:
                    genre = Genre.objects.get(pk=genre_id)
                    genre.titles.add(title_id)
                    genre.save()
                except Genre.DoesNotExist:
                    self.stderr.write(self.style.ERROR(
                        f'Genre with ID "{genre_id}" does not exist'))


    def load_users(self, path):
        user_file = os.path.join(path, 'users.csv')
        with open(user_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Assuming you have fields like username, email, password_hash in the CSV
                username = row['username']
                email = row['email']
                password_hash = row['password_hash']
                # Create a user object and save it
                user = User(username=username, email=email,
                            password=password_hash)
                user.save()
                self.stdout.write(self.style.SUCCESS(
                    f'User "{user.username}" created'))

    def load_reviews(self, path):
        reviews_file = path + 'review.csv'
        try:
            with open(reviews_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    review = Review(
                        id=row['id'],
                        title_id=row['title_id'],
                        text=row['text'],
                        author_id=row['author_id'],
                        score=row['score'],
                        pub_date=row['pub_date']
                    )
                    review.save()
                    print(f'Review "{review.title_id}" created')
        except FileNotFoundError:
            raise CommandError(f'The file "{reviews_file}" does not exist')

    def load_comments(self, path):
        comments_file = path + 'comments.csv'
        try:
            with open(comments_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    comment = Comment(
                        id=row['id'],
                        review_id=row['review_id'],
                        text=row['text'],
                        author_id=row['author_id'],
                        pub_date=row['pub_date']
                    )
                    comment.save()
                    print(f'Comment "{comment.id}" created')
        except FileNotFoundError:
            raise CommandError(f'The file "{comments_file}" does not exist')
