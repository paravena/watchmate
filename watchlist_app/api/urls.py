from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from watchlist_app.api.views import GenreViewSet, MovieViewSet, PlatformViewSet, ReviewViewSet, WatchlistViewSet

router = DefaultRouter()
router.register(r"movies", MovieViewSet, basename="movie")
router.register(r"platforms", PlatformViewSet, basename="platform")
router.register(r"genres", GenreViewSet, basename="genre")
router.register(r"watchlists", WatchlistViewSet, basename="watchlist")
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),
]
