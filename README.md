# Videoflix Backend

A Netflix-inspired video streaming backend built with Django REST Framework.
Videos are automatically converted to HLS format using FFMPEG in the background,
enabling adaptive streaming in 480p, 720p and 1080p.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 6.0 + Django REST Framework |
| Database | PostgreSQL |
| Cache / Queue | Redis + Django RQ |
| Video Processing | FFMPEG (HLS conversion) |
| Authentication | JWT via HttpOnly Cookies |
| Email | SMTP (Mailtrap for development) |
| Static Files | Whitenoise |
| Server | Gunicorn |
| Containerization | Docker + Docker Compose |

---

## Features

- Email-based registration with account activation via tokenised link
- JWT authentication stored in HttpOnly cookies (XSS-protected)
- Refresh token rotation with blacklisting
- Password reset via email
- Automatic HLS video conversion in three resolutions (480p / 720p / 1080p)
- Automatic thumbnail generation via FFMPEG
- Video dashboard with genre grouping
- Background task processing via Redis Queue
- Redis caching layer
- Full test suite (27 tests) following TDD methodology

---

## Project Structure

```
videoflix-backend/
├── core/                   # Django settings and root URLs
├── users/                  # Authentication app
│   ├── models.py           # CustomUser (email-based login)
│   ├── managers.py         # CustomUserManager
│   ├── authentication.py   # CookieJWTAuthentication
│   ├── serializers.py      # Register, User, PasswordReset serializers
│   ├── views.py            # All auth views
│   ├── urls.py             # Auth endpoints
│   └── utils.py            # Cookie helpers and email functions
├── videos/                 # Video app
│   ├── models.py           # Video model with hls_ready flag
│   ├── serializers.py      # VideoSerializer with absolute thumbnail URL
│   ├── views.py            # VideoListView, HLSManifestView, HLSSegmentView
│   ├── urls.py             # Video endpoints
│   ├── signals.py          # post_save → RQ task
│   ├── tasks.py            # FFMPEG HLS conversion (480p/720p/1080p)
│   ├── utils.py            # HLS path helper functions
│   └── apps.py             # Signal registration
├── tests/
│   ├── base.py             # VideoflixTestCase, UserFactory, InactiveUserFactory
│   ├── users/              # Auth tests (16)
│   └── videos/             # Video tests (11)
├── templates/emails/       # HTML email templates (activation, password reset)
├── backend.Dockerfile      # Official Akademie Dockerfile
├── docker-compose.yml      # Official Akademie Docker Compose
├── backend.entrypoint.sh   # DB health check, migrations, superuser, gunicorn
├── requirements.txt
├── .env.template           # Environment variable template
└── .gitignore
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/register/` | No | Register new user |
| GET | `/api/activate/<uid>/<token>/` | No | Activate account via email link |
| POST | `/api/login/` | No | Login and receive JWT cookies |
| POST | `/api/logout/` | Yes | Logout and blacklist refresh token |
| POST | `/api/token/refresh/` | Cookie | Refresh access token |
| POST | `/api/password_reset/` | No | Request password reset email |
| POST | `/api/password_confirm/<uid>/<token>/` | No | Set new password |
| GET | `/api/video/` | Yes | List all videos |
| GET | `/api/video/<id>/<res>/index.m3u8` | Yes | HLS manifest file |
| GET | `/api/video/<id>/<res>/<segment>/` | Yes | HLS video segment |

---

## Getting Started

### Prerequisites

- Docker Desktop installed and running
- Git installed

### Setup

**1. Clone the repository:**

```bash
git clone <your-repo-url>
cd videoflix-backend
```

**2. Create your `.env` file from the template:**

```bash
cp .env.template .env
```

**3. Fill in the required values in `.env`:**

```env
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=your-secure-password
DJANGO_SUPERUSER_EMAIL=admin@example.com

SECRET_KEY=your-very-secret-django-key

DB_NAME=videoflix
DB_USER=videoflix_user
DB_PASSWORD=your-db-password

EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_HOST_USER=your-mailtrap-user
EMAIL_HOST_PASSWORD=your-mailtrap-password
```

**4. Start the project:**

```bash
docker-compose up --build
```

The backend is now running at `http://localhost:8000`.

On first start, the entrypoint automatically:
- Waits for PostgreSQL to be ready
- Runs all migrations
- Creates the superuser from `.env`
- Starts the RQ worker for background tasks
- Starts Gunicorn

---

## Admin Panel

```
URL:      http://localhost:8000/admin/
Email:    value of DJANGO_SUPERUSER_EMAIL in .env
Password: value of DJANGO_SUPERUSER_PASSWORD in .env
```

---

## Running Tests

Docker must be running before executing tests.

```bash
# Run all 27 tests
docker-compose exec web python manage.py test tests --verbosity=2

# Run only auth tests
docker-compose exec web python manage.py test tests.users --verbosity=2

# Run only video tests
docker-compose exec web python manage.py test tests.videos --verbosity=2
```

---

## Migrations

```bash
# Create new migrations after model changes
docker-compose exec web python manage.py makemigrations

# Migrations run automatically on container start via entrypoint
```

---

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `DJANGO_SUPERUSER_USERNAME` | Admin username | Yes |
| `DJANGO_SUPERUSER_PASSWORD` | Admin password | Yes |
| `DJANGO_SUPERUSER_EMAIL` | Admin email | Yes |
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (True/False) | No |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | No |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins | No |
| `DB_NAME` | PostgreSQL database name | Yes |
| `DB_USER` | PostgreSQL user | Yes |
| `DB_PASSWORD` | PostgreSQL password | Yes |
| `DB_HOST` | PostgreSQL host (default: db) | No |
| `DB_PORT` | PostgreSQL port (default: 5432) | No |
| `REDIS_HOST` | Redis host (default: redis) | No |
| `REDIS_LOCATION` | Redis location URL | No |
| `REDIS_PORT` | Redis port (default: 6379) | No |
| `EMAIL_HOST` | SMTP server host | Yes |
| `EMAIL_PORT` | SMTP server port | No |
| `EMAIL_HOST_USER` | SMTP username | Yes |
| `EMAIL_HOST_PASSWORD` | SMTP password | Yes |
| `EMAIL_USE_TLS` | Use TLS (default: True) | No |
| `DEFAULT_FROM_EMAIL` | Sender email address | No |
| `FRONTEND_URL` | Frontend base URL for email links | No |

---

## HLS Video Processing

When a video is uploaded via the Django Admin:

```
Upload → post_save signal → Redis Queue → RQ Worker
    → FFMPEG generates 480p / 720p / 1080p HLS segments
    → FFMPEG extracts thumbnail at 1s mark
    → hls_ready = True
    → Video available for streaming
```

HLS files are stored in:
```
media/videos/<video_id>/480p/
media/videos/<video_id>/720p/
media/videos/<video_id>/1080p/
media/videos/thumbnails/
```

---

## Authentication Flow

```
Register → Activation email → Activate account
    → Login → JWT in HttpOnly cookies
        → Access token (30min) + Refresh token (7 days)
            → Auto-refresh via /api/token/refresh/
                → Logout → Token blacklisted
```

---

## Notes

- The `.env` file is excluded from version control via `.gitignore`
- Docker files (`backend.Dockerfile`, `docker-compose.yml`, `backend.entrypoint.sh`) are provided by Developer Akademie and must not be modified
- All videos are stored in Docker volumes, not locally
- Mailtrap is recommended for development email testing
