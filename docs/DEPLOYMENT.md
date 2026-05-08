# OfficeFlow Deployment Guide

## Docker

```bash
cp .env.example .env
docker compose up --build
```

The stack includes:

- Django + Gunicorn web container
- PostgreSQL 16
- Redis for Channels
- Nginx reverse proxy
- Persistent volumes for PostgreSQL, static files, and media uploads

## Production Checklist

- Set a strong `DJANGO_SECRET_KEY`
- Set `DJANGO_DEBUG=False`
- Configure `DJANGO_ALLOWED_HOSTS`
- Configure `DJANGO_CSRF_TRUSTED_ORIGINS`
- Use real SMTP credentials for password reset and verification email
- Enable secure cookie and HSTS settings from `.env.example`
- Put TLS in front of Nginx or extend `docker/nginx/default.conf` with certificates
- Create the first admin with `python manage.py createsuperuser`
- Configure at least one active office location before staff punch attendance

## Post-Deploy Commands

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py createsuperuser
```

For demo data:

```bash
docker compose exec web python manage.py seed_demo
```
