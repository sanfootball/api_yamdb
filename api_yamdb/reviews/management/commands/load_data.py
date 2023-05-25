import csv
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
                base_slug = slugify(name).lower()
                slug = base_slug
                counter = 1
                while Genre.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                genre, created = Genre.objects.get_or_create(
                    name=name, defaults={'slug': slug})
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Genre "{genre.name}" created with slug "{genre.slug}"')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Genre "{genre.name}" already exists with slug "{genre.slug}"')
                    )

    def load_titles(self, path):
        title_file = os.path.join(path, 'titles.csv')
        with open(title_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row['name']
                year = int(row['year'])
                category_id = int(row['category'])
                if not self.get_object_by_id(Category, category_id):
                    continue
                category = self.get_object_by_id(Category, category_id)
                title, created = Title.objects.get_or_create(
                    name=name, year=year, category=category
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Title "{title.name}" created'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Title "{title.name}" already exists'))

    def get_object_by_id(self, obj, pk):
        try:
            value = obj.objects.get(pk=pk)
        except obj.DoesNotExist:
            self.stderr.write(self.style.ERROR(
                f'{obj.__name__} with ID "{pk}" does not exist'))
            return False
        return value

    def load_genre_titles(self, path):
        genre_title_file = os.path.join(path, 'genre_title.csv')
        with open(genre_title_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    genre = Genre.objects.get(pk=row['genre_id'])
                    title = Title.objects.get(pk=row['title_id'])
                    genre_title, created = TitleGenre.objects.get_or_create(
                        title=title,
                        genre=genre
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(
                            f'TitleGenre {genre_title.id} created'))
                    else:
                        self.stdout.write(self.style.SUCCESS(
                            f'TitleGenre {genre_title.id} already exists'))
                except Genre.DoesNotExist:
                    self.stderr.write(self.style.ERROR(
                        f'Genre with ID "{row["genre_id"]}" does not exist'))
                except Title.DoesNotExist:
                    self.stderr.write(self.style.ERROR(
                        f'Title with ID "{row["title_id"]}" does not exist'))

    def load_users(self, path):
        user_file = os.path.join(path, 'users.csv')
        with open(user_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_id = row['id']
                username = row['username']
                email = row['email']
                first_name = row['first_name']
                last_name = row['last_name']
                role = row['role']
                bio = row['bio']

                user, created = User.objects.update_or_create(
                    id=user_id,
                    defaults={
                        'username': username,
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                        'role': role,
                        'bio': bio
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'User "{user.username}" created'))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f'User "{user.username}" updated'))

    def load_reviews(self, path):
        reviews_file = os.path.join(path, 'review.csv')
        try:
            with open(reviews_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        title_id = row['title_id']
                        author_id = row['author']
                        defaults = {
                            'text': row['text'],
                            'score': row['score'],
                            'pub_date': row['pub_date']
                        }
                        review, created = Review.objects.update_or_create(
                            title_id=title_id,
                            author_id=author_id,
                            defaults=defaults
                        )

                        if created:
                            self.stdout.write(self.style.SUCCESS(
                                f"Review {review.id} created"))
                        else:
                            self.stdout.write(self.style.SUCCESS(
                                f"Review {review.id} updated"))
                    except ObjectDoesNotExist:
                        self.stderr.write(
                            self.style.ERROR('Error creating review: Title or User not found'))
        except FileNotFoundError:
            raise CommandError(f'The file "{reviews_file}" does not exist')

    def load_comments(self, path):
        comments_file = os.path.join(path, 'comments.csv')
        try:
            with open(comments_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        if not self.get_object_by_id(Review, row['review_id']):
                            continue
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
