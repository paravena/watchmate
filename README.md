# Watchmate API

A Django REST Framework API for a streaming platform watchlist system (Django 4.2 LTS).

## Features
- Movies CRUD with genres and platforms
- JWT authentication (SimpleJWT)
- Watchlists with add/remove/bulk add
- Reviews and Ratings (1-5)
- Filtering, search, pagination
- Swagger and Redoc documentation
- CORS, Postgres-ready, soft deletes

## Quickstart (Local, SQLite)
1. Create virtualenv and install deps:
   - `python -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`
   - Ensure Django 4.2.x is installed: `python -c "import django,sys; sys.exit(0 if django.__version__.startswith('4.2') else 1)" && echo 'Django 4.2 LTS detected'`
2. Run migrations and seed sample data (optional):
   - `python manage.py migrate`
   - `python manage.py seed` (idempotent; creates sample users, genres, platforms, movies, watchlists, ratings, reviews)
   - `python manage.py createsuperuser` (optional)
   - `python manage.py runserver`
3. Open Swagger: http://127.0.0.1:8000/swagger/

## Quickstart with Postgres via Docker
1. Copy env: `cp .env.example .env` and adjust as needed.
2. Start DB: `docker compose up -d`
3. Export env for Django: `export $(grep -v '^#' .env | xargs)`
4. Install deps and migrate as above.
5. Seed sample data (optional): `python manage.py seed`
   - To reset previously seeded data first: `python manage.py seed --reset`

## Auth Endpoints
- `POST /api/auth/token/` obtain token (username, password)
- `POST /api/auth/token/refresh/`
- `POST /api/auth/token/verify/`

## API Endpoints
- `GET/POST /api/movies/` (rate: `POST /api/movies/{id}/rate/`)
- `GET/POST /api/platforms/`
- `GET/POST /api/genres/`
- `GET/POST /api/reviews/`
- `GET/POST /api/watchlists/` (add/remove/bulk: `/api/watchlists/{id}/add-item/`, `/remove-item/`, `/bulk-add/`)

Use Bearer token in Authorization header for write actions.

## Notes
- Pagination: page, page_size via query params
- Filtering: django-filter on common fields (e.g., `?genres=1&platforms=2`)
- Search: DRF SearchFilter on selected fields (e.g., `?search=matrix`)

## Sample Seeded Data
If you run `python manage.py seed`, the following demo users are created:
- username: `alice`, password: `password123`
- username: `bob`, password: `password123`

It also creates a handful of genres, platforms, movies (with relationships), default watchlists per user, a few reviews, and ratings.
To re-run from a clean state without wiping your whole DB, use: `python manage.py seed --reset`.

## Development
- Linting/type hints recommended via mypy/ruff (not included).
- Tests skeleton may be added under `watchlist_app/tests.py`.
