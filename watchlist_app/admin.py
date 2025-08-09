from __future__ import annotations

from django.contrib import admin

from watchlist_app.models import Genre, Movie, Rating, Review, StreamingPlatform, Watchlist, WatchlistItem


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "release_date", "is_active", "created_at")
    list_filter = ("is_active", "release_date")
    search_fields = ("title",)


@admin.register(StreamingPlatform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "website", "is_active")
    search_fields = ("name",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")
    search_fields = ("name",)


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "is_active")
    search_fields = ("name",)


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ("id", "watchlist", "movie", "is_active")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "movie", "title", "is_active")
    search_fields = ("title", "body")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "movie", "score", "is_active")
    list_filter = ("score",)

