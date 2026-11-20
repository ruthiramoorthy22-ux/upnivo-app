# UPNIVO INTERN
```
pip install -r requirements.txt
export ADMIN_PASSWORD='YourStrongPassword'   # creates admin@yourdomain.com as admin on first start
export SECRET_KEY='long-random-string'
uvicorn main:app --reload
```
Student app: http://localhost:8000/   Admin: http://localhost:8000/admin   API docs: /docs

## Flow
1. Student registers -> admin gets a notification (with all student details in Admin > Students).
2. Student enrolls in an internship -> admin gets a notification (Admin > Enrollments).
3. Admin clicks **Send offer letter** (chooses start date) -> student is notified, a printable offer letter is generated and the internship **unlocks**.
4. From the start date, one task is released per working day (Mon-Fri). Student submits link/notes.
5. Admin reviews in Admin > Submissions (Approve / Needs rework + feedback) -> student is notified.

Program content (roadmap, roles, tools, capstone, daily tasks for Full Stack, Python, AI/ML, Java, UI/UX, Cyber Security) lives in `programs.py`.
It is added automatically on startup, including to an existing `upnivo.db` (new columns are migrated automatically).
Set `TZ_OFFSET_MIN` (default 330 = IST) to change when daily tasks are released.
PostgreSQL: set DATABASE_URL (see .env.example). Android: wrap with Capacitor later.

## Version 2 additions
- 1 / 2 / 3 month plans for every domain (20 / 40 / 60 tasks). Student picks the plan while enrolling.
- Tasks open one by one: submitting a task opens the next one (after the offer letter + start date).
- Certificate unlocks after all tasks are submitted and is paid via UPI: student pays, enters the UTR number, admin verifies in Admin > Payments.
  Set the fee and your UPI ID in Admin > Settings (or env CERT_FEE, UPI_ID, UPI_NAME).
- Admin can edit internships, tasks (text, steps, image, study link, order), students, and review submissions.
- Images (task images, profile photos, screenshots) are saved in the `uploads/` folder (UPLOAD_DIR to change). On hosts with temporary disks, attach a persistent disk or uploaded images are lost on redeploy.
- Offer letter and certificate use `static/signature.png` (replace this file to change the signature).

## Razorpay (optional)
1. Razorpay Dashboard > Account & Settings > API Keys > Generate **Test** Key.
2. Set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` (env vars or `.env`), then restart the server.
3. Optional webhook: Dashboard > Webhooks > URL `https://YOUR-DOMAIN/api/razorpay-webhook`, events `payment.captured` and `order.paid`, set a secret and put it in `RAZORPAY_WEBHOOK_SECRET`.
4. For real money, complete Razorpay KYC and replace the test keys with live keys.
Without the keys the app uses manual UPI + admin verification.
Run with a .env file: `uvicorn main:app --reload --env-file .env`

## Offer letter (admin)
Admin > Offer Letter: edit the common wording, terms, signer name/designation, footer and upload a signature, then Preview and Save.
Admin > Enrollments (or Dashboard) > Send offer letter: choose the start date, add an optional personal note, Preview, then Send.
A letter keeps the wording it was sent with; "Edit / resend offer" re-sends it with the current wording.
Tasks: Admin > Internships > Tasks > Edit (text, steps, image, study link, order).

## Version 3 additions
- 4 new domains with 1/2/3 month plans (20/40/60 tasks each): Data Analytics, Digital Marketing, Mobile App (Flutter), Cloud DevOps. Added automatically on first start (existing database is kept).
- Every domain has a picture (`static/covers/*.svg`). Admin > Domains & Tasks > **Photo** / **Edit** uploads your own picture.
- Admin app redesigned: colourful, animated, mobile bottom-nav. Tabs: Dashboard, Students, Enrollments, Offer Letter Model, Certificate Model, Domains & Tasks, Submissions, Payments, Payment Details.
- Certificate model is editable (title, paragraph, signer, signature, footer) with Preview. Your signature is in `static/signature.png` and used on offer letters and certificates.
- Enrollments > **Send payment details** notifies the student with the certificate fee and UPI ID.
- Tasks without a detailed explanation now show a clear "Goal / How to do it / What to submit" guide.

## Version 3.1
- Admin login: admin@yourdomain.com (password in `.env` ADMIN_PASSWORD). Logging in on the student page opens /admin.
- Android: installable PWA (manifest.webmanifest, sw.js, icons). Open the deployed HTTPS site in Chrome > Install app. For a Play Store APK use PWABuilder.com.
- Info pages: Terms, Privacy, Refund, Help/FAQ, About & Team (#info/terms etc.). Register needs agreement to Terms and Privacy.

## Version 3.2
- Task submission has separate fields: GitHub link, Demo video link, other link, notes, screenshot (links are validated). Admin sees them as buttons.
- Admin > Send Message: send information / new update / comment to all students, one domain or one student.
- Notifications: in-app alerts + sound; phone push notifications when VAPID keys are set (run `python gen_vapid.py`, paste into .env, `pip install -r requirements.txt`).
- "New update available" banner appears automatically when a new version is deployed.
- Click sound + vibration (can be turned off in Profile). Gzip + caching for faster loading.
