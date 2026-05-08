# OfficeFlow API

Base path: `/api/`

Authentication:

- Session authentication for browser UI requests
- JWT via `/api/auth/token/` and `/api/auth/token/refresh/`
- Send JWT requests as `Authorization: Bearer <access_token>`

## Accounts

- `GET /api/accounts/staff/`
- `POST /api/accounts/staff/`
- `GET /api/accounts/staff/me/`
- `PATCH /api/accounts/staff/me/`
- `GET /api/accounts/departments/`

## Attendance

- `GET /api/attendance/offices/`
- `POST /api/attendance/records/punch-in/`
- `POST /api/attendance/records/punch-out/`
- `GET /api/attendance/records/`
- `PATCH /api/attendance/records/{id}/correct/`
- `GET /api/attendance/records/stats/`
- `GET /api/attendance/attempts/`

Punch payload:

```json
{
  "latitude": 12.9715987,
  "longitude": 77.5945627,
  "accuracy_m": 18.5,
  "selfie_data": "data:image/jpeg;base64,..."
}
```

## Tasks

- `GET /api/tasks/items/`
- `POST /api/tasks/items/`
- `PATCH /api/tasks/items/{id}/progress/`
- `POST /api/tasks/items/{id}/comments/`
- `POST /api/tasks/items/{id}/attachments/`

## Leave

- `GET /api/leaves/requests/`
- `POST /api/leaves/requests/`
- `POST /api/leaves/requests/{id}/review/`
- `GET /api/leaves/balances/`

## Notifications

- `GET /api/notifications/`
- `POST /api/notifications/`
- `POST /api/notifications/{id}/mark-read/`
- `POST /api/notifications/mark-all-read/`
- `GET /api/notifications/unread-count/`

WebSocket: `/ws/officeflow/`

## Reports

- `GET /api/reports/summary/productivity/`
- `GET /api/reports/performance/`
- `GET /reports/attendance.csv`
- `GET /reports/attendance.xlsx`
- `GET /reports/attendance.pdf`
