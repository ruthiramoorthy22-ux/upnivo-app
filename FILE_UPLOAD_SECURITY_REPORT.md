# File Upload Security Report

## Summary
The upload path has been hardened to prevent unsafe file handling, path traversal, and provider misconfiguration. The app still remains compatible with local development and does not alter production data.

## Positive findings
- Randomized local filenames are used for uploaded files.
- File types are restricted to approved image MIME values.
- File sizes are capped at `UPLOAD_MAX_BYTES`.
- `clean_url()` rejects path traversal patterns such as `../` and blocks malformed URLs.
- Production mode now blocks the local storage backend unless a provider is explicitly configured.
- The S3 and Cloudinary integrations are configured through environment variables only.

## Remaining issues to monitor
- Real deployment still needs a working bucket or Cloudinary project with credentials.
- Local `uploads/` remains appropriate only for development use.
- File validation should be expanded if non-image content or additional document types are added later.
- The app still uses a deprecated FastAPI startup event; this is not a file storage issue but is a future modernization item.

## Result
- PASS: local upload validation tested
- PASS: malicious path strings rejected
- PASS: temporary test image upload accepted
- BLOCKED: real cloud upload verification requires external provider credentials and a deployment environment
