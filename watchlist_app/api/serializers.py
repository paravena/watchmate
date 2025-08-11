from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from watchlist_app.models import Genre, Movie, Rating, Review, StreamingPlatform, Watchlist, WatchlistItem

User = get_user_model()


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "created_at", "updated_at", "is_active"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamingPlatform
        fields = ["id", "name", "website", "description", "created_at", "updated_at", "is_active"]
        read_only_fields = ["id", "created_at", "updated_at"]


class MovieSerializer(serializers.ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), many=True, required=False)
    platforms = serializers.PrimaryKeyRelatedField(queryset=StreamingPlatform.objects.all(), many=True, required=False)
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "release_date",
            "duration",
            "poster_url",
            "genres",
            "platforms",
            "avg_rating",
            "created_at",
            "updated_at",
            "is_active",
        ]
        read_only_fields = ["id", "avg_rating", "created_at", "updated_at"]

    def validate_duration(self, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise serializers.ValidationError("Duration must be positive")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "movie", "title", "body", "created_at", "updated_at", "is_active"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Rating
        fields = ["id", "user", "movie", "score", "created_at", "updated_at", "is_active"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate_score(self, value: int) -> int:
        if not 1 <= int(value) <= 5:
            raise serializers.ValidationError("Score must be between 1 and 5")
        return value


class WatchlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistItem
        fields = ["id", "watchlist", "movie", "created_at", "updated_at", "is_active"]
        read_only_fields = ["id", "created_at", "updated_at"]


class WatchlistSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    items = WatchlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Watchlist
        fields = ["id", "user", "name", "description", "items", "created_at", "updated_at", "is_active"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class MovieDetailSerializer(MovieSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    platforms = PlatformSerializer(many=True, read_only=True)


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def create(self, validated_data: dict[str, Any]) -> User:  # type: ignore[name-defined]
        # Use Django's built-in user creation to ensure password hashing
        username = validated_data.get("username")
        email = validated_data.get("email")
        password = validated_data.get("password")
        user = User.objects.create_user(username=username, email=email, password=password)
        return user
