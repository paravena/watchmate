from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from watchlist_app.api.serializers import (
    GenreSerializer,
    MovieDetailSerializer,
    MovieSerializer,
    PlatformSerializer,
    RatingSerializer,
    ReviewSerializer,
    WatchlistItemSerializer,
    WatchlistSerializer,
)
from watchlist_app.models import Genre, Movie, Rating, Review, StreamingPlatform, Watchlist, WatchlistItem


class ReadOnlyOrIsAuthenticated(permissions.BasePermission):
    """Allow read-only access to anyone, write access to authenticated users."""

    def has_permission(self, request: Request, view: viewsets.ViewSet) -> bool:  # type: ignore[override]
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)


class PlatformViewSet(viewsets.ModelViewSet):
    queryset: QuerySet[StreamingPlatform] = StreamingPlatform.objects.filter(is_active=True)
    serializer_class = PlatformSerializer
    permission_classes = [ReadOnlyOrIsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "description"]
    filterset_fields = ["name", "is_active"]


class GenreViewSet(viewsets.ModelViewSet):
    queryset: QuerySet[Genre] = Genre.objects.filter(is_active=True)
    serializer_class = GenreSerializer
    permission_classes = [ReadOnlyOrIsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name"]
    filterset_fields = ["name", "is_active"]


class MovieViewSet(viewsets.ModelViewSet):
    queryset: QuerySet[Movie] = Movie.objects.filter(is_active=True)
    serializer_class = MovieSerializer
    permission_classes = [ReadOnlyOrIsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["title", "description"]
    filterset_fields = ["genres", "platforms", "release_date", "is_active"]
    ordering_fields = ["created_at", "release_date", "title"]

    def get_serializer_class(self):  # type: ignore[override]
        if self.action in ["retrieve"]:
            return MovieDetailSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request: Request, pk: str | None = None) -> Response:
        movie = self.get_object()
        serializer = RatingSerializer(data={"movie": movie.id, "score": request.data.get("score")})
        serializer.is_valid(raise_exception=True)
        Rating.objects.update_or_create(
            user=request.user,  # type: ignore[arg-type]
            movie=movie,
            defaults={"score": serializer.validated_data["score"]},
        )
        return Response(RatingSerializer(Rating.objects.get(user=request.user, movie=movie)).data, status=status.HTTP_201_CREATED)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset: QuerySet[Review] = Review.objects.filter(is_active=True)
    serializer_class = ReviewSerializer
    permission_classes = [ReadOnlyOrIsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["title", "body"]
    filterset_fields = ["movie", "user"]

    def perform_create(self, serializer: ReviewSerializer) -> None:  # type: ignore[override]
        serializer.save(user=self.request.user)


class WatchlistViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "description"]

    def get_queryset(self) -> QuerySet[Watchlist]:  # type: ignore[override]
        return Watchlist.objects.filter(user=self.request.user)  # type: ignore[arg-type]

    def perform_create(self, serializer: WatchlistSerializer) -> None:  # type: ignore[override]
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="add-item")
    def add_item(self, request: Request, pk: str | None = None) -> Response:
        watchlist = self.get_object()
        movie_id = request.data.get("movie")
        if not movie_id:
            return Response({"detail": "movie is required"}, status=status.HTTP_400_BAD_REQUEST)
        item, _ = WatchlistItem.objects.get_or_create(watchlist=watchlist, movie_id=movie_id)
        return Response(WatchlistItemSerializer(item).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="remove-item")
    def remove_item(self, request: Request, pk: str | None = None) -> Response:
        watchlist = self.get_object()
        movie_id = request.data.get("movie")
        try:
            item = WatchlistItem.objects.get(watchlist=watchlist, movie_id=movie_id)
        except WatchlistItem.DoesNotExist:
            return Response({"detail": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="bulk-add")
    def bulk_add(self, request: Request, pk: str | None = None) -> Response:
        watchlist = self.get_object()
        movie_ids = request.data.get("movies", [])
        if not isinstance(movie_ids, list) or not movie_ids:
            return Response({"detail": "movies must be a non-empty list of IDs"}, status=status.HTTP_400_BAD_REQUEST)
        created = []
        for mid in movie_ids:
            item, _ = WatchlistItem.objects.get_or_create(watchlist=watchlist, movie_id=mid)
            created.append(item)
        return Response(WatchlistItemSerializer(created, many=True).data, status=status.HTTP_201_CREATED)
