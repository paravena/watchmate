from __future__ import annotations

from datetime import date
from typing import Iterable

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from watchlist_app.models import (
    Genre,
    Movie,
    Rating,
    Review,
    StreamingPlatform,
    Watchlist,
    WatchlistItem,
)

User = get_user_model()

SEED_USERS = [
    {"username": "alice", "email": "alice@example.com", "password": "password123"},
    {"username": "bob", "email": "bob@example.com", "password": "password123"},
]

SEED_PLATFORMS = [
    {"name": "Netflix", "website": "https://www.netflix.com", "description": "Streaming service"},
    {"name": "Hulu", "website": "https://www.hulu.com", "description": "TV and movies"},
    {"name": "Disney+", "website": "https://www.disneyplus.com", "description": "Disney, Marvel, Star Wars"},
]

SEED_GENRES = [
    "Action",
    "Adventure",
    "Comedy",
    "Drama",
    "Sci-Fi",
    "Thriller",
]

SEED_MOVIES = [
    {
        "title": "The Matrix",
        "description": "A hacker discovers the true nature of his reality.",
        "release_date": date(1999, 3, 31),
        "duration": 136,
        "poster_url": "https://example.com/matrix.jpg",
        "genres": ["Action", "Sci-Fi", "Thriller"],
        "platforms": ["Netflix"],
    },
    {
        "title": "Inception",
        "description": "A thief who steals corporate secrets through dream-sharing technology.",
        "release_date": date(2010, 7, 16),
        "duration": 148,
        "poster_url": "https://example.com/inception.jpg",
        "genres": ["Action", "Adventure", "Sci-Fi"],
        "platforms": ["Hulu"],
    },
    {
        "title": "Toy Story",
        "description": "Toys come to life when humans aren't around.",
        "release_date": date(1995, 11, 22),
        "duration": 81,
        "poster_url": "https://example.com/toy-story.jpg",
        "genres": ["Comedy", "Adventure"],
        "platforms": ["Disney+"],
    },
]


class Command(BaseCommand):
    help = "Seed the database with example data. Idempotent. Use --reset to remove previously seeded data first."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete previously seeded data before creating new records (safe, app-scoped).",
        )

    def handle(self, *args, **options):
        reset: bool = options.get("reset", False)

        if reset:
            self.stdout.write(self.style.WARNING("Resetting previously seeded data..."))
            self._reset_seed_data()

        with transaction.atomic():
            users = self._seed_users()
            platforms = self._seed_platforms()
            genres = self._seed_genres()
            movies = self._seed_movies(genres=genres, platforms=platforms)
            self._seed_watchlists(users=users, movies=movies)
            self._seed_reviews_and_ratings(users=users, movies=movies)

        self.stdout.write(self.style.SUCCESS("Seeding completed successfully."))

    # --- helpers ---

    def _reset_seed_data(self) -> None:
        from django.db.utils import OperationalError, ProgrammingError
        try:
            # Delete dependent objects first to respect FKs
            Rating.objects.all().delete()
            Review.objects.all().delete()
            WatchlistItem.objects.all().delete()
            Watchlist.objects.all().delete()
            # Clear M2M relations by deleting movies (M2M cleans automatically)
            Movie.objects.all().delete()
            Genre.objects.all().delete()
            StreamingPlatform.objects.all().delete()
            # Delete only seed users (leave any existing non-seed users untouched)
            User.objects.filter(username__in=[u["username"] for u in SEED_USERS]).delete()
        except (OperationalError, ProgrammingError):
            # Tables are likely not created yet; ignore reset.
            self.stdout.write(self.style.NOTICE("Tables not found; skipping reset."))

    def _seed_users(self) -> list[User]:
        created_users: list[User] = []
        for u in SEED_USERS:
            user, created = User.objects.get_or_create(
                username=u["username"], defaults={"email": u["email"]}
            )
            # ensure password is set (even if user existed without it)
            if created or not user.has_usable_password():
                user.set_password(u["password"])
                user.save(update_fields=["password"])
            created_users.append(user)
        return created_users

    def _seed_platforms(self) -> list[StreamingPlatform]:
        platforms: list[StreamingPlatform] = []
        for p in SEED_PLATFORMS:
            obj, _ = StreamingPlatform.objects.get_or_create(
                name=p["name"], defaults={"website": p.get("website", ""), "description": p.get("description", "")}
            )
            platforms.append(obj)
        return platforms

    def _seed_genres(self) -> list[Genre]:
        genres: list[Genre] = []
        for name in SEED_GENRES:
            obj, _ = Genre.objects.get_or_create(name=name)
            genres.append(obj)
        return genres

    def _by_name(self, items: Iterable, name: str):
        for it in items:
            if getattr(it, "name", None) == name:
                return it
        return None

    def _seed_movies(self, *, genres: list[Genre], platforms: list[StreamingPlatform]) -> list[Movie]:
        result: list[Movie] = []
        for m in SEED_MOVIES:
            movie, _ = Movie.objects.get_or_create(
                title=m["title"],
                release_date=m["release_date"],
                defaults={
                    "description": m["description"],
                    "duration": m.get("duration"),
                    "poster_url": m.get("poster_url"),
                },
            )
            # set many-to-many relations idempotently
            genre_objs = [self._by_name(genres, g) for g in m.get("genres", [])]
            platform_objs = [self._by_name(platforms, p) for p in m.get("platforms", [])]
            movie.genres.set([g for g in genre_objs if g])
            movie.platforms.set([p for p in platform_objs if p])
            result.append(movie)
        return result

    def _seed_watchlists(self, *, users: list[User], movies: list[Movie]) -> None:
        if not users or not movies:
            return
        # Each user gets a default watchlist with first two movies
        for user in users:
            wl, _ = Watchlist.objects.get_or_create(user=user, name="My Watchlist", defaults={"description": "Default list"})
            to_add = movies[:2] if len(movies) >= 2 else movies
            for mv in to_add:
                WatchlistItem.objects.get_or_create(watchlist=wl, movie=mv)

    def _seed_reviews_and_ratings(self, *, users: list[User], movies: list[Movie]) -> None:
        if len(users) < 2 or len(movies) < 2:
            return
        alice, bob = users[0], users[1]
        m1, m2 = movies[0], movies[1]

        # Ratings are unique per (user, movie)
        Rating.objects.get_or_create(user=alice, movie=m1, defaults={"score": 5})
        Rating.objects.get_or_create(user=bob, movie=m1, defaults={"score": 4})
        Rating.objects.get_or_create(user=alice, movie=m2, defaults={"score": 4})

        # Reviews allow multiple titles per (user, movie) as long as title diff; provide one each idempotently
        Review.objects.get_or_create(user=alice, movie=m1, title="Mind-blowing", defaults={"body": "A classic."})
        Review.objects.get_or_create(user=bob, movie=m1, title="Great action", defaults={"body": "Loved the concept."})
