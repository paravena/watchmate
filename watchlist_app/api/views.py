from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.views import APIView
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
    SignupSerializer,
)
from watchlist_app.models import Genre, Movie, Rating, Review, StreamingPlatform, Watchlist, WatchlistItem
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings
from django.contrib.auth import get_user_model


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

    @swagger_auto_schema(
        operation_summary="Create streaming platform",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, example="Netflix"),
                "website": openapi.Schema(type=openapi.TYPE_STRING, example="https://www.netflix.com"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, example="Popular streaming platform"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
            description="Create a new streaming platform",
        ),
        responses={
            201: openapi.Response(
                description="Created",
                examples={
                    "application/json": {
                        "id": 10,
                        "name": "Netflix",
                        "website": "https://www.netflix.com",
                        "description": "Popular streaming platform",
                        "created_at": "2025-01-01T12:00:00Z",
                        "updated_at": "2025-01-01T12:00:00Z",
                        "is_active": True,
                    }
                },
            )
        },
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update streaming platform",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, example="Netflix"),
                "website": openapi.Schema(type=openapi.TYPE_STRING, example="https://www.netflix.com"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, example="Popular streaming platform"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={200: openapi.Response(description="OK")},
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update streaming platform",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, example="Netflix"),
                "website": openapi.Schema(type=openapi.TYPE_STRING, example="https://www.netflix.com"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, example="Popular streaming platform"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={200: openapi.Response(description="OK")},
    )
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().partial_update(request, *args, **kwargs)


class GenreViewSet(viewsets.ModelViewSet):
    queryset: QuerySet[Genre] = Genre.objects.filter(is_active=True)
    serializer_class = GenreSerializer
    permission_classes = [ReadOnlyOrIsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name"]
    filterset_fields = ["name", "is_active"]

    @swagger_auto_schema(
        operation_summary="Create genre",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, example="Action"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={
            201: openapi.Response(
                description="Created",
                examples={
                    "application/json": {
                        "id": 5,
                        "name": "Action",
                        "created_at": "2025-01-01T12:00:00Z",
                        "updated_at": "2025-01-01T12:00:00Z",
                        "is_active": True,
                    }
                },
            )
        },
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update genre",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, example="Action"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={200: openapi.Response(description="OK")},
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update genre",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, example="Action"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={200: openapi.Response(description="OK")},
    )
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().partial_update(request, *args, **kwargs)


class MovieViewSet(viewsets.ModelViewSet):
    queryset: QuerySet[Movie] = Movie.objects.filter(is_active=True)
    serializer_class = MovieSerializer
    permission_classes = [ReadOnlyOrIsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["title", "description"]
    filterset_fields = ["genres", "platforms", "release_date", "is_active"]
    ordering_fields = ["created_at", "release_date", "title"]

    @swagger_auto_schema(
        operation_summary="Create movie",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title"],
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, example="Inception"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, example="A mind-bending thriller"),
                "release_date": openapi.Schema(type=openapi.TYPE_STRING, format="date", example="2024-05-01"),
                "duration": openapi.Schema(type=openapi.TYPE_INTEGER, example=148),
                "poster_url": openapi.Schema(type=openapi.TYPE_STRING, example="https://example.com/poster.jpg"),
                "genres": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), example=[1, 2]),
                "platforms": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), example=[1]),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={201: openapi.Response(description="Created")},
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update movie",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, example="Inception"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, example="A mind-bending thriller"),
                "release_date": openapi.Schema(type=openapi.TYPE_STRING, format="date", example="2024-05-01"),
                "duration": openapi.Schema(type=openapi.TYPE_INTEGER, example=148),
                "poster_url": openapi.Schema(type=openapi.TYPE_STRING, example="https://example.com/poster.jpg"),
                "genres": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), example=[1, 2]),
                "platforms": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), example=[1]),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={200: openapi.Response(description="OK")},
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update movie",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, example="Inception"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, example="A mind-bending thriller"),
                "release_date": openapi.Schema(type=openapi.TYPE_STRING, format="date", example="2024-05-01"),
                "duration": openapi.Schema(type=openapi.TYPE_INTEGER, example=148),
                "poster_url": openapi.Schema(type=openapi.TYPE_STRING, example="https://example.com/poster.jpg"),
                "genres": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), example=[1, 2]),
                "platforms": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), example=[1]),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={200: openapi.Response(description="OK")},
    )
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().partial_update(request, *args, **kwargs)

    def get_serializer_class(self):  # type: ignore[override]
        if self.action in ["retrieve"]:
            return MovieDetailSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(
        method="post",
        operation_summary="Rate a movie",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["score"],
            properties={
                "score": openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
            },
        ),
        responses={
            201: openapi.Response(
                description="Created",
                examples={
                    "application/json": {
                        "id": 1,
                        "user": 3,
                        "movie": 12,
                        "score": 5,
                        "created_at": "2025-01-01T12:00:00Z",
                        "updated_at": "2025-01-01T12:00:00Z",
                        "is_active": True,
                    }
                },
            )
        },
    )
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

    @swagger_auto_schema(
        operation_summary="Create review",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["movie", "title", "body"],
            properties={
                "movie": openapi.Schema(type=openapi.TYPE_INTEGER, example=12),
                "title": openapi.Schema(type=openapi.TYPE_STRING, example="Amazing movie"),
                "body": openapi.Schema(type=openapi.TYPE_STRING, example="I loved the plot and characters"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={201: openapi.Response(description="Created")},
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update review",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "movie": openapi.Schema(type=openapi.TYPE_INTEGER, example=12),
                "title": openapi.Schema(type=openapi.TYPE_STRING, example="Amazing movie"),
                "body": openapi.Schema(type=openapi.TYPE_STRING, example="I loved the plot and characters"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={200: openapi.Response(description="OK")},
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update review",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "movie": openapi.Schema(type=openapi.TYPE_INTEGER, example=12),
                "title": openapi.Schema(type=openapi.TYPE_STRING, example="Amazing movie"),
                "body": openapi.Schema(type=openapi.TYPE_STRING, example="I loved the plot and characters"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={200: openapi.Response(description="OK")},
    )
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().partial_update(request, *args, **kwargs)

    def perform_create(self, serializer: ReviewSerializer) -> None:  # type: ignore[override]
        serializer.save(user=self.request.user)


class WatchlistViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "description"]

    @swagger_auto_schema(
        operation_summary="Create watchlist",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, example="My Watchlist"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, example="Movies to watch this month"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={201: openapi.Response(description="Created")},
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update watchlist",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, example="My Watchlist"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, example="Movies to watch this month"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={200: openapi.Response(description="OK")},
    )
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update watchlist",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, example="My Watchlist"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, example="Movies to watch this month"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
            },
        ),
        responses={200: openapi.Response(description="OK")},
    )
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return super().partial_update(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Watchlist]:  # type: ignore[override]
        return Watchlist.objects.filter(user=self.request.user)  # type: ignore[arg-type]

    def perform_create(self, serializer: WatchlistSerializer) -> None:  # type: ignore[override]
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        method="post",
        operation_summary="Add item to watchlist",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["movie"],
            properties={"movie": openapi.Schema(type=openapi.TYPE_INTEGER, example=1)},
        ),
        responses={
            201: openapi.Response(
                description="Created",
                examples={
                    "application/json": {
                        "id": 1,
                        "watchlist": 3,
                        "movie": 1,
                        "created_at": "2025-01-01T12:00:00Z",
                        "updated_at": "2025-01-01T12:00:00Z",
                        "is_active": True,
                    }
                },
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="add-item")
    def add_item(self, request: Request, pk: str | None = None) -> Response:
        watchlist = self.get_object()
        movie_id = request.data.get("movie")
        if not movie_id:
            return Response({"detail": "movie is required"}, status=status.HTTP_400_BAD_REQUEST)
        item, _ = WatchlistItem.objects.get_or_create(watchlist=watchlist, movie_id=movie_id)
        return Response(WatchlistItemSerializer(item).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        method="post",
        operation_summary="Remove item from watchlist",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["movie"],
            properties={"movie": openapi.Schema(type=openapi.TYPE_INTEGER, example=1)},
        ),
        responses={204: openapi.Response(description="No Content")},
    )
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

    @swagger_auto_schema(
        method="post",
        operation_summary="Bulk add items to watchlist",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["movies"],
            properties={
                "movies": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    example=[1, 2, 3],
                )
            },
        ),
        responses={
            201: openapi.Response(
                description="Created",
                examples={
                    "application/json": [
                        {
                            "id": 11,
                            "watchlist": 3,
                            "movie": 1,
                            "created_at": "2025-01-01T12:00:00Z",
                            "updated_at": "2025-01-01T12:00:00Z",
                            "is_active": True,
                        },
                        {
                            "id": 12,
                            "watchlist": 3,
                            "movie": 2,
                            "created_at": "2025-01-01T12:00:00Z",
                            "updated_at": "2025-01-01T12:00:00Z",
                            "is_active": True,
                        },
                    ]
                },
            )
        },
    )
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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add differentiation claims
        token["is_staff"] = bool(user.is_staff)
        token["is_superuser"] = bool(user.is_superuser)
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Rebuild access token to include custom claims
        refresh = self.token_class(attrs["refresh"])  # type: ignore[attr-defined]
        access = refresh.access_token
        try:
            user_id = refresh.payload[jwt_api_settings.USER_ID_CLAIM]
        except Exception:
            # If payload missing claim, just return original data
            return data
        User = get_user_model()
        try:
            user = User.objects.get(**{jwt_api_settings.USER_ID_FIELD: user_id})
        except User.DoesNotExist:
            return data
        access["is_staff"] = bool(user.is_staff)
        access["is_superuser"] = bool(user.is_superuser)
        data["access"] = str(access)
        return data


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Sign up",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, example="john_doe"),
                "email": openapi.Schema(type=openapi.TYPE_STRING, example="john@example.com"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, example="Password123!"),
            },
        ),
        responses={
            201: openapi.Response(
                description="Created",
                examples={
                    "application/json": {
                        "user": {
                            "id": 7,
                            "username": "john_doe",
                            "email": "john@example.com"
                        },
                        "refresh": "<refresh_token>",
                        "access": "<access_token>"
                    }
                },
            )
        },
    )
    def post(self, request: Request) -> Response:
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Generate JWT tokens using the same SimpleJWT mechanism
        refresh = RefreshToken.for_user(user)
        # Inject claims into access token so clients can differentiate roles
        access = refresh.access_token
        access["is_staff"] = bool(user.is_staff)
        access["is_superuser"] = bool(user.is_superuser)
        data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "refresh": str(refresh),
            "access": str(access),
        }
        return Response(data, status=status.HTTP_201_CREATED)
