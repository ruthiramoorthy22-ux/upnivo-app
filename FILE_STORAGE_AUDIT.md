# File Storage Audit

## Scope
The Phase 4 review inspected the app's current file-handling flow, upload APIs, screenshot uploads, certificate-related assets, and the persistent storage setup used by the FastAPI app.

## Current upload locations
1. `POST /api/upload` in `main.py` for image uploads from the student/admin frontend.
2. Student submission screenshots and task evidence are saved using the `Submission.image` field and local upload URL values.
3. Internship and task cover images are stored via the `Internship.image` and `Task.image` fields.
4. User profile photos are stored in the `users.photo` field and validated through `clean_url`.
5. Static certificate/offers rely on the app's existing `static/` directory, including `static/signature.png`.
6. Local dev storage is served by `app.mount("/uploads", StaticFiles(directory=str(UPLOADS)))`.

## Storage configuration observed
- Local dev default: `UPLOAD_STORAGE_PROVIDER=local`
- Local storage directory: `UPLOAD_DIR=uploads`
- S3 integration: optional via `AWS_S3_BUCKET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- External object-store integration was not actively wired into the app's working storage flow for all public upload paths and was effectively only partially implemented.

## Security review
- The app already generated random file names in local mode and used `uuid.uuid4().hex`.
- The original implementation still needed stronger validation across storage providers, explicit path sanitization, and consistent handling for remote URLs and S3/Cloudinary integration.
- `clean_url()` required stricter path traversal blocking and remote URL validation.
- `persist_upload()` required provider-aware handling and safe environment configuration for production.

## Findings
- Local uploads were working for development but not robust enough for managed hosting with ephemeral disks.
- Cloud-backed persistence was optional and not fully integrated with all upload flows.
- Image uploads were not yet strongly normalized across all provider types.
- No production `Render` deployment, cloud bucket, or live payment service was used in this phase.

## Status
- PASS: local dev storage remains functional
- BLOCKED: deployment to Render or a live cloud storage provider is not executed in this environment
- NEEDS REVIEW: real Cloudinary or S3 credentials and bucket setup for production deployment
