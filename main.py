import os, threading, secrets, io, re, uuid, json, hmac, base64, html, urllib.request, urllib.error, datetime as dt, jwt
from pathlib import Path
from urllib.parse import quote
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, Response, RedirectResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, ForeignKey, UniqueConstraint, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from argon2 import PasswordHasher
from programs import PROGRAMS, METHOD, PLAN_LABEL
try:
    import qrcode, qrcode.image.svg
except Exception:
    qrcode = None

DB = os.getenv("DATABASE_URL", "sqlite:///./upnivo.db")
SECRET = os.getenv("SECRET_KEY", "dev-secret-change-me")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "skillforgelearning22@gmail.com").lower()
TZ_MIN = int(os.getenv("TZ_OFFSET_MIN", "330"))  # IST by default
UPLOADS = Path(os.getenv("UPLOAD_DIR", "uploads")); UPLOADS.mkdir(parents=True, exist_ok=True)
engine = create_engine(DB, connect_args={"check_same_thread": False} if DB.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
ph = PasswordHasher()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120)); email = Column(String(200), unique=True, index=True)
    mobile = Column(String(20)); college = Column(String(200)); degree = Column(String(100))
    department = Column(String(100)); year = Column(String(20)); about = Column(Text, default="")
    city = Column(String(80), default=""); state = Column(String(80), default=""); country = Column(String(80), default="India")
    gender = Column(String(20), default=""); pw = Column(String(300)); photo = Column(String(200), default="")
    role = Column(String(10), default="student"); active = Column(Boolean, default=True)
    created = Column(DateTime, default=dt.datetime.utcnow)

class Internship(Base):
    __tablename__ = "internships"
    id = Column(Integer, primary_key=True)
    title = Column(String(200)); org = Column(String(200), default="UPNIVO INTERN")
    category = Column(String(80)); duration = Column(String(50)); mode = Column(String(20), default="Online")
    skills = Column(Text, default=""); description = Column(Text, default=""); outcomes = Column(Text, default="")
    eligibility = Column(Text, default=""); published = Column(Boolean, default=True)
    is_sample = Column(Boolean, default=False)
    method = Column(Text, default=""); roles = Column(Text, default=""); tools = Column(Text, default="")
    final = Column(Text, default=""); roadmap = Column(Text, default="")
    image = Column(String(300), default="")
    plans = Column(String(20), default="1,2,3")  # durations (months) students can choose from

class Task(Base):  # one task per day of a plan (internship + months)
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    internship_id = Column(Integer, ForeignKey("internships.id"), index=True)
    months = Column(Integer); day = Column(Integer); theme = Column(String(120), default="")
    title = Column(Text); submit = Column(Text, default=""); brief = Column(Text, default="")
    image = Column(String(300), default=""); resource = Column(String(400), default="")

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("user_id", "internship_id"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id")); internship_id = Column(Integer, ForeignKey("internships.id"))
    months = Column(Integer)
    status = Column(String(20), default="Pending"); note = Column(Text, default="")  # Pending | Under Review | Approved | Offer Sent | Rejected
    created = Column(DateTime, default=dt.datetime.utcnow)
    offer_date = Column(DateTime); offer_ref = Column(String(40)); start_date = Column(String(12))
    offer_note = Column(Text, default=""); offer_snap = Column(Text, default="")

class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (UniqueConstraint("application_id", "task_id"),)
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), index=True); task_id = Column(Integer, ForeignKey("tasks.id"))
    link = Column(Text, default=""); notes = Column(Text, default=""); image = Column(String(300), default="")
    github = Column(String(500), default=""); video = Column(String(500), default="")
    status = Column(String(20), default="Submitted")  # Submitted | Approved | Rework
    feedback = Column(Text, default=""); created = Column(DateTime, default=dt.datetime.utcnow)

class Payment(Base):  # certificate payment (UPI, verified by admin)
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("applications.id"), index=True); amount = Column(Integer, default=0)
    utr = Column(String(60)); status = Column(String(12), default="Pending")  # Pending | Paid | Rejected
    note = Column(Text, default=""); created = Column(DateTime, default=dt.datetime.utcnow)

class Setting(Base):
    __tablename__ = "settings"
    key = Column(String(40), primary_key=True); value = Column(Text, default="")

class PushSub(Base):
    __tablename__ = "push_subs"
    id = Column(Integer, primary_key=True); user_id = Column(Integer, index=True)
    endpoint = Column(String(600), unique=True); p256dh = Column(String(200)); auth = Column(String(100))
    created = Column(DateTime, default=dt.datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True); to_admin = Column(Boolean, default=False)
    title = Column(String(200)); body = Column(Text, default=""); link = Column(String(100), default="")
    read = Column(Boolean, default=False); created = Column(DateTime, default=dt.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True); actor = Column(String(200)); action = Column(String(300))
    created = Column(DateTime, default=dt.datetime.utcnow)

Base.metadata.create_all(engine)

def migrate():  # adds new columns to a database created by an older version
    insp = inspect(engine)
    want = {"users": {"photo": "VARCHAR(200)"},
            "internships": {"method": "TEXT", "roles": "TEXT", "tools": "TEXT", "final": "TEXT", "roadmap": "TEXT", "plans": "VARCHAR(20)", "image": "VARCHAR(300)"},
            "applications": {"offer_date": "TIMESTAMP", "offer_ref": "VARCHAR(40)", "start_date": "VARCHAR(12)", "months": "INTEGER", "offer_note": "TEXT", "offer_snap": "TEXT"},
            "tasks": {"months": "INTEGER", "theme": "VARCHAR(120)", "brief": "TEXT", "image": "VARCHAR(300)", "resource": "VARCHAR(400)"},
            "submissions": {"image": "VARCHAR(300)", "github": "VARCHAR(500)", "video": "VARCHAR(500)"}}
    with engine.begin() as c:
        for t, cols in want.items():
            have = {x["name"] for x in insp.get_columns(t)}
            for n, ty in cols.items():
                if n not in have: c.execute(text(f"ALTER TABLE {t} ADD COLUMN {n} {ty}"))
migrate()
from fastapi.middleware.gzip import GZipMiddleware
app = FastAPI(title="UPNIVO INTERN API")
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=800)  # smaller downloads = faster app
@app.middleware("http")
async def cache_static(request, call_next):
    r = await call_next(request)
    p = request.url.path
    if p.startswith("/static/covers") or p.startswith("/uploads") or p.endswith((".png", ".svg")): r.headers["Cache-Control"] = "public, max-age=86400"
    elif p.startswith("/api/"): r.headers["Cache-Control"] = "no-store"
    return r

def db():
    s = SessionLocal()
    try: yield s
    finally: s.close()

def token(u): return jwt.encode({"sub": str(u.id), "role": u.role, "exp": dt.datetime.utcnow() + dt.timedelta(days=7)}, SECRET, "HS256")
def current(authorization: str = Header(None), s: Session = Depends(db)):
    try: data = jwt.decode((authorization or "").replace("Bearer ", ""), SECRET, ["HS256"])
    except Exception: raise HTTPException(401, "Please login")
    u = s.get(User, int(data["sub"]))  # role is read from DB, never trusted from the token
    if not u or not u.active: raise HTTPException(403, "Account disabled")
    return u
def admin(u: User = Depends(current)):
    if u.role != "admin": raise HTTPException(403, "Admin only")
    return u

def log(s, who, what): s.add(AuditLog(actor=who, action=what)); s.commit()
def today(): return (dt.datetime.utcnow() + dt.timedelta(minutes=TZ_MIN)).date()
def task_date(start, d):  # working day number d (1-based) counted from start (used for the offer-letter end date)
    x, n = start, 0
    while True:
        if x.weekday() < 5:
            n += 1
            if n == d: return x
        x += dt.timedelta(days=1)
def next_monday():
    t = today(); return t + dt.timedelta(days=(7 - t.weekday()) % 7 or 7)
VAPID_PUB, VAPID_PRIV = os.getenv("VAPID_PUBLIC_KEY", ""), os.getenv("VAPID_PRIVATE_KEY", "")
try: from pywebpush import webpush, WebPushException
except Exception: webpush = None
def _push_send(subs, payload):  # runs in a background thread so the app stays fast
    for ep, k1, k2 in subs:
        try: webpush(subscription_info={"endpoint": ep, "keys": {"p256dh": k1, "auth": k2}}, data=json.dumps(payload), vapid_private_key=VAPID_PRIV, vapid_claims={"sub": "mailto:" + (os.getenv("ADMIN_EMAIL") or "skillforgelearning22@gmail.com")})
        except Exception as e:
            if "410" in str(e) or "404" in str(e):
                d = SessionLocal()
                try: d.query(PushSub).filter_by(endpoint=ep).delete(); d.commit()
                finally: d.close()
def notify(s, title, body="", user_id=None, admin_=False, link=""):
    s.add(Notification(user_id=user_id, to_admin=admin_, title=title, body=body, link=link))
    if not (webpush and VAPID_PRIV): return
    if admin_: ids = [x.id for x in s.query(User).filter_by(role="admin")]
    else: ids = [user_id]
    subs = [(p.endpoint, p.p256dh, p.auth) for p in s.query(PushSub).filter(PushSub.user_id.in_(ids))] if ids else []
    if subs: threading.Thread(target=_push_send, args=(subs, {"title": title, "body": body[:160], "link": link}), daemon=True).start()

# ---------- settings, uploads ----------
DEFAULTS = {"cert_fee": os.getenv("CERT_FEE", "199"), "upi_id": os.getenv("UPI_ID", ""), "upi_name": os.getenv("UPI_NAME", "UPNIVO INTERN")}
def setting(s, k): r = s.get(Setting, k); return r.value if r else DEFAULTS[k]
def fee(s):
    try: return max(0, int(float(setting(s, "cert_fee"))))
    except ValueError: return 0
RZP_KEY, RZP_SECRET, RZP_WH = os.getenv("RAZORPAY_KEY_ID", ""), os.getenv("RAZORPAY_KEY_SECRET", ""), os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
def rzp_on(): return bool(RZP_KEY and RZP_SECRET)
def rzp_request(path, payload):  # plain HTTPS call to Razorpay (no extra library needed)
    auth = base64.b64encode(f"{RZP_KEY}:{RZP_SECRET}".encode()).decode()
    req = urllib.request.Request("https://api.razorpay.com/v1" + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", "Authorization": "Basic " + auth})
    try: return json.loads(urllib.request.urlopen(req, timeout=20).read())
    except urllib.error.HTTPError as e: raise HTTPException(502, "Razorpay error: " + e.read().decode()[:200])
    except Exception: raise HTTPException(502, "Could not reach Razorpay")
def rzp_sig_ok(msg, sig, secret): return bool(secret) and hmac.compare_digest(hmac.new(secret.encode(), msg.encode(), "sha256").hexdigest(), sig or "")
TPL_DEFAULTS = {
    "offer_intro": "Congratulations! We are delighted to offer you an internship with UPNIVO INTERN as a {internship} Intern. After reviewing your enrollment, we believe you will learn and contribute well in this programme.",
    "offer_terms": "Submit only your own original work and follow the code of conduct.\nKeep platform and project information confidential unless told otherwise.\nUPNIVO INTERN may end the internship in case of long inactivity or misconduct.",
    "offer_closing": "We wish you great learning ahead. Welcome aboard!",
    "signer_name": "", "signer_title": "Authorised Signatory", "signature": "/static/signature.png",
    "offer_footer": "Issued digitally by the UPNIVO INTERN platform",
    "cert_heading": "Internship Certificate", "cert_sub": "CERTIFICATE OF COMPLETION",
    "cert_body": "has successfully completed the {plan} {internship} internship at UPNIVO INTERN by completing all {tasks} assigned tasks with dedication and quality.",
    "cert_footer": "This certificate can be verified with the Certificate ID by UPNIVO INTERN."}
DEFAULTS.update(TPL_DEFAULTS)
def tpl(s): return {k: setting(s, k) for k in TPL_DEFAULTS}
EXT = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp", "image/gif": "gif"}
def save_image(data):
    m = re.match(r"data:(image/[a-z+]+);base64,(.+)$", data or "", re.S)
    if not m or m.group(1) not in EXT: raise HTTPException(400, "Upload a PNG, JPG, WEBP or GIF image")
    raw = base64.b64decode(m.group(2))
    if len(raw) > 4_000_000: raise HTTPException(413, "Image is too large (max 4 MB)")
    name = f"{uuid.uuid4().hex}.{EXT[m.group(1)]}"; (UPLOADS / name).write_bytes(raw); return "/uploads/" + name
def clean_url(u):
    u = (u or "").strip(); return u if re.match(r"^(/uploads/[\w.-]+|https?://\S+)$", u) else ""

COVER = {"Full Stack": "full-stack", "Python": "python", "Java": "java", "AI/ML": "ai-ml", "UI/UX": "ui-ux", "Cyber Security": "cyber-security",
         "Data Analytics": "data-analytics", "Digital Marketing": "digital-marketing", "Mobile App": "mobile-app", "Cloud DevOps": "cloud-devops"}
def irow(i): return {**row(i), "cover": i.image or f"/static/covers/{COVER.get(i.category, 'full-stack')}.svg"}
NEW_DOMAINS = [("Data Analytics with Excel, SQL & Power BI", "Data Analytics"), ("Digital Marketing & SEO", "Digital Marketing"),
               ("Mobile App Development with Flutter", "Mobile App"), ("Cloud Computing & DevOps", "Cloud DevOps")]
# ---------- programs ----------
def plans_of(i): return [int(x) for x in (i.plans or "1,2,3").split(",") if x.strip().isdigit()]
def plan_tasks(s, iid, m): return s.query(Task).filter_by(internship_id=iid, months=m).order_by(Task.day).all()

def seed_program(s, i):  # fills program details + tasks for every plan from programs.py (only where empty)
    p = PROGRAMS.get(i.category)
    if not p: return
    if not i.roles: i.roles = "\n".join(p["roles"])
    if not i.tools: i.tools = p["tools"]
    if not i.final: i.final = p["final"]
    if not i.method: i.method = "\n".join(METHOD)
    if not i.plans: i.plans = "1,2,3"
    for m in (1, 2, 3):
        if s.query(Task).filter_by(internship_id=i.id, months=m).count(): continue
        d = 0
        for wi in p["plans"][m]:
            theme, items = p["weeks"][wi]
            for it in items:
                d += 1; t, _, sub = it.partition(" | ")
                s.add(Task(internship_id=i.id, months=m, day=d, theme=theme, title=t, submit=sub))

def fix_legacy(s):  # upgrade data from the older version (tasks/applications without a plan)
    for i in s.query(Internship).all():
        old = s.query(Task).filter(Task.internship_id == i.id, Task.months.is_(None)).all()
        if old:
            m = max(1, min(3, round(len(old) / 20))); p = PROGRAMS.get(i.category)
            for t in old:
                t.months = m; w = (t.day - 1) // 5
                if p and w < len(p["plans"][m]): t.theme = p["weeks"][p["plans"][m][w]][0]
    s.flush()
    for a in s.query(Application).filter(Application.months.is_(None)).all():
        i = s.get(Internship, a.internship_id); ms = plans_of(i); dg = re.search(r"\d+", i.duration or "")
        n = int(dg.group()) if dg else 0; a.months = n if n in ms else (ms[0] if ms else 1)
    s.commit()

@app.on_event("startup")
def bootstrap():
    s = SessionLocal()
    pw = os.getenv("ADMIN_PASSWORD") or "ruthira227227"  # change in .env for production
    adm_u = s.query(User).filter_by(email=ADMIN_EMAIL).first()
    if not adm_u:
        s.add(User(name="Administrator", email=ADMIN_EMAIL, pw=ph.hash(pw), role="admin")); s.commit()
    else:  # keep the admin account in sync with the configured password and role
        try: ph.verify(adm_u.pw, pw)
        except Exception: adm_u.pw = ph.hash(pw)
        adm_u.role = "admin"; s.commit()
    if s.query(Internship).count() == 0:
        for t, c in [("Full Stack Web Development (MERN)", "Full Stack"), ("Python Development", "Python"), ("Artificial Intelligence & Machine Learning", "AI/ML"),
                     ("Core Java Programming", "Java"), ("UI/UX Design", "UI/UX"), ("Cyber Security Basics", "Cyber Security")] + NEW_DOMAINS:
            s.add(Internship(title=t, category=c, duration="1 / 2 / 3 months", is_sample=True, skills=c + ", Projects, Git",
                             description=f"Practical {t} internship with real-world projects, step-by-step daily tasks and mentor feedback. Choose a 1, 2 or 3 month plan.",
                             outcomes="Build real projects\nLearn industry tools\nEarn a certificate", eligibility="Any UG/PG student"))
        s.commit()
    if not s.get(Setting, "domains_v3"):  # one-time: add the 4 new domains to an existing database
        for t, c in NEW_DOMAINS:
            if not s.query(Internship).filter_by(category=c).first():
                s.add(Internship(title=t, category=c, duration="1 / 2 / 3 months", skills=c + ", Projects, Daily tasks",
                                 description=f"Practical {t} internship with real-world projects, clear step-by-step daily tasks and mentor feedback. Choose a 1, 2 or 3 month plan.",
                                 outcomes="Build real projects\nLearn industry tools\nEarn a certificate", eligibility="Any UG/PG student"))
        s.add(Setting(key="domains_v3", value="1")); s.commit()
    fix_legacy(s)
    for i in s.query(Internship).all(): seed_program(s, i)
    s.commit(); s.close()

class Reg(BaseModel):
    name: str; email: str; mobile: str; college: str; degree: str; department: str; year: str; password: str
class Login(BaseModel): email: str; password: str
class Intern(BaseModel):
    title: str; org: str = "UPNIVO INTERN"; category: str; duration: str = ""; mode: str = "Online"
    skills: str = ""; description: str = ""; outcomes: str = ""; eligibility: str = ""; published: bool = True
    method: str = ""; roles: str = ""; tools: str = ""; final: str = ""; roadmap: str = ""; plans: str = "1,2,3"; image: str = ""
class Prof(BaseModel):
    mobile: str = None; college: str = None; degree: str = None; department: str = None; year: str = None
    about: str = None; city: str = None; state: str = None; country: str = None; gender: str = None; photo: str = None
class StuEdit(BaseModel):
    name: str = None; mobile: str = None; college: str = None; degree: str = None; department: str = None; year: str = None
    about: str = None; city: str = None; state: str = None; country: str = None; gender: str = None
class Review(BaseModel): status: str; note: str = ""
class Offer(BaseModel): start_date: str; note: str = ""
class Enroll(BaseModel): months: int = 0
class Sub(BaseModel): link: str = ""; notes: str = ""; image: str = ""; github: str = ""; video: str = ""
class Announce(BaseModel): title: str; body: str = ""; internship_id: int = 0; user_id: int = 0; link: str = ""
class SubReview(BaseModel): status: str; feedback: str = ""
class TaskIn(BaseModel): title: str; submit: str = ""; brief: str = ""; image: str = ""; resource: str = ""; theme: str = ""; months: int = 0
class Upload(BaseModel): data: str
class Pay(BaseModel): utr: str
class PayReview(BaseModel): status: str; note: str = ""
class Settings(BaseModel):
    cert_fee: str = None; upi_id: str = None; upi_name: str = None; offer_intro: str = None; offer_terms: str = None; offer_closing: str = None
    signer_name: str = None; signer_title: str = None; signature: str = None; offer_footer: str = None
    cert_heading: str = None; cert_sub: str = None; cert_body: str = None; cert_footer: str = None

def row(o): return {c.name: getattr(o, c.name) for c in o.__table__.columns if c.name != "pw"}

# ---------------- auth ----------------
@app.post("/api/register")
def register(r: Reg, s: Session = Depends(db)):
    e = r.email.strip().lower()
    if "@" not in e or len(r.password) < 8: raise HTTPException(400, "Valid email and password (min 8 chars) required")
    if s.query(User).filter_by(email=e).first(): raise HTTPException(409, "Email already registered")
    u = User(name=r.name.strip(), email=e, mobile=r.mobile, college=r.college, degree=r.degree, department=r.department, year=r.year, pw=ph.hash(r.password))
    s.add(u); s.flush()
    notify(s, "New student registered", f"{u.name} · {u.college} · {u.email}", admin_=True, link="students")
    s.commit(); return {"token": token(u), "user": row(u)}

def do_login(l, s, need_admin):
    u = s.query(User).filter_by(email=l.email.strip().lower()).first()
    try: ph.verify(u.pw, l.password)
    except Exception: raise HTTPException(401, "Invalid email or password")
    if need_admin and u.role != "admin": raise HTTPException(403, "Not an administrator")
    if not u.active: raise HTTPException(403, "Account suspended")
    return {"token": token(u), "user": row(u)}

@app.post("/api/login")
def login(l: Login, s: Session = Depends(db)): return do_login(l, s, False)
@app.post("/api/admin/login")
def alogin(l: Login, s: Session = Depends(db)): return do_login(l, s, True)
@app.get("/api/me")
def me(u: User = Depends(current)): return row(u)
@app.put("/api/me")
def upd(p: Prof, u: User = Depends(current), s: Session = Depends(db)):
    d = p.dict(exclude_none=True)
    if "photo" in d: d["photo"] = clean_url(d["photo"])
    for k, v in d.items(): setattr(u, k, v)  # name/email deliberately not editable
    s.commit(); return row(u)
class PushIn(BaseModel): endpoint: str; p256dh: str; auth: str
@app.get("/api/push-key")
def push_key(): return {"key": VAPID_PUB if (webpush and VAPID_PRIV) else ""}
@app.post("/api/push/subscribe")
def push_sub(b: PushIn, u: User = Depends(current), s: Session = Depends(db)):
    p = s.query(PushSub).filter_by(endpoint=b.endpoint).first()
    if not p: p = PushSub(endpoint=b.endpoint); s.add(p)
    p.user_id, p.p256dh, p.auth = u.id, b.p256dh, b.auth; s.commit(); return {"ok": True}
@app.post("/api/admin/announce")
def announce(b: Announce, a: User = Depends(admin), s: Session = Depends(db)):  # admin message / new update / information to students
    if not b.title.strip(): raise HTTPException(400, "Write a title")
    if b.user_id: ids = [b.user_id]
    elif b.internship_id: ids = list({x.user_id for x in s.query(Application).filter_by(internship_id=b.internship_id)})
    else: ids = [x.id for x in s.query(User).filter_by(role="student", active=True)]
    for uid in ids: notify(s, b.title.strip()[:190], b.body.strip()[:1500], user_id=uid, link=b.link[:100])
    s.commit(); log(s, a.email, f"Announcement '{b.title[:60]}' sent to {len(ids)} student(s)"); return {"sent": len(ids)}

class DelAcc(BaseModel): password: str
@app.post("/api/me/delete")
def delete_me(b: DelAcc, u: User = Depends(current), s: Session = Depends(db)):  # Play Store requires in-app account deletion
    if u.role == "admin": raise HTTPException(400, "Admin account cannot be deleted here")
    try: ph.verify(u.pw, b.password)
    except Exception: raise HTTPException(401, "Wrong password")
    u.name, u.email, u.mobile, u.college, u.degree, u.department, u.year = "Deleted user", f"deleted{u.id}@deleted.invalid", "", "", "", "", ""
    u.about = u.city = u.state = u.gender = u.photo = ""; u.pw = ph.hash(secrets.token_hex(16)); u.active = False
    s.commit(); log(s, "system", f"Account {u.id} deleted by the user"); return {"ok": True}

@app.post("/api/upload")
def upload(b: Upload, u: User = Depends(current)): return {"url": save_image(b.data)}

# ---------------- catalogue ----------------
def weeks_of(ts):
    weeks = []
    for t in ts:
        w = (t.day - 1) // 5
        while len(weeks) <= w: weeks.append({"theme": "", "days": []})
        if not weeks[w]["theme"]: weeks[w]["theme"] = t.theme or f"Week {w + 1}"
        weeks[w]["days"].append({"day": t.day, "title": t.title})
    return weeks

@app.get("/api/internships")
def internships(q: str = "", category: str = "", s: Session = Depends(db)):
    qs = s.query(Internship).filter_by(published=True)
    if category: qs = qs.filter(Internship.category == category)
    out = []
    for i in qs.all():
        if q.lower() in f"{i.title} {i.org} {i.category} {i.skills}".lower():
            pl = {str(m): s.query(Task).filter_by(internship_id=i.id, months=m).count() for m in plans_of(i)}
            out.append({**irow(i), "applicants": s.query(Application).filter_by(internship_id=i.id).count(), "plan_days": pl})
    return out

@app.get("/api/internships/{iid}")
def one(iid: int, s: Session = Depends(db)):
    i = s.get(Internship, iid)
    if not i or not i.published: raise HTTPException(404, "Not found")
    plans = {}
    for m in plans_of(i):
        ts = plan_tasks(s, iid, m); plans[str(m)] = {"days": len(ts), "label": PLAN_LABEL.get(m, ""), "weeks": weeks_of(ts)}
    return {**irow(i), "applicants": s.query(Application).filter_by(internship_id=iid).count(), "plans": plans}

# ---------------- student: enroll, offer, tasks ----------------
def plan_total(s, a): return s.query(Task).filter_by(internship_id=a.internship_id, months=a.months).count()
def counts(s, a):
    q = s.query(Submission).filter_by(application_id=a.id)
    return plan_total(s, a), q.filter_by(status="Approved").count(), q.count()

@app.post("/api/internships/{iid}/apply")
def apply(iid: int, b: Enroll, u: User = Depends(current), s: Session = Depends(db)):
    if u.role != "student": raise HTTPException(403, "Students only")
    i = s.get(Internship, iid)
    if not i or not i.published: raise HTTPException(404, "Not found")
    ms = plans_of(i); m = b.months or (ms[0] if ms else 1)
    if m not in ms: raise HTTPException(400, "Choose a valid duration")
    if s.query(Application).filter_by(user_id=u.id, internship_id=iid).first(): raise HTTPException(409, "You already enrolled")
    a = Application(user_id=u.id, internship_id=iid, months=m); s.add(a); s.flush()
    notify(s, "New enrollment", f"{u.name} ({u.college}) enrolled in {i.title} · {m} month plan", admin_=True, link="enrollments")
    s.commit(); return {"ok": True, "id": a.id}

@app.get("/api/applications")
def mine(u: User = Depends(current), s: Session = Depends(db)):
    out = []
    for a in s.query(Application).filter_by(user_id=u.id).order_by(Application.id.desc()):
        i = s.get(Internship, a.internship_id); total, done, sub = counts(s, a)
        out.append({**row(a), "title": i.title, "category": i.category, "unlocked": a.status == "Offer Sent", "total": total, "approved": done, "submitted": sub})
    return out

def own_app(s, u, aid, need_offer=False):
    a = s.get(Application, aid)
    if not a or a.user_id != u.id: raise HTTPException(404, "Not found")
    if need_offer and a.status != "Offer Sent": raise HTTPException(403, "Locked: your internship unlocks after the admin sends your offer letter")
    return a

def task_states(s, a):  # a task opens only when every task before it has been submitted
    ok = dt.date.fromisoformat(a.start_date) <= today()
    subs = {x.task_id: x for x in s.query(Submission).filter_by(application_id=a.id)}
    out = []
    for t in plan_tasks(s, a.internship_id, a.months):
        x = subs.get(t.id)
        if x: st = {"Approved": "approved", "Rework": "rework"}.get(x.status, "submitted")
        else: st = "open" if ok else "locked"; ok = False
        out.append({"id": t.id, "day": t.day, "week": (t.day - 1) // 5 + 1, "theme": t.theme, "title": t.title, "submit": t.submit, "brief": t.brief or default_brief(t),
                    "image": t.image, "resource": t.resource, "state": st, "link": x.link if x else "", "github": x.github if x else "", "video": x.video if x else "", "notes": x.notes if x else "",
                    "sub_image": x.image if x else "", "feedback": x.feedback if x else ""})
    return out
def default_brief(t):  # shown when the admin has not written a detailed explanation
    return (f"GOAL FOR TODAY\n{t.title}.\n\nHOW TO DO IT\n1. Read the goal above and note what is new for you.\n2. Watch the tutorial or read about it (buttons below).\n"
            f"3. Do it yourself on your computer. Type or build it; do not copy-paste.\n4. Save proof of your work.\n\nWHAT TO SUBMIT\n{t.submit or 'A link or a short note about your work'}.")
def is_complete(st): return bool(st) and all(x["state"] in ("submitted", "approved") for x in st)

def cert_info(s, a, st):
    done = is_complete(st); f = fee(s); p = s.query(Payment).filter(Payment.application_id == a.id, Payment.status != "Created").order_by(Payment.id.desc()).first()
    if not done: status = "locked"
    elif f <= 0 or (p and p.status == "Paid"): status = "paid"
    elif p and p.status == "Pending": status = "pending"
    elif p and p.status == "Rejected": status = "rejected"
    else: status = "payable"
    return {"status": status, "fee": f, "upi_id": setting(s, "upi_id"), "upi_name": setting(s, "upi_name"), "note": p.note if p and p.status == "Rejected" else "",
            "ref": f"UPN-CERT-{today().year}-{a.id:05d}", "gateway": "razorpay" if rzp_on() else "upi"}

@app.get("/api/applications/{aid}/tasks")
def tasks(aid: int, u: User = Depends(current), s: Session = Depends(db)):
    a = own_app(s, u, aid, True); st = task_states(s, a); i = s.get(Internship, a.internship_id)
    return {"title": i.title, "category": i.category, "months": a.months, "start_date": a.start_date, "started": dt.date.fromisoformat(a.start_date) <= today(),
            "offer_ref": a.offer_ref, "tasks": st, "cert": cert_info(s, a, st)}

@app.post("/api/applications/{aid}/tasks/{tid}/submit")
def submit(aid: int, tid: int, b: Sub, u: User = Depends(current), s: Session = Depends(db)):
    a = own_app(s, u, aid, True); st = task_states(s, a); cur = next((x for x in st if x["id"] == tid), None)
    if not cur: raise HTTPException(404, "Task not found")
    if cur["state"] == "locked":
        raise HTTPException(403, "Your internship has not started yet" if dt.date.fromisoformat(a.start_date) > today() else "Submit the previous task to unlock this one")
    if cur["state"] == "approved": raise HTTPException(409, "This task is already approved")
    gh, vd, ln = b.github.strip(), b.video.strip(), b.link.strip()
    for v, nm in ((gh, "GitHub link"), (vd, "Demo video link"), (ln, "Other link")):
        if v and not re.match(r"^https?://[^\s]+\.[^\s]+$", v): raise HTTPException(400, f"{nm} must start with https://")
    if gh and "github.com" not in gh.lower() and "gitlab.com" not in gh.lower() and "bitbucket.org" not in gh.lower(): raise HTTPException(400, "GitHub link must be a github.com (or gitlab.com) link")
    if not (gh or vd or ln or b.notes.strip() or b.image): raise HTTPException(400, "Add your GitHub link, demo video link, a screenshot or a short note")
    was = is_complete(st)
    x = s.query(Submission).filter_by(application_id=aid, task_id=tid).first()
    if not x: x = Submission(application_id=aid, task_id=tid); s.add(x)
    x.github, x.video = gh[:500], vd[:500]
    x.link, x.notes, x.image, x.status, x.created = ln[:500], b.notes.strip()[:2000], clean_url(b.image), "Submitted", dt.datetime.utcnow()
    s.flush()
    if not was and is_complete(task_states(s, a)):
        notify(s, "Internship completed 🎓", f"{u.name} finished all tasks of {s.get(Internship, a.internship_id).title}", admin_=True, link="submissions")
    s.commit(); return {"ok": True}

# ---------------- offer letter + certificate ----------------
DOC_CSS = """*{box-sizing:border-box}body{margin:0;background:#e9edf5;font-family:Georgia,'Times New Roman',serif;color:#14203f}
.bar{text-align:center;padding:14px}.bar button{font:700 14px system-ui;padding:11px 22px;border:0;border-radius:10px;background:#1a73e8;color:#fff;cursor:pointer}
.pg{position:relative;background:#fff;width:210mm;min-height:297mm;margin:0 auto 30px;padding:0 18mm 16mm;box-shadow:0 10px 40px #0a1a3f33;overflow:hidden}
.top{margin:0 -18mm;padding:18px 18mm;background:linear-gradient(120deg,#071433,#0d2260 60%,#1356c8);color:#fff;display:flex;align-items:center;gap:16px}
.top img{width:78px;mix-blend-mode:screen}.top h1{margin:0;font:800 24px system-ui;letter-spacing:.5px}.top small{font:12px system-ui;color:#9ec5ff;letter-spacing:2px}
.stripe{height:5px;margin:0 -18mm 22px;background:linear-gradient(90deg,#22d3ee,#1a73e8)}
.wm{position:absolute;left:50%;top:52%;width:420px;transform:translate(-50%,-50%);opacity:.05;filter:invert(1) hue-rotate(180deg);pointer-events:none}
h2{font:800 20px system-ui;color:#0a1a3f;margin:0 0 4px;letter-spacing:.3px}.meta{display:flex;justify-content:space-between;font:13px system-ui;color:#475569;margin:12px 0 18px;padding-bottom:10px;border-bottom:1px dashed #c5d3ee}
p{font-size:14.5px;line-height:1.7;margin:10px 0}table{width:100%;border-collapse:collapse;margin:14px 0;font:14px system-ui}td{padding:9px 14px;border:1px solid #d5e0f5}td:first-child{background:#f1f6ff;width:32%;font-weight:700;color:#1d3a78}
h3{font:700 14px system-ui;color:#1d3a78;margin:18px 0 6px;text-transform:uppercase;letter-spacing:1px}ol,ul{margin:4px 0;padding-left:22px}li{font-size:14px;line-height:1.65;margin:3px 0}
.sg{display:flex;justify-content:space-between;align-items:flex-end;margin-top:30px}.sg img{height:62px;display:block;mix-blend-mode:multiply}.sg .ln{border-top:1.5px solid #14203f;padding-top:5px;font:13px system-ui;min-width:210px}
.seal{width:104px;height:104px;border-radius:50%;border:3px double #1a73e8;color:#1a73e8;display:flex;flex-direction:column;align-items:center;justify-content:center;font:800 11px system-ui;text-align:center;transform:rotate(-12deg);letter-spacing:1px;line-height:1.5}
.ft{position:absolute;bottom:8mm;left:18mm;right:18mm;text-align:center;font:11px system-ui;color:#7b89a8;border-top:1px solid #e3e9f5;padding-top:7px}
.cert{width:297mm;min-height:210mm;padding:14mm 20mm;text-align:center;background:#fffdf6}.cert .bd{position:absolute;inset:7mm;border:3px solid #c9a227;outline:1px solid #c9a227;outline-offset:-9px}
.cert img.lg{width:120px;mix-blend-mode:multiply;margin-top:6px}.cert h1{font:700 40px Georgia,serif;color:#0a1a3f;letter-spacing:4px;margin:6px 0 0;text-transform:uppercase}.cert .sub{font:13px system-ui;letter-spacing:5px;color:#9a7b0c;margin-bottom:16px}
.cert .nm{font:italic 700 44px Georgia,serif;color:#1356c8;margin:10px 0;border-bottom:1.5px solid #c9a227;display:inline-block;padding:0 30px 4px}.cert p{font-size:16px}
@page{margin:0}@media print{body{background:#fff}.bar{display:none}.pg{box-shadow:none;margin:0}}"""
SEAL = '<div class="seal">UPNIVO<br>INTERN<br>OFFICIAL</div>'

def doc_user(s, u, aid):
    a = s.get(Application, aid)
    if not a or (u.role != "admin" and a.user_id != u.id): raise HTTPException(404, "Not found")
    return a, s.get(User, a.user_id), s.get(Internship, a.internship_id)

def sign_html(base, t):
    sg = t["signature"]; src = sg if sg.startswith("http") else base + sg; nm, tt = html.escape(t["signer_name"]), html.escape(t["signer_title"])
    return f'<img src="{src}"><div class="ln"><b>{nm or tt}</b><br>{tt + " · " if nm else ""}UPNIVO INTERN</div>'

def offer_html(base, t, d):  # t = letter template (text settings), d = details of this offer
    e = html.escape; f = lambda x: x.strftime("%d %B %Y")
    fill = lambda x: e(x).replace("{name}", e(d["name"])).replace("{internship}", e(d["internship"])).replace("{plan}", e(d["plan"])).replace("{start}", f(d["start"]))
    terms = "".join(f"<li>{fill(x)}</li>" for x in t["offer_terms"].split("\n") if x.strip())
    note = f'<p style="background:#f1f6ff;border-left:4px solid #1a73e8;padding:10px 14px;border-radius:6px">{fill(d["note"])}</p>' if d["note"].strip() else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Offer Letter - {e(d['name'])}</title><style>{DOC_CSS}</style></head><body>
<div class="bar"><button onclick="print()">Print / Save as PDF</button></div><div class="pg"><img class="wm" src="{base}/static/logo.png">
<div class="top"><img src="{base}/static/logo.png"><div><h1>UPNIVO INTERN</h1><small>LEARN · BUILD · GROW</small></div></div><div class="stripe"></div>
<h2>INTERNSHIP OFFER LETTER</h2><div class="meta"><span><b>Ref No:</b> {e(d['ref'])}</span><span><b>Date:</b> {f(d['date'])}</span></div>
<p>Dear <b>{e(d['name'])}</b>,<br><span style="font:13px system-ui;color:#475569">{e(d['college'])}</span></p><p>{fill(t['offer_intro'])}</p>{note}
<table><tr><td>Intern name</td><td>{e(d['name'])}</td></tr><tr><td>Internship</td><td>{e(d['internship'])}</td></tr><tr><td>Plan / Duration</td><td>{e(d['plan'])}</td></tr><tr><td>Total tasks</td><td>{d['n']} daily tasks</td></tr>
<tr><td>Mode</td><td>{e(d['mode'])}</td></tr><tr><td>Start date</td><td>{f(d['start'])}</td></tr><tr><td>Expected completion</td><td>{f(d['end'])} (working one task per day)</td></tr></table>
<h3>How your internship works</h3><ol><li>Log in to your UPNIVO INTERN account; your program is now unlocked.</li><li>Open the task of the day, read the steps and complete it.</li><li>Submit your work link or screenshot. The next task opens as soon as you submit.</li>
<li>Your mentor reviews your work and gives feedback. Fix any task marked for rework.</li><li>After completing all tasks you can unlock your Certificate of Completion.</li></ol>
<h3>Terms</h3><ul>{terms}</ul><p>{fill(t['offer_closing'])}</p>
<div class="sg"><div>{sign_html(base, t)}</div>{SEAL}</div><div class="ft">Offer Ref {e(d['ref'])} · {e(t['offer_footer'])}</div></div></body></html>"""

def offer_details(s, a, st, i, start, note, ref, date):
    n = plan_total(s, a); end = task_date(start, n) if n else start
    return {"name": st.name, "college": " · ".join(x for x in [st.college, st.degree, st.department] if x), "internship": i.title,
            "plan": f"{a.months} {'Month' if a.months == 1 else 'Months'} ({PLAN_LABEL.get(a.months, '')})", "n": n, "mode": i.mode, "start": start, "end": end, "ref": ref, "date": date, "note": note or ""}

@app.get("/api/applications/{aid}/offer-letter", response_class=HTMLResponse)
def letter(aid: int, request: Request, u: User = Depends(current), s: Session = Depends(db)):
    a, st, i = doc_user(s, u, aid)
    if not a.offer_ref: raise HTTPException(404, "Offer letter has not been sent yet")
    t = {**tpl(s), **(json.loads(a.offer_snap) if a.offer_snap else {})}  # the wording that was current when the offer was sent
    return offer_html(str(request.base_url).rstrip("/"), t, offer_details(s, a, st, i, dt.date.fromisoformat(a.start_date), a.offer_note, a.offer_ref, a.offer_date))

@app.post("/api/admin/applications/{aid}/offer-preview", response_class=HTMLResponse)
def offer_preview(aid: int, b: Offer, request: Request, a_: User = Depends(admin), s: Session = Depends(db)):
    a = s.get(Application, aid)
    if not a: raise HTTPException(404, "Not found")
    try: sd = dt.date.fromisoformat(b.start_date)
    except ValueError: raise HTTPException(400, "Choose a valid start date")
    return offer_html(str(request.base_url).rstrip("/"), tpl(s), offer_details(s, a, s.get(User, a.user_id), s.get(Internship, a.internship_id), sd, b.note, a.offer_ref or "PREVIEW", a.offer_date or dt.datetime.utcnow()))

@app.post("/api/admin/offer-template-preview", response_class=HTMLResponse)
def template_preview(b: Settings, request: Request, a_: User = Depends(admin), s: Session = Depends(db)):
    t = {**tpl(s), **b.dict(exclude_none=True)}; t["signature"] = clean_url(t["signature"]) or "/static/signature.png"
    d = {"name": "Sample Student", "college": "Sample College · B.E · CSE", "internship": "Full Stack Web Development (MERN)", "plan": "2 Months (Standard)", "n": 40, "mode": "Online",
         "start": next_monday(), "end": task_date(next_monday(), 40), "ref": "UPN-SAMPLE-00001", "date": dt.datetime.utcnow(), "note": ""}
    return offer_html(str(request.base_url).rstrip("/"), t, d)

CERT_CSS = """.cert{background:linear-gradient(135deg,#fffdf6,#fff6dd)}.cert .bd{position:absolute;inset:6mm;border:4px solid transparent;border-radius:6px;background:linear-gradient(#fffdf6,#fffdf6) padding-box,linear-gradient(120deg,#c9a227,#1a73e8,#22d3ee,#c9a227) border-box}
.cert .bd2{position:absolute;inset:10mm;border:1px solid #c9a227;border-radius:4px}.cert .ribbon{position:absolute;top:0;left:50%;transform:translateX(-50%);width:230px;height:16px;background:linear-gradient(90deg,#1a73e8,#22d3ee,#1a73e8);border-radius:0 0 10px 10px}
.cert>*:not(.bd):not(.bd2):not(.ribbon){position:relative}.cert h1{background:linear-gradient(90deg,#0a1a3f,#1356c8);-webkit-background-clip:text;background-clip:text;color:transparent}
.cert .nm{color:#1356c8;font-size:46px}.cert .meta2{display:flex;justify-content:center;gap:26px;font:13px system-ui;color:#475569;margin-top:6px}.cert .meta2 b{color:#14203f}"""

def cert_html(base, t, d):
    e = html.escape; fill = lambda x: e(x).replace("{name}", e(d["name"])).replace("{internship}", e(d["internship"])).replace("{plan}", e(d["plan"])).replace("{tasks}", str(d["tasks"]))
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Certificate - {e(d['name'])}</title><style>{DOC_CSS}{CERT_CSS}@page{{size:A4 landscape;margin:0}}</style></head><body>
<div class="bar"><button onclick="print()">Print / Save as PDF</button></div><div class="pg cert"><div class="bd"></div><div class="bd2"></div><div class="ribbon"></div>
<img class="lg" src="{base}/static/logo.png"><div class="sub">{e(t['cert_sub'])}</div><h1>{e(t['cert_heading'])}</h1>
<p style="margin-top:20px">This is to certify that</p><div class="nm">{e(d['name'])}</div>
<p>of <b>{e(d['college'])}</b><br>{fill(t['cert_body'])}</p>
<div class="meta2"><span>Internship period: <b>{e(d['start'])} to {e(d['done'])}</b></span><span>Certificate ID: <b>{e(d['ref'])}</b></span></div>
<div class="sg" style="margin:26px 12mm 0"><div>{sign_html(base, t)}</div>{SEAL}<div style="font:12px system-ui;text-align:left;color:#475569">Issued on<br><b style="font-size:14px;color:#14203f">{e(d['done'])}</b></div></div>
<p style="font:11px system-ui;color:#7b89a8;margin-top:12px">{e(t['cert_footer'])}</p></div></body></html>"""

@app.get("/api/applications/{aid}/certificate", response_class=HTMLResponse)
def certificate(aid: int, request: Request, u: User = Depends(current), s: Session = Depends(db)):
    a, st, i = doc_user(s, u, aid)
    states = task_states(s, a) if a.status == "Offer Sent" else []; info = cert_info(s, a, states)
    if info["status"] != "paid": raise HTTPException(403, "Certificate is locked")
    last = s.query(Submission).filter_by(application_id=aid).order_by(Submission.created.desc()).first()
    done = (last.created if last else dt.datetime.utcnow()).strftime("%d %B %Y"); start = dt.date.fromisoformat(a.start_date).strftime("%d %B %Y")
    d = {"name": st.name, "college": st.college or "", "internship": i.title, "plan": f"{a.months}-month", "tasks": len(states), "start": start, "done": done, "ref": info["ref"]}
    return cert_html(str(request.base_url).rstrip("/"), tpl(s), d)

@app.post("/api/admin/certificate-preview", response_class=HTMLResponse)
def cert_preview(b: Settings, request: Request, a_: User = Depends(admin), s: Session = Depends(db)):
    t = {**tpl(s), **b.dict(exclude_none=True)}; t["signature"] = clean_url(t["signature"]) or "/static/signature.png"
    d = {"name": "Sample Student", "college": "Sample College of Engineering", "internship": "Full Stack Web Development (MERN)", "plan": "2-month", "tasks": 40,
         "start": "01 January 2027", "done": "28 February 2027", "ref": "UPN-CERT-2027-00001"}
    return cert_html(str(request.base_url).rstrip("/"), t, d)

@app.post("/api/admin/applications/{aid}/send-payment")
def send_payment(aid: int, a_: User = Depends(admin), s: Session = Depends(db)):  # sends the certificate fee + UPI details to the student
    x = s.get(Application, aid)
    if not x: raise HTTPException(404, "Not found")
    f, upi = fee(s), setting(s, "upi_id")
    body = f"Certificate fee: Rs {f}." + (f" Pay by UPI to {upi} ({setting(s, 'upi_name')}) and enter the UTR number in your program page." if upi else " Open your program page to pay.") if f else "Your certificate is free. Open your program page."
    notify(s, "Certificate payment details", body, user_id=x.user_id, link=f"program/{x.id}"); s.commit(); log(s, a_.email, f"Payment details sent for application {aid}")
    return {"ok": True}

@app.post("/api/applications/{aid}/pay")
def pay(aid: int, b: Pay, u: User = Depends(current), s: Session = Depends(db)):
    a = own_app(s, u, aid, True); info = cert_info(s, a, task_states(s, a))
    if info["status"] == "locked": raise HTTPException(403, "Complete all tasks first")
    if info["status"] == "paid": raise HTTPException(409, "Certificate is already unlocked")
    if info["status"] == "pending": raise HTTPException(409, "Your payment is already waiting for verification")
    if len(b.utr.strip()) < 6: raise HTTPException(400, "Enter the UPI transaction / UTR number")
    s.add(Payment(application_id=aid, amount=info["fee"], utr=b.utr.strip()[:60]))
    notify(s, "Certificate payment submitted", f"{u.name} paid ₹{info['fee']} (UTR {b.utr.strip()[:20]}). Please verify.", admin_=True, link="payments")
    s.commit(); return {"ok": True}

class RzpVerify(BaseModel): razorpay_order_id: str; razorpay_payment_id: str; razorpay_signature: str

def mark_paid(s, p, payment_id):
    p.status, p.utr, p.note = "Paid", payment_id, "Razorpay"; ap = s.get(Application, p.application_id); st = s.get(User, ap.user_id)
    notify(s, "Certificate unlocked 🎓", "Payment received. Open your program to view and download your certificate.", user_id=ap.user_id, link=f"program/{ap.id}")
    notify(s, "Certificate payment received", f"{st.name} paid ₹{p.amount} via Razorpay ({payment_id})", admin_=True, link="payments")

@app.post("/api/applications/{aid}/razorpay-order")
def rzp_order(aid: int, u: User = Depends(current), s: Session = Depends(db)):
    if not rzp_on(): raise HTTPException(400, "Online payment is not enabled")
    a = own_app(s, u, aid, True); info = cert_info(s, a, task_states(s, a))
    if info["status"] not in ("payable", "rejected"): raise HTTPException(409, "Certificate payment is not needed right now")
    o = rzp_request("/orders", {"amount": info["fee"] * 100, "currency": "INR", "receipt": info["ref"], "notes": {"application": str(aid)}})
    s.add(Payment(application_id=aid, amount=info["fee"], utr=o["id"], status="Created")); s.commit()
    return {"order_id": o["id"], "amount": o["amount"], "key_id": RZP_KEY, "name": u.name, "email": u.email, "contact": u.mobile, "ref": info["ref"]}

@app.post("/api/applications/{aid}/razorpay-verify")
def rzp_verify(aid: int, b: RzpVerify, u: User = Depends(current), s: Session = Depends(db)):
    own_app(s, u, aid, True)
    p = s.query(Payment).filter(Payment.application_id == aid, Payment.utr.in_([b.razorpay_order_id, b.razorpay_payment_id])).first()
    if not p or not rzp_sig_ok(f"{b.razorpay_order_id}|{b.razorpay_payment_id}", b.razorpay_signature, RZP_SECRET): raise HTTPException(400, "Payment verification failed")
    if p.status != "Paid": mark_paid(s, p, b.razorpay_payment_id)
    s.commit(); return {"ok": True}

@app.post("/api/razorpay-webhook")  # optional safety net: unlocks the certificate even if the student closes the browser after paying
async def rzp_hook(request: Request, s: Session = Depends(db)):
    raw = await request.body()
    if not rzp_sig_ok(raw.decode(), request.headers.get("x-razorpay-signature"), RZP_WH): raise HTTPException(400, "Bad signature")
    ev = json.loads(raw); pl = ev.get("payload", {}); pay = (pl.get("payment") or {}).get("entity", {}); order = pay.get("order_id") or ((pl.get("order") or {}).get("entity", {}).get("id"))
    if ev.get("event") in ("payment.captured", "order.paid") and order:
        p = s.query(Payment).filter_by(utr=order, status="Created").first()
        if p: mark_paid(s, p, pay.get("id", "")); s.commit()
    return {"ok": True}

@app.get("/api/upi-qr.svg")
def upi_qr(am: str = "", tn: str = "", s: Session = Depends(db)):
    upi = setting(s, "upi_id")
    if not upi or not qrcode: raise HTTPException(404, "UPI is not configured")
    link = f"upi://pay?pa={quote(upi)}&pn={quote(setting(s, 'upi_name'))}&am={re.sub(r'[^0-9.]', '', am)}&cu=INR&tn={quote(tn[:40])}"
    buf = io.BytesIO(); qrcode.make(link, image_factory=qrcode.image.svg.SvgPathImage).save(buf)
    return Response(buf.getvalue(), media_type="image/svg+xml")

# ---------------- notifications ----------------
def my_notes(u, s):
    return s.query(Notification).filter_by(to_admin=True) if u.role == "admin" else s.query(Notification).filter_by(user_id=u.id, to_admin=False)
@app.get("/api/notifications")
def notes(u: User = Depends(current), s: Session = Depends(db)):
    q = my_notes(u, s)
    return {"unread": q.filter_by(read=False).count(), "items": [row(n) for n in q.order_by(Notification.id.desc()).limit(50)]}
@app.post("/api/notifications/read")
def read_all(u: User = Depends(current), s: Session = Depends(db)):
    my_notes(u, s).filter_by(read=False).update({"read": True}); s.commit(); return {"ok": True}

# ---------------- admin ----------------
@app.get("/api/admin/stats")
def stats(a: User = Depends(admin), s: Session = Depends(db)):
    A = s.query(Application)
    recent = [row(u) for u in s.query(User).filter_by(role="student").order_by(User.id.desc()).limit(6)]
    rapps = [{**row(x), "student": s.get(User, x.user_id).name, "college": s.get(User, x.user_id).college, "title": s.get(Internship, x.internship_id).title}
             for x in A.order_by(Application.id.desc()).limit(6)]
    return {"students": s.query(User).filter_by(role="student").count(), "internships": s.query(Internship).count(),
            "enrollments": A.count(), "pending": A.filter(Application.status.in_(["Pending", "Under Review", "Approved"])).count(),
            "offers": A.filter_by(status="Offer Sent").count(), "to_review": s.query(Submission).filter_by(status="Submitted").count(),
            "payments": s.query(Payment).filter_by(status="Pending").count(), "recent_students": recent, "recent_apps": rapps}

@app.get("/api/admin/internships")
def aint(a: User = Depends(admin), s: Session = Depends(db)):
    return [{**irow(i), "applicants": s.query(Application).filter_by(internship_id=i.id).count(), "plan_days": {str(m): s.query(Task).filter_by(internship_id=i.id, months=m).count() for m in plans_of(i)}} for i in s.query(Internship).order_by(Internship.id.desc())]
@app.post("/api/admin/internships")
def aadd(b: Intern, a: User = Depends(admin), s: Session = Depends(db)):
    d = b.dict(); d["image"] = clean_url(d["image"]); i = Internship(**d); s.add(i); s.flush(); seed_program(s, i); s.commit(); log(s, a.email, f"Added internship {i.title}"); return row(i)
@app.put("/api/admin/internships/{iid}")
def aedit(iid: int, b: Intern, a: User = Depends(admin), s: Session = Depends(db)):
    i = s.get(Internship, iid)
    if not i: raise HTTPException(404, "Not found")
    for k, v in b.dict().items(): setattr(i, k, clean_url(v) if k == "image" else v)
    i.is_sample = False; s.commit(); log(s, a.email, f"Edited internship {iid}"); return row(i)
@app.delete("/api/admin/internships/{iid}")
def adel(iid: int, a: User = Depends(admin), s: Session = Depends(db)):
    ids = [x.id for x in s.query(Application).filter_by(internship_id=iid)]
    if ids:
        s.query(Submission).filter(Submission.application_id.in_(ids)).delete(synchronize_session=False)
        s.query(Payment).filter(Payment.application_id.in_(ids)).delete(synchronize_session=False)
    s.query(Application).filter_by(internship_id=iid).delete(); s.query(Task).filter_by(internship_id=iid).delete(); s.query(Internship).filter_by(id=iid).delete()
    s.commit(); log(s, a.email, f"Deleted internship {iid}"); return {"ok": True}

def renumber(s, iid, m):
    for n, x in enumerate(plan_tasks(s, iid, m), 1): x.day = n
@app.get("/api/admin/internships/{iid}/tasks")
def atasks(iid: int, months: int = 1, a: User = Depends(admin), s: Session = Depends(db)):
    return [row(t) for t in plan_tasks(s, iid, months)]
@app.post("/api/admin/internships/{iid}/tasks")
def atask_add(iid: int, b: TaskIn, a: User = Depends(admin), s: Session = Depends(db)):
    m = b.months or 1; ts = plan_tasks(s, iid, m)
    t = Task(internship_id=iid, months=m, day=len(ts) + 1, theme=b.theme or (ts[-1].theme if ts else ""), title=b.title.strip(), submit=b.submit.strip(),
             brief=b.brief.strip(), image=clean_url(b.image), resource=clean_url(b.resource))
    s.add(t); s.commit(); return row(t)
@app.put("/api/admin/tasks/{tid}")
def atask_edit(tid: int, b: TaskIn, a: User = Depends(admin), s: Session = Depends(db)):
    t = s.get(Task, tid)
    if not t: raise HTTPException(404, "Not found")
    t.title, t.submit, t.brief, t.theme = b.title.strip(), b.submit.strip(), b.brief.strip(), b.theme.strip()
    t.image, t.resource = clean_url(b.image), clean_url(b.resource); s.commit(); return row(t)
@app.post("/api/admin/tasks/{tid}/move")
def atask_move(tid: int, dir: str, a: User = Depends(admin), s: Session = Depends(db)):
    t = s.get(Task, tid)
    if not t: raise HTTPException(404, "Not found")
    o = s.query(Task).filter_by(internship_id=t.internship_id, months=t.months, day=t.day + (-1 if dir == "up" else 1)).first()
    if o: t.day, o.day = o.day, t.day; s.commit()
    return {"ok": True}
@app.delete("/api/admin/tasks/{tid}")
def atask_del(tid: int, a: User = Depends(admin), s: Session = Depends(db)):
    t = s.get(Task, tid)
    if not t: raise HTTPException(404, "Not found")
    iid, m = t.internship_id, t.months; s.query(Submission).filter_by(task_id=tid).delete(); s.delete(t); s.flush()
    renumber(s, iid, m); s.commit(); return {"ok": True}

@app.get("/api/admin/applications")
def aapps(status: str = "", a: User = Depends(admin), s: Session = Depends(db)):
    qs = s.query(Application)
    if status: qs = qs.filter_by(status=status)
    out = []
    for x in qs.order_by(Application.id.desc()):
        u, i = s.get(User, x.user_id), s.get(Internship, x.internship_id); total, done, sub = counts(s, x)
        out.append({**row(x), "student": u.name, "email": u.email, "mobile": u.mobile, "college": u.college, "degree": u.degree, "department": u.department,
                    "year": u.year, "city": u.city, "title": i.title, "category": i.category, "total": total, "approved": done, "submitted": sub})
    return out
@app.put("/api/admin/applications/{aid}")
def areview(aid: int, r: Review, a: User = Depends(admin), s: Session = Depends(db)):
    if r.status not in ("Pending", "Under Review", "Approved", "Rejected"): raise HTTPException(400, "Bad status")
    x = s.get(Application, aid)
    if not x: raise HTTPException(404, "Not found")
    x.status, x.note = r.status, r.note
    t = s.get(Internship, x.internship_id).title
    msg = {"Under Review": ("Your enrollment is under review", f"Our team is reviewing your enrollment for {t}."),
           "Rejected": ("Enrollment update", f"Your enrollment for {t} was not selected this time. {r.note}".strip())}.get(r.status)
    if msg: notify(s, msg[0], msg[1], user_id=x.user_id, link="apps")
    s.commit(); log(s, a.email, f"Application {aid} -> {r.status}"); return row(x)

@app.post("/api/admin/applications/{aid}/offer")
def send_offer(aid: int, b: Offer, a: User = Depends(admin), s: Session = Depends(db)):
    x = s.get(Application, aid)
    if not x: raise HTTPException(404, "Not found")
    if x.status == "Rejected": raise HTTPException(400, "Re-open a rejected enrollment before sending an offer")
    try: sd = dt.date.fromisoformat(b.start_date)
    except ValueError: raise HTTPException(400, "Choose a valid start date")
    first = not x.offer_ref
    if first: x.offer_date, x.offer_ref = dt.datetime.utcnow(), f"UPN-{dt.date.today().year}-{x.id:05d}"
    x.status, x.start_date, x.offer_note, x.offer_snap = "Offer Sent", sd.isoformat(), b.note.strip()[:1500], json.dumps(tpl(s)); t = s.get(Internship, x.internship_id).title
    notify(s, "Offer letter received 🎉" if first else "Offer letter updated",
           f"Your offer for {t} ({x.months} month plan) is ready. Starts {sd.strftime('%d %b %Y')}. Tap to open your program.", user_id=x.user_id, link=f"program/{x.id}")
    s.commit(); log(s, a.email, f"Offer letter sent for application {aid}"); return row(x)

@app.get("/api/admin/students")
def astud(a: User = Depends(admin), s: Session = Depends(db)):
    out = []
    for u in s.query(User).filter_by(role="student").order_by(User.id.desc()):
        q = s.query(Application).filter_by(user_id=u.id); out.append({**row(u), "enrolled": q.count(), "offers": q.filter_by(status="Offer Sent").count()})
    return out
@app.get("/api/admin/students/{uid}")
def astud_one(uid: int, a: User = Depends(admin), s: Session = Depends(db)):
    u = s.get(User, uid)
    if not u or u.role != "student": raise HTTPException(404, "Not found")
    apps_ = []
    for x in s.query(Application).filter_by(user_id=uid).order_by(Application.id.desc()):
        total, done, sub = counts(s, x); apps_.append({**row(x), "title": s.get(Internship, x.internship_id).title, "total": total, "approved": done, "submitted": sub})
    return {"user": row(u), "applications": apps_}
@app.put("/api/admin/students/{uid}")
def astud_edit(uid: int, b: StuEdit, a: User = Depends(admin), s: Session = Depends(db)):
    u = s.get(User, uid)
    if not u or u.role != "student": raise HTTPException(404, "Not found")
    for k, v in b.dict(exclude_none=True).items(): setattr(u, k, v)
    s.commit(); log(s, a.email, f"Edited student {uid}"); return row(u)
@app.put("/api/admin/students/{uid}/active")
def aact(uid: int, active: bool, a: User = Depends(admin), s: Session = Depends(db)):
    u = s.get(User, uid)
    if not u or u.role != "student": raise HTTPException(404, "Not found")
    u.active = active; s.commit(); log(s, a.email, f"Student {uid} active={active}"); return row(u)

@app.get("/api/admin/submissions")
def asubs(status: str = "Submitted", a: User = Depends(admin), s: Session = Depends(db)):
    qs = s.query(Submission)
    if status: qs = qs.filter_by(status=status)
    out = []
    for x in qs.order_by(Submission.created.desc()).limit(300):
        ap = s.get(Application, x.application_id); t = s.get(Task, x.task_id)
        out.append({**row(x), "student": s.get(User, ap.user_id).name, "internship": s.get(Internship, ap.internship_id).title, "day": t.day, "task": t.title})
    return out
@app.put("/api/admin/submissions/{sid}")
def areview_sub(sid: int, r: SubReview, a: User = Depends(admin), s: Session = Depends(db)):
    if r.status not in ("Approved", "Rework"): raise HTTPException(400, "Bad status")
    x = s.get(Submission, sid)
    if not x: raise HTTPException(404, "Not found")
    x.status, x.feedback = r.status, r.feedback; ap = s.get(Application, x.application_id); t = s.get(Task, x.task_id)
    notify(s, f"Day {t.day} " + ("approved ✅" if r.status == "Approved" else "needs changes"), r.feedback or t.title, user_id=ap.user_id, link=f"task/{ap.id}/{t.id}")
    s.commit(); return row(x)

@app.get("/api/admin/payments")
def apays(a: User = Depends(admin), s: Session = Depends(db)):
    out = []
    for p in s.query(Payment).filter(Payment.status != "Created").order_by(Payment.id.desc()).limit(300):
        ap = s.get(Application, p.application_id)
        out.append({**row(p), "student": s.get(User, ap.user_id).name, "email": s.get(User, ap.user_id).email, "internship": s.get(Internship, ap.internship_id).title, "months": ap.months})
    return out
@app.put("/api/admin/payments/{pid}")
def areview_pay(pid: int, r: PayReview, a: User = Depends(admin), s: Session = Depends(db)):
    if r.status not in ("Paid", "Rejected"): raise HTTPException(400, "Bad status")
    p = s.get(Payment, pid)
    if not p: raise HTTPException(404, "Not found")
    p.status, p.note = r.status, r.note; ap = s.get(Application, p.application_id)
    notify(s, "Certificate unlocked 🎓" if r.status == "Paid" else "Payment could not be verified",
           "Your certificate is ready. Open your program to view and download it." if r.status == "Paid" else (r.note or "Please check your transaction number and pay again."),
           user_id=ap.user_id, link=f"program/{ap.id}")
    s.commit(); log(s, a.email, f"Payment {pid} -> {r.status}"); return row(p)
@app.get("/api/admin/settings")
def aset(a: User = Depends(admin), s: Session = Depends(db)): return {**{k: setting(s, k) for k in DEFAULTS}, "razorpay": rzp_on()}
@app.put("/api/admin/settings")
def aset_save(b: Settings, a: User = Depends(admin), s: Session = Depends(db)):
    for k, v in b.dict(exclude_none=True).items():
        if k == "signature": v = clean_url(v) or "/static/signature.png"
        r = s.get(Setting, k)
        if r: r.value = v
        else: s.add(Setting(key=k, value=v))
    s.commit(); log(s, a.email, "Updated settings"); return {k: setting(s, k) for k in DEFAULTS}

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS)), name="uploads")
@app.get("/")
def home(): return FileResponse("static/app.html")
@app.get("/admin")
def adm(): return FileResponse("static/admin.html")
@app.get("/privacy")
def pg_privacy(): return RedirectResponse("/#info/privacy")
@app.get("/terms")
def pg_terms(): return RedirectResponse("/#info/terms")
@app.get("/delete-account")
def pg_delete(): return RedirectResponse("/#info/delete")
@app.get("/.well-known/assetlinks.json")  # lets the Play Store app open full screen (no browser bar)
def assetlinks():
    pkg, fp = os.getenv("ANDROID_PACKAGE", ""), [x.strip() for x in os.getenv("ANDROID_SHA256", "").split(",") if x.strip()]
    return [{"relation": ["delegate_permission/common.handle_all_urls"], "target": {"namespace": "android_app", "package_name": pkg, "sha256_cert_fingerprints": fp}}] if pkg and fp else []
@app.get("/sw.js")
def sw(): return FileResponse("static/sw.js", media_type="application/javascript", headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"})
@app.get("/manifest.webmanifest")
def manifest(): return FileResponse("static/manifest.webmanifest", media_type="application/manifest+json")
