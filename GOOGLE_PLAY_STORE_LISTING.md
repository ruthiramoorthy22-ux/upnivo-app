# Google Play Store Listing (draft)

Every field marked **[YOU]** needs a real value from you. Nothing below was invented: no email, phone, address, company name or legal claim.

## Basics
| Field | Draft |
|---|---|
| App name (≤30 chars) | **Upnivo** (store title); in-app name "UPNIVO INTERN" |
| Package | com.upnivo.app |
| Category recommendation | **Education** |
| Tags (suggested) | Education, Career, Learning |
| Default language | English (India) |
| Contact email (public, required) | **[YOU]** |
| Website | https://upnivo-intern.onrender.com (or your custom domain) |
| Phone | **[YOU]** (optional/depends on account type) |
| Developer name / address | **[YOU]** as registered with Google (shown publicly for some account types) |
| Privacy Policy URL (required) | `https://upnivo-intern.onrender.com/privacy` |
| Account deletion URL | `https://upnivo-intern.onrender.com/delete-account-request` |

## Short description (≤80 characters)
`Virtual internships with daily tasks, review and certificates.` (62 chars)

## Full description (≤4000 characters)
```
Upnivo is a virtual internship platform for students. Choose a domain, pick a 1, 2 or 3 month plan, and build real work through structured daily tasks.

DOMAINS
• Full Stack Development • Python Development • Java Development
• AI / Machine Learning • UI/UX Design • Cyber Security
• Data Analytics • Digital Marketing • Mobile App Development
• Cloud & DevOps

HOW IT WORKS
1. Create your account and choose an internship domain and plan (20, 40 or 60 tasks).
2. Your enrollment is reviewed and you receive an offer letter in the app.
3. Complete one task at a time. Share a GitHub link, a demo link, notes and screenshots.
4. The Upnivo team reviews your work and may ask for improvements.
5. Finish all tasks to unlock your certificate of completion.

FEATURES
• Daily task roadmap with progress tracking
• Submit GitHub links, demo links, notes and screenshots
• Feedback from reviewers on every submission
• Notifications for approvals, feedback and updates
• Offer letter and certificate you can view and print or save as PDF
• Manage or delete your account and data at any time inside the app

PRICING
Enrolling is free. A certificate fee applies when you finish the program; the amount is shown in the app before you pay.

Your privacy: we do not run ads, and we do not collect your location or contacts.
```
(≈1,300 characters. **Do not add** claims such as "recognised by companies", "job guarantee" or "verified certificates" unless they are true; the code has no public certificate verification.) Revise the PRICING paragraph to match whatever billing route you choose.

## Feature list (for "What's new" / promo)
Daily tasks · Progress tracking · Reviewer feedback · Offer letters · Certificates · Push notifications · Delete-account control

## Graphic assets
| Asset | Requirement (verify in Play Console) | Status |
|---|---|---|
| App icon | 512×512 PNG | `static/icon-512.png` is 512×512 (checked). Play applies its own mask: keep as is. |
| Feature graphic | 1024×500 PNG/JPG | **Draft generated** in `play_store_assets/feature_graphic_1024x500.png` from your logo and tagline. Replace if you want a designed one. |
| Phone screenshots | 2–8 images, 16:9 or 9:16, each side 320–3840 px | **6 generated** at 1080×1920 in `play_store_assets/screenshots/` from the real app running on fictional demo data. Re-take from the production app for the final listing. |
| Tablet screenshots | optional (needed for tablet featuring) | not generated |
| Promo video | optional | none |

## App access instructions (Play Console → App content)
See GOOGLE_PLAY_REVIEWER_ACCESS_GUIDE.md.

## Content rating
Complete the IARC questionnaire yourself. Facts to answer truthfully: no violence, no user-to-user chat, no user-visible UGC sharing between users, no gambling, no ads, in-app payment for a digital certificate.

## Target audience
Decide deliberately. Current policy text says 16+. Choose the age groups accordingly; selecting under-13 triggers the Families policy, which this app is not built for.
