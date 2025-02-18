import os
import datetime
import math
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# .env dosyasını yükle
load_dotenv()

# .env'den veritabanı bilgilerini al
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy engine ve session tanımları
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy temel modeli
Base = declarative_base()


class SalarySurvey(Base):
    __tablename__ = "salary_survey"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=True)
    title = Column(String, nullable=True)
    company_size = Column(
        Float, nullable=True
    )  # Şirket büyüklüğü sayısal olarak saklanıyor
    accoms = Column(String, nullable=True)
    experience = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    pay_range = Column(String, nullable=True)
    area = Column(String, nullable=True)
    company_origin = Column(String, nullable=True)
    work_style = Column(String, nullable=True)
    work_area = Column(String, nullable=True)


# Gerekirse tabloyu oluştur (migration aracı kullanman önerilir)
Base.metadata.create_all(bind=engine)


# Pydantic modeli (Response Model)
class SalarySurveyOut(BaseModel):
    id: int
    date: Optional[datetime.datetime]
    title: Optional[str]
    company_size: Optional[float]
    accoms: Optional[str]
    experience: Optional[float]
    currency: Optional[str]
    pay_range: Optional[str]
    area: Optional[str]
    company_origin: Optional[str]
    work_style: Optional[str]
    work_area: Optional[str]

    class Config:
        orm_mode = True
        # float değerleri JSON encode ederken, finite değilse None döndür.
        json_encoders = {float: lambda v: v if math.isfinite(v) else None}


app = FastAPI(title="Salary Survey API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# DB bağlantısı için dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# # GET endpoint'i; query parametreleri ile filtreleme yapılıyor.
# @app.get("/salaries", response_model=List[SalarySurveyOut])
# def get_salary_surveys(
#     title: Optional[str] = Query(None, description="Pozisyon veya seviye filtresi"),
#     min_company_size: Optional[float] = Query(
#         None, description="Minimum şirket büyüklüğü"
#     ),
#     max_company_size: Optional[float] = Query(
#         None, description="Maksimum şirket büyüklüğü"
#     ),
#     currency: Optional[str] = Query(None, description="Currency"),
#     work_area: Optional[str] = Query(None, description="Çalışma Alanı"),
#     min_experience: Optional[float] = Query(None, description="Minimum tecrübe (yıl)"),
#     max_experience: Optional[float] = Query(None, description="Maksimum tecrübe (yıl)"),
#     area: Optional[str] = Query(None, description="Sektör filtresi"),
#     db: Session = Depends(get_db),
# ):
#     query = db.query(SalarySurvey)

#     if title:
#         query = query.filter(SalarySurvey.title.ilike(f"%{title}%"))
#     if min_company_size is not None:
#         query = query.filter(SalarySurvey.company_size >= min_company_size)
#     if max_company_size is not None:
#         query = query.filter(SalarySurvey.company_size <= max_company_size)
#     if min_experience is not None:
#         query = query.filter(SalarySurvey.experience >= min_experience)
#     if max_experience is not None:
#         query = query.filter(SalarySurvey.experience <= max_experience)
#     if area:
#         query = query.filter(SalarySurvey.area.ilike(f"%{area}%"))
#     if work_area:
#         query = query.filter(SalarySurvey.area.ilike(f"%{work_area}%"))
#     if currency:
#         query = query.filter(SalarySurvey.currency.ilike(f"%{currency}"))

#     results = query.all()
#     return results


# Yeni endpoint: Filtreler uygulanmış sonuçlar için pay_range'e göre gruplandırma ve
# her grubun kayıt sayısını döndürüp, en çok bulunan ilk 3'ü gösterir.
@app.get("/salaries/pay_range_summary")
def get_pay_range_summary(
    title: Optional[str] = Query(None, description="Pozisyon veya seviye filtresi"),
    min_company_size: Optional[float] = Query(
        None, description="Minimum şirket büyüklüğü"
    ),
    max_company_size: Optional[float] = Query(
        None, description="Maksimum şirket büyüklüğü"
    ),
    min_experience: Optional[float] = Query(None, description="Minimum tecrübe (yıl)"),
    max_experience: Optional[float] = Query(None, description="Maksimum tecrübe (yıl)"),
    area: Optional[str] = Query(None, description="Sektör filtresi"),
    work_area: Optional[str] = Query(None, description="Çalışma Alanı"),
    currency: Optional[str] = Query(None, description="Currency"),
    db: Session = Depends(get_db),
):
    query = db.query(SalarySurvey.pay_range, func.count(SalarySurvey.id).label("count"))

    if title:
        query = query.filter(SalarySurvey.title.ilike(f"%{title}%"))
    if min_company_size is not None:
        query = query.filter(SalarySurvey.company_size >= min_company_size)
    if max_company_size is not None:
        query = query.filter(SalarySurvey.company_size <= max_company_size)
    if min_experience is not None:
        query = query.filter(SalarySurvey.experience >= min_experience)
    if max_experience is not None:
        query = query.filter(SalarySurvey.experience <= max_experience)
    if area:
        query = query.filter(SalarySurvey.area.ilike(f"%{area}%"))
    if work_area:
        query = query.filter(SalarySurvey.work_area.ilike(f"%{work_area}%"))
    if currency:
        query = query.filter(SalarySurvey.currency.ilike(f"%{currency}"))
    # Group by pay_range ve sayıyı hesapla, ardından azalan sırayla ilk 3 sonucu getir.
    query = (
        query.group_by(SalarySurvey.pay_range)
        .order_by(func.count(SalarySurvey.id).desc())
        .limit(3)
    )
    results = query.all()
    summary = [{"pay_range": pr, "count": count} for pr, count in results]
    return summary
