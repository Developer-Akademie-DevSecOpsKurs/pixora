# Instaclone

A full-stack Instagram clone built with Angular 21 and Django 6, featuring photo sharing, follows, likes, and comments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quickstart](#quickstart)
- [Usage](#usage)

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [pnpm](https://pnpm.io/installation) (for local frontend development without Docker)
- [Python 3.12+](https://www.python.org/) (for local backend development without Docker)

## Quickstart

1. **Clone the repository and enter the project directory**

2. **Create a `.env` file** in the project root based on the example:

   ```bash
   cp backend/.env.example backend/.env
   ```

   Edit `backend/.env` and set a strong `SECRET_KEY`.

3. **Start all services with Docker Compose:**

   ```bash
   docker-compose up --build
   ```

4. **Seed the database with sample data** (optional):

   ```bash
   docker-compose exec backend python manage.py seed_db
   ```

5. **Create a superuser** for the Django admin:

   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

## Usage

| Service    | URL                          |
|------------|------------------------------|
| Frontend   | http://localhost:4200        |
| Backend API| http://localhost:8000/api    |
| Django Admin| http://localhost:8000/admin |
| PostgreSQL | localhost:5432               |

### API Overview

| Method | Endpoint                          | Description              |
|--------|-----------------------------------|--------------------------|
| POST   | `/api/auth/register/`             | Register a new user      |
| POST   | `/api/auth/login/`                | Obtain JWT tokens        |
| POST   | `/api/auth/refresh/`              | Refresh access token     |
| GET    | `/api/users/me/`                  | Current user profile     |
| GET    | `/api/users/{id}/`                | User profile             |
| POST   | `/api/users/{id}/follow/`         | Follow a user            |
| POST   | `/api/users/{id}/unfollow/`       | Unfollow a user          |
| GET    | `/api/posts/`                     | Feed (followed users)    |
| POST   | `/api/posts/`                     | Create a post            |
| DELETE | `/api/posts/{id}/`                | Delete own post          |
| POST   | `/api/posts/{id}/like/`           | Like a post              |
| POST   | `/api/posts/{id}/unlike/`         | Unlike a post            |
| POST   | `/api/posts/{id}/comments/`       | Add a comment            |
| DELETE | `/api/comments/{id}/`             | Delete own comment       |

### Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit as needed
python manage.py migrate
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
pnpm install
pnpm start
```
