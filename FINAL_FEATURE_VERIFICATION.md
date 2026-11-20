# Final Feature Verification (Phase 10)

Legend: **PASS** = executed here and passed · **PARTIAL** = part verified · **NOT TESTED** · **BLOCKED** · **NOT PRESENT** = the feature does not exist in the code.
Evidence "RT" = `tests/test_full_regression.py`; "PT" = `tests/test_payments.py`; "ST" = `tests/test_security_basics.py`; "B" = real-browser run. All backend tests ran on SQLite **and** on a local PostgreSQL 16.

## Student (1–22)
| # | Item | Status | Evidence / note |
|---|---|---|---|
| 1 | Registration | PASS | RT, ST (duplicate + weak password rejected) |
| 2 | Login | PASS | RT; B (UI login) |
| 3 | Logout | PASS (API) | no-token access refused (RT). Stateless JWT: logout is client-side; the UI button was not clicked in a browser |
| 4 | Profile editing | PASS | RT (city/state/about/gender/photo) |
| 5 | Domain listing | PASS | RT: exactly the 10 domains |
| 6 | Domain selection | PASS | RT detail + apply; B (card opens detail) |
| 7 | Plan selection | PASS | RT: 1/2/3 months give 20/40/60 tasks; invalid plan refused |
| 8 | Enrollment | PASS | RT incl. duplicate refused |
| 9 | Enrollment approval | PASS | RT |
| 10 | Daily task display | PASS | RT: only first task open; cannot skip ahead; next opens after submit |
| 11 | Task submission | PASS | RT |
| 12 | GitHub link | PASS | RT; `javascript:` URLs never stored |
| 13 | Demo link | PASS | RT |
| 14 | Notes | PASS | RT |
| 15 | Screenshot upload | PASS (local storage) | RT; type/size validation ST. Cloud storage not tested |
| 16 | Progress tracking | PASS | RT |
| 17 | Notifications | PASS in-app / NOT TESTED push delivery | RT; push needs VAPID keys + device |
| 18 | Offer letter | PASS | RT; other students refused |
| 19 | Certificate generation | PASS | RT after payment; ID format `UPN-CERT-YYYY-NNNNN` |
| 20 | Certificate PDF view/download | **PARTIAL** | The certificate is a printable HTML page ("Print / Save as PDF" in the browser). The server does not generate a PDF file. Browser print dialog not tested |
| 21 | **Certificate ID verification** | **NOT PRESENT** | No public verify route or UI exists anywhere in the code (earlier checklists mislabelled payment verification). Not built: IDs are sequential, so a public lookup would let anyone enumerate student names. Needs a design decision (unguessable ID/token). The privacy policy no longer claims it |
| 22 | Account deletion request | PASS | in-app + public page + purge of associated data (4 tests; B) |

## Admin (23–33)
| # | Item | Status | Evidence |
|---|---|---|---|
| 23 | Admin login | PASS | RT; B |
| 24 | Admin authorization | PASS | ST: students/anonymous/forged/expired tokens refused; JWT `role` claim not trusted |
| 25 | Student management | PASS | RT (list, detail, edit, deactivate/reactivate) |
| 26 | Enrollment approval | PASS | RT |
| 27 | Domain management | PASS | RT create/edit/unpublish/delete; delete **blocked** when paid certificates exist (new safeguard) |
| 28 | Task management | PASS | RT add/edit/reorder/delete |
| 29 | Submission review | PASS | RT approve/rework/invalid status |
| 30 | Certificate management | PARTIAL | Admin Certificate tab renders without errors (B); fee/payment settings tested (RT); certificate-template editing endpoints were not exercised |
| 31 | Messaging | PASS | RT announce to all / one user; students cannot send |
| 32 | Notification management | PASS | RT |
| 33 | Payment verification | PASS | PT (UPI review once; gateway payments immutable) |

## Payments (34–39)
| # | Item | Status | Evidence |
|---|---|---|---|
| 34 | Order creation (mock) | PASS | PT |
| 35 | Signature verification | PASS | PT (valid, bad, wrong secret, non-ASCII, cross-student) |
| 36 | Webhook verification | PASS | PT (signature, size, secret unset, dedupe, amount/currency) |
| 37 | Duplicate protection | PASS | PT (replay, duplicate event, duplicate UTR, double payment flagged, concurrency race ×8) |
| 38 | Failed payment handling | PASS | PT (order stays open for retry) |
| 39 | Refund logic review | PASS (logic) / NOT TESTED live | PT partial/full refund; refunds are made in the Razorpay dashboard |

## Technical (40–55)
| # | Item | Status | Evidence |
|---|---|---|---|
| 40 | FastAPI startup | PASS | started under uvicorn and via TestClient lifespan |
| 41 | Frontend loading | PASS | B: 135 + 54 page loads, 0 errors |
| 42 | API health check | PASS | `/api/health` added; ST (ok + DB failure → 503 without details) |
| 43 | Database connectivity | PASS | SQLite and local PostgreSQL 16 |
| 44 | PostgreSQL configuration review | **PARTIAL** | Full suite passes on PostgreSQL 16; DB URL scheme normalisation added (`postgres://` used to crash). **Your production database/URL was not verified** |
| 45 | Upload validation | PASS | ST (HTML/SVG/non-image refused, oversize 413, auth required) |
| 46 | Cloud storage integration | **NOT TESTED** | no credentials. Production refuses to start with local storage (existing guard). Deletion of cloud files not implemented |
| 47 | CORS | PASS | ST |
| 48 | Authentication and authorization | PASS | ST, RT |
| 49 | Rate limiting | PASS with caveat | login, register and payment endpoints limited (ST/PT). In-memory per process; keyed on `X-Forwarded-For` |
| 50 | Mobile responsiveness | PASS | B: 5 viewports; see FRONTEND_TEST_REPORT.md |
| 51 | PWA manifest | PASS | tests + B |
| 52 | Service worker | PASS | B: registers, activates, offline start URL returns 200 |
| 53 | TWA configuration | PASS (config) / not built | generated, tested; never compiled |
| 54 | Digital Asset Links | PASS (endpoint) / **NOT configured, NOT verified live** | needs your signing fingerprints and a deployment |
| 55 | Android build configuration | PARTIAL / **BLOCKED** (build) | targetSdk 36, versions, no secrets verified; SDK unreachable here |
