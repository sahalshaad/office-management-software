# OfficeFlow Architecture

## Django Apps

- `accounts`: custom user model, roles, departments, profile management, staff CRUD, login audits, email verification
- `attendance`: office geo-fence settings, attendance records, attempt logs, GPS validation, punch services
- `tasks`: task assignment, comments, attachments, progress tracking
- `leaves`: leave requests, review workflow, balances
- `notifications`: announcements, read state, WebSocket consumer
- `reports`: exports and performance logs
- `core`: shared models, permissions, middleware, dashboard, utilities, seed command

## Primary Tables

- `accounts_user`
- `accounts_department`
- `attendance_officelocation`
- `attendance_attendance`
- `attendance_attendanceattempt`
- `tasks_task`
- `tasks_taskcomment`
- `tasks_taskattachment`
- `leaves_leaverequest`
- `leaves_leavebalance`
- `notifications_notification`
- `reports_performancelog`

## Role Model

- `super_admin`: full platform access
- `hr_admin`: administrative access to staff, attendance, task, leave, notification, and report workflows
- `staff`: self-service attendance, assigned tasks, leave requests, notifications, and personal analytics

## Attendance Flow

1. Browser requests high-accuracy GPS.
2. Optional camera selfie is captured as a base64 image.
3. Client posts coordinates, GPS accuracy, and selfie to `/api/attendance/records/punch-in/` or `/punch-out/`.
4. Server calculates distance using the Haversine formula.
5. Attendance is accepted only within active office radius and acceptable GPS accuracy.
6. Server logs timestamp, IP, browser/device user agent, distance, and failed attempts.
7. Admin dashboards receive live attendance events over WebSocket.

## Realtime Flow

Clients connect to `/ws/officeflow/`. The authenticated user is subscribed to `user_{id}`. Admin users also join the `attendance` group for live punch events.
