from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class TimeStampedSoftDeleteModel(models.Model):
    """Abstract base model with created/updated timestamps and soft-delete fields."""

    created_at: timezone.datetime = models.DateTimeField(auto_now_add=True)
    updated_at: timezone.datetime = models.DateTimeField(auto_now=True)
    is_active: bool = models.BooleanField(default=True, db_index=True)
    deleted_at: timezone.datetime | None = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_active", "deleted_at"])


class StreamingPlatform(TimeStampedSoftDeleteModel):
    name: str = models.CharField(max_length=100, unique=True)
    website: str = models.URLField(blank=True)
    description: str = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - simple dunder
        return self.name


class Genre(TimeStampedSoftDeleteModel):
    name: str = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]

    def __str__(self) -> str:
        return self.name


class Movie(TimeStampedSoftDeleteModel):
    title: str = models.CharField(max_length=255, db_index=True)
    description: str = models.TextField()
    release_date: timezone.datetime | None = models.DateField(null=True, blank=True)
    duration: int | None = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in minutes")
    poster_url: str | None = models.URLField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name="movies", blank=True)
    platforms = models.ManyToManyField(StreamingPlatform, related_name="movies", blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["title", "release_date"], name="uniq_movie_title_release"),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def avg_rating(self) -> float:
        agg = self.ratings.filter(is_active=True).aggregate(models.Avg("score"))
        return float(agg["score__avg"]) if agg["score__avg"] is not None else 0.0


class Watchlist(TimeStampedSoftDeleteModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watchlists")
    name: str = models.CharField(max_length=150)
    description: str = models.TextField(blank=True)

    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.user} - {self.name}"


class WatchlistItem(TimeStampedSoftDeleteModel):
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, related_name="items")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="in_watchlists")

    class Meta:
        unique_together = ("watchlist", "movie")
        indexes = [models.Index(fields=["watchlist", "movie"]) ]

    def __str__(self) -> str:
        return f"{self.watchlist}: {self.movie}"


class Review(TimeStampedSoftDeleteModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    title: str = models.CharField(max_length=255)
    body: str = models.TextField(blank=True)

    class Meta:
        unique_together = ("user", "movie", "title")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Review({self.user} -> {self.movie})"


class Rating(TimeStampedSoftDeleteModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    score: int = models.IntegerField()

    class Meta:
        unique_together = ("user", "movie")
        indexes = [models.Index(fields=["movie"]) ]

    def clean(self) -> None:
        if not 1 <= int(self.score) <= 5:
            from django.core.exceptions import ValidationError
            raise ValidationError({"score": "Score must be between 1 and 5"})

    def __str__(self) -> str:
        return f"Rating({self.score}) {self.user} -> {self.movie}"
