# Account Deletion Audit

## Scope
This review covered the in-app deletion route, public deletion page, backend endpoint, student profile/auth flow, privacy UI, and database data model related to personal data and deletion behavior.

## Verified implementation

### 1. In-app student deletion
- `POST /api/me/delete` requires an authenticated student token.
- The route rejects admin accounts.
- It verifies the current password before anonymizing the user record.
- It disables the account and clears profile fields.
- It sets `deletion_status = "completed"` and `deleted_at` for audit clarity.

### 2. Public self-service deletion page
- `/delete-account-request` returns `static/delete-account-request.html`.
- The page requires the email and password that match the account and submits to `/api/account-delete-request`.
- This page is public but still requires the correct password for ownership verification.

### 3. Public backend deletion route
- `POST /api/account-delete-request` verifies that the email exists and the password matches.
- It rejects inactive or deleted accounts.
- It does not allow one user to delete another user’s account because it checks the exact email match and current password.

### 4. Auth and ownership protection
- `Depends(current)` enforces JWT authentication for in-app deletion.
- The public route verifies the specific account email and password for the matching record.
- Only the active record for that email is modified.

## Data reviewed
The following personal data is stored by the app:
- `users`: name, email, phone, college, degree, department, year, city, state, gender, about, photo, password hash, role, status
- `applications`: student enrollment and internship status
- `submissions`: task work, notes, URLs, screenshots, feedback
- `payments`: certificate payment status and UTR details
- `notifications`: app alerts and related metadata
- `audit_logs`: operational history
- uploaded assets under `uploads/` and external storage URLs

## Risk observations
- A student’s `User` row is anonymized on deletion, which is a good safety measure.
- Associated records such as applications, payment entries, and submissions remain for audit and verification purposes and are not automatically removed in the current design.
- This prevents data loss in certificate verification and avoids breaking legal/payment records.

## Result
- PASS: in-app deletion route exists and checks password
- PASS: public deletion route exists and verifies ownership
- PASS: non-owner deletion is blocked by matching account identity
- PASS: frontend deletion instructions exist in the app profile and on the public page
- BLOCKED: no bulk admin deletion workflow was added, by design
- NOT TESTED: real external storage provider with live credentials
