# Cloud Storage Setup Guide

## Allowed providers
- Cloudinary for images
- S3-compatible storage for general file/object storage
- Local uploads for development only

## Local development
Use the defaults in `.env.example`:

```env
UPLOAD_STORAGE_PROVIDER=local
UPLOAD_DIR=uploads
UPLOAD_MAX_BYTES=4000000
```

This keeps local testing easy without touching production systems.

## Cloudinary setup
Set these environment variables in a local `.env` file or deployment environment:

```env
UPLOAD_STORAGE_PROVIDER=cloudinary
CLOUDINARY_CLOUD_NAME=replace-with-cloud-name
CLOUDINARY_API_KEY=replace-with-api-key
CLOUDINARY_API_SECRET=replace-with-api-secret
CLOUDINARY_FOLDER=uploads
UPLOAD_PUBLIC_BASE_URL=https://res.cloudinary.com/your-cloud-name
```

Notes:
- Do not commit actual secrets.
- Use temporary sandbox credentials only.
- Validate image uploads with sample files only.

## S3-compatible setup
```env
UPLOAD_STORAGE_PROVIDER=s3
AWS_S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=replace-with-access-key
AWS_SECRET_ACCESS_KEY=replace-with-secret-key
AWS_REGION=us-east-1
AWS_S3_ENDPOINT_URL=https://s3.example.com
AWS_S3_PUBLIC_URL=https://your-public-url.example.com
UPLOAD_PUBLIC_BASE_URL=https://your-public-url.example.com
```

Notes:
- Keep the bucket private unless public access is explicitly required.
- Use IAM credentials with narrow object-write permissions.
- Do not deploy or activate paid services during validation.

## Render-ready guidance
- Use a persistent object store, not local disk for uploaded files.
- Configure environment variables at the Render service level, not in source control.
- Validate uploads with sample images only and never with real student data.
