# File Storage Architecture

## Goal
Provide secure, persistent, and provider-agnostic file storage for the Upnivo application while preserving local development and avoiding destructive production changes.

## Architecture
The app currently uses a layered pattern:

1. Frontend sends a base64 image payload to the API.
2. `main.py` validates MIME type, file size, and content.
3. The backend chooses a storage backend:
   - local file system (`UPLOAD_STORAGE_PROVIDER=local`)
   - S3-compatible object storage (`UPLOAD_STORAGE_PROVIDER=s3`)
   - Cloudinary image uploads (`UPLOAD_STORAGE_PROVIDER=cloudinary`)
4. The app returns a public URL for the saved asset.
5. The URL is stored in the database for later display: `User.photo`, `Internship.image`, `Task.image`, `Submission.image`, and settings such as signature URLs.

## Local flow
- The image is saved under `uploads/` in the project directory.
- The URL is exposed through `/uploads/{filename}`.
- This is suitable for safe dev testing and local debugging, but not durable for Render ephemeral storage.

## S3-compatible flow
- The app uploads to the configured bucket and optionally uses `UPLOAD_PUBLIC_BASE_URL` or `AWS_S3_PUBLIC_URL`.
- This is suitable for Render or other managed infrastructure with persisted object storage.
- Credentials come from environment variables and are never committed to source control.

## Cloudinary flow
- The app uploads the image to the configured Cloudinary folder using the environment credentials.
- This is suitable for image-heavy use cases and fits the current app's feature set.
- The Cloudinary configuration is turned on via environment variables only.

## Safety rules implemented
- Randomized filenames only.
- File extensions are restricted to allowed image types.
- File size is bounded by `UPLOAD_MAX_BYTES`.
- `clean_url()` rejects suspicious paths like `/uploads/../...`.
- Local dev remains isolated; the app does not place real student payloads into production storage.

## Known limitations
- This project is still a local app and does not include a live bucket account or a production deployment in this environment.
- No real student data or production database was used during storage validation.
- Cloud storage should be fully validated with real credentials before deployment.
