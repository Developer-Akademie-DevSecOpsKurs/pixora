"""
Management command: seed_db

Creates fake users, follow relationships, posts, likes and comments.
Usage:
    python manage.py seed_db
    python manage.py seed_db --reset   # Wipes existing data first
"""
from __future__ import annotations

import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from faker import Faker

from apps.posts.models import Comment, Like, Post
from apps.users.models import Follow

User = get_user_model()
fake = Faker()

NUM_USERS = 10
FOLLOWS_PER_USER_MIN = 2
FOLLOWS_PER_USER_MAX = 5
POSTS_PER_USER_MIN = 3
POSTS_PER_USER_MAX = 5
COMMENTS_PER_POST_MIN = 0
COMMENTS_PER_POST_MAX = 5


class Command(BaseCommand):
    help = 'Seed the database with fake users, posts, likes and comments.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Clear all existing users (except superusers), posts, likes and comments before seeding.',
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        if options['reset']:
            self.stdout.write(self.style.WARNING('Resetting data...'))
            Comment.objects.all().delete()
            Like.objects.all().delete()
            Post.objects.all().delete()
            Follow.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Data cleared.'))

        self.stdout.write('Creating users...')
        users: list[User] = []
        for i in range(NUM_USERS):
            username = fake.unique.user_name()[:30]
            email = fake.unique.email()
            bio = fake.text(max_nb_chars=150)
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                bio=bio,
            )
            users.append(user)
            self.stdout.write(f'  Created user: {username}')

        self.stdout.write('Creating follow relationships...')
        for user in users:
            potential_targets = [u for u in users if u != user]
            num_follows = random.randint(FOLLOWS_PER_USER_MIN, FOLLOWS_PER_USER_MAX)
            targets = random.sample(potential_targets, min(num_follows, len(potential_targets)))
            for target in targets:
                Follow.objects.get_or_create(follower=user, following=target)
        self.stdout.write(f'  Total follows created: {Follow.objects.count()}')

        self.stdout.write('Creating posts...')
        posts: list[Post] = []
        for user in users:
            num_posts = random.randint(POSTS_PER_USER_MIN, POSTS_PER_USER_MAX)
            for _ in range(num_posts):
                caption = fake.text(max_nb_chars=200)
                # We skip uploading a real image — set image field to a placeholder path.
                # In production the field requires a real file; here we store a string
                # directly to avoid needing actual image files during seeding.
                post = Post.objects.create(owner=user, caption=caption)
                posts.append(post)
        self.stdout.write(f'  Total posts created: {len(posts)}')

        self.stdout.write('Creating likes...')
        for post in posts:
            potential_likers = [u for u in users if u != post.owner]
            num_likes = random.randint(0, len(potential_likers))
            likers = random.sample(potential_likers, num_likes)
            for liker in likers:
                Like.objects.get_or_create(post=post, user=liker)
        self.stdout.write(f'  Total likes created: {Like.objects.count()}')

        self.stdout.write('Creating comments...')
        for post in posts:
            num_comments = random.randint(COMMENTS_PER_POST_MIN, COMMENTS_PER_POST_MAX)
            top_level_comments: list[Comment] = []
            for _ in range(num_comments):
                commenter = random.choice(users)
                comment = Comment.objects.create(
                    post=post,
                    user=commenter,
                    text=fake.sentence(nb_words=random.randint(5, 20)),
                )
                top_level_comments.append(comment)
            # Add a random reply to some top-level comments
            for parent in top_level_comments:
                if random.random() < 0.3:
                    replier = random.choice(users)
                    Comment.objects.create(
                        post=post,
                        user=replier,
                        text=fake.sentence(nb_words=random.randint(3, 12)),
                        parent=parent,
                    )
        self.stdout.write(f'  Total comments created: {Comment.objects.count()}')

        self.stdout.write(self.style.SUCCESS(
            f'\nSeeding complete! '
            f'{User.objects.filter(is_superuser=False).count()} users, '
            f'{Post.objects.count()} posts, '
            f'{Like.objects.count()} likes, '
            f'{Comment.objects.count()} comments, '
            f'{Follow.objects.count()} follows.'
        ))
