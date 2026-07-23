import json, os
from datetime import date, datetime
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session
from auth import create_access_token, get_admin, get_current_user, hash_password, verify_password
from database import Base, engine, get_db
from models import Report, User
from schemas import AnalyticsOut, KundliRequest, LoginRequest, ProfileUpdate, ReportOut, SignupRequest, TokenResponse, UserOut
from services.gemini_service import generate_report
from services.prompt_generator import build_kundli_prompt

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Kundli AI API", version="1.0.0")
origins = [item.strip() for item in os.getenv("FRONTEND_ORIGIN", "http://localhost:3000").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def create_configured_admin():
    email, password = os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASSWORD")
    if not email or not password:
        return
    db = next(get_db())
    try:
        if not db.query(User).filter(User.email == email.lower()).first():
            db.add(User(full_name="Kundli AI Admin", email=email.lower(), password_hash=hash_password(password), is_admin=True))
            db.commit()
    finally:
        db.close()

@app.get("/health")
def health(): return {"status": "ok"}
@app.post("/signup", response_model=TokenResponse, status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email.lower()).first(): raise HTTPException(409, "Email is already registered")
    user = User(full_name=payload.full_name, email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_access_token(user.email), "user": user}
@app.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash): raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    return {"access_token": create_access_token(user.email), "user": user}
@app.get("/profile", response_model=UserOut)
def profile(user: User = Depends(get_current_user)): return user
@app.put("/profile", response_model=UserOut)
def update_profile(payload: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.email and payload.email.lower() != user.email:
        if db.query(User).filter(User.email == payload.email.lower()).first(): raise HTTPException(409, "Email is already registered")
        user.email = payload.email.lower()
    if payload.full_name: user.full_name = payload.full_name
    if payload.new_password:
        if not payload.current_password or not verify_password(payload.current_password, user.password_hash): raise HTTPException(400, "Current password is incorrect")
        user.password_hash = hash_password(payload.new_password)
    db.commit(); db.refresh(user); return user
@app.delete("/account", status_code=204)
def delete_account(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(user); db.commit()
@app.post("/generate-kundli", response_model=ReportOut, status_code=201)
def generate_kundli(payload: KundliRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try: content = generate_report(build_kundli_prompt(payload))
    except RuntimeError as error: raise HTTPException(503, str(error))
    report = Report(user_id=user.id, full_name=payload.full_name, birth_date=payload.birth_date, birth_time=payload.birth_time, city=payload.city, request_data=payload.model_dump_json(), content=content)
    db.add(report); db.commit(); db.refresh(report); return report
@app.get("/history", response_model=list[ReportOut])
def history(search: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Report).filter(Report.user_id == user.id)
    if search: query = query.filter(Report.full_name.ilike(f"%{search}%"))
    return query.order_by(Report.created_at.desc()).all()
@app.get("/report/{report_id}", response_model=ReportOut)
def get_report(report_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == user.id).first()
    if not report: raise HTTPException(404, "Report not found")
    return report
@app.delete("/report/{report_id}", status_code=204)
def delete_report(report_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == user.id).first()
    if not report: raise HTTPException(404, "Report not found")
    db.delete(report); db.commit()
@app.get("/admin/users", response_model=list[UserOut])
def admin_users(_: User = Depends(get_admin), db: Session = Depends(get_db)): return db.query(User).order_by(User.created_at.desc()).all()
@app.get("/admin/reports", response_model=list[ReportOut])
def admin_reports(_: User = Depends(get_admin), db: Session = Depends(get_db)): return db.query(Report).order_by(Report.created_at.desc()).all()
@app.delete("/admin/users/{user_id}", status_code=204)
def admin_delete_user(user_id: int, admin: User = Depends(get_admin), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target: raise HTTPException(404, "User not found")
    if target.id == admin.id: raise HTTPException(400, "You cannot delete your own account here")
    db.delete(target); db.commit()
@app.get("/admin/analytics", response_model=AnalyticsOut)
def admin_analytics(_: User = Depends(get_admin), db: Session = Depends(get_db)):
    return {"users": db.query(func.count(User.id)).scalar(), "reports": db.query(func.count(Report.id)).scalar(), "reports_today": db.query(func.count(Report.id)).filter(func.date(Report.created_at) == date.today()).scalar()}
