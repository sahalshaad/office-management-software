# OfficeFlow

OfficeFlow is a Django office attendance and task management platform with geo-fenced punch-in/out, staff management, tasks, leave approvals, real-time notifications, analytics, exports, PWA support, and Docker deployment.

## Features

- Role-based access for Super Admin, HR/Admin, and Staff Employee
- Session login plus JWT API authentication
- Email verification and password reset plumbing
- GPS radius attendance with IP/device logging, duplicate prevention, timestamp audit, optional selfie capture, and attendance attempt logs
- Staff, department, task, leave, notification, performance, and office settings modules
- REST APIs with pagination, filtering, search, and ordering
- Django Channels WebSockets for live notifications and attendance updates
- CSV, Excel, and PDF attendance exports
- Dark mode, responsive Bootstrap 5 dashboard UI, Chart.js analytics, and PWA install support
- Docker, Gunicorn, Nginx, PostgreSQL, and Redis configuration

## Local Setup

```bashh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Demo accounts created by `seed_demo`:

- Admin: `admin@officeflow.local` / `OfficeFlow123!`
- Staff: `staff@officeflow.local` / `OfficeFlow123!`

## Docker Deployment

```bash
cp .env.example .env
docker compose up --build
```

Set production values in `.env`, point DNS at the server, and terminate TLS at a reverse proxy or load balancer. For direct TLS in Nginx, add certificates and redirect port 80 to 443.

## Geo-Fence Configuration

Create or edit office locations in `Attendance > Office Settings` or Django Admin. Attendance is accepted only when browser GPS coordinates are within the configured radius and GPS accuracy is acceptable.

## Useful Commands

```bash
python manage.py createsuperuser
python manage.py seed_demo
python manage.py collectstatic
python manage.py test
```

## API Documentation

See [docs/API.md](docs/API.md).

## Architecture & Deployment

- [Architecture](docs/ARCHITECTURE.md)
- [Deployment guide](docs/DEPLOYMENT.md)
