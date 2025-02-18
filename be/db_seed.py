import os
import re
import math
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# .env'den veritabanı bağlantı bilgilerini al
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

# PostgreSQL bağlantı URL'sini oluştur
db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy temel modeli
Base = declarative_base()


class SalarySurvey(Base):
    __tablename__ = "salary_survey"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=True)
    title = Column(String, nullable=True)
    # "Şirket  kadar büyük?" sütunu artık numeric değer olarak işlenecek (ortalama değer)
    company_size = Column(Float, nullable=True)
    accoms = Column(String, nullable=True)
    experience = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    pay_range = Column(String, nullable=True)
    area = Column(String, nullable=True)
    company_origin = Column(String, nullable=True)
    work_style = Column(String, nullable=True)
    work_area = Column(String, nullable=True)


class CSVImporter:
    def __init__(self, csv_file: str, db_url: str):
        """
        CSV dosyası yolunu ve veritabanı URL'sini alır, gerekli bağlantıları oluşturur.
        """
        self.csv_file = csv_file
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def import_csv(self) -> None:
        """
        CSV dosyasını okur, dönüştürür, temizler ve veritabanına aktarır.
        """
        df = self._read_csv()
        df = self._transform_dataframe(df)
        self._load_to_db(df)

    def _read_csv(self) -> pd.DataFrame:
        """
        CSV dosyasını DataFrame'e okur.
        """
        try:
            df = pd.read_csv(self.csv_file)
            print(
                f"CSV dosyası '{self.csv_file}' başarıyla okundu. Toplam {len(df)} satır mevcut."
            )
            return df
        except Exception as e:
            print("CSV okunurken hata oluştu:", e)
            raise

    def _clean_string(self, value):
        """
        String değerleri temizler; baş ve sondaki boşlukları kaldırır, boş string ise None döner.
        """
        if pd.isna(value):
            return None
        if isinstance(value, str):
            value = value.strip()
            return value if value != "" else None
        return value

    def _convert_range(self, value):
        """
        Verilen değerden sayıları yakalar.
        - Eğer '-' karakteri varsa, aralık olarak kabul edilir ve yakalanan sayıların ortalaması hesaplanır.
        - Eğer '-' yoksa, string tamamen sayısal ise sayıyı döndürür, aksi halde None döner.
        - Eğer değer "startup" ise, 10-15 aralığını varsayar ve ortalamasını döndürür.

        Örnekler:
        "Dinazor"                => None
        "16-25 kişi"            => (16+25)/2 = 20.5
        "3000 uzeri"            => None
        "101- büyük işte :D"     => 101.0
        "Startup"               => (10+15)/2 = 12.5
        """
        try:
            if pd.isna(value):
                return None
            value_str = str(value).strip().lower()
            # "startup" ifadesi varsa, 10-15 aralığı varsay
            if value_str == "startup":
                return (10 + 15) / 2
            if "-" in value_str:
                matches = re.findall(r"(\d+\.?\d*)", value_str)
                if not matches:
                    return None
                numbers = [float(num) for num in matches]
                return sum(numbers) / len(numbers) if numbers else None
            else:
                if re.fullmatch(r"\d+\.?\d*", value_str):
                    return float(value_str)
                else:
                    return None
        except Exception as e:
            print(f"Aralık dönüştürme hatası ({value}):", e)
            return None

    def _transform_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        CSV sütunlarını veritabanı kolonlarına göre yeniden adlandırır,
        tarih sütununu datetime formatına çevirir,
        ve ilgili sütunlardaki değerleri temizleyip dönüştürür.
        """
        rename_mapping = {
            "Zaman damgası": "date",
            "Kendinizi ne olarak tanımlarsınız?": "title",
            # "Şirket  kadar büyük?" sütunu company_size olarak işlenecek
            "Şirket  kadar büyük?": "company_size",
            "Yan haklar var mı?": "accoms",
            "Tecrübe yılınız ?": "experience",
            "Maaşınızın para birimi?": "currency",
            "Maaş aralığınız?": "pay_range",
            "Çalıştığınız Sektör?": "area",
            "Şirket Menşei": "company_origin",
            "Çalışma Şekli?": "work_style",
            "Göreviniz nedir?": "work_area",
        }
        df.rename(columns=rename_mapping, inplace=True)

        # 'date' sütununu datetime formatına çevir (gün-ay-yıl formatı)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)

        # 'experience' sütunundaki değerleri dönüştür (aralık vs.)
        if "experience" in df.columns:
            df["experience"] = df["experience"].apply(self._convert_range)

        # 'company_size' sütunundaki değerleri dönüştür (aralık vs.)
        if "company_size" in df.columns:
            df["company_size"] = df["company_size"].apply(self._convert_range)

        # Diğer string sütunlarını temizle
        string_columns = [
            "title",
            "accoms",
            "currency",
            "pay_range",
            "area",
            "company_origin",
            "work_style",
            "work_area",
        ]
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._clean_string)

        print("DataFrame sütunları yeniden adlandırıldı, dönüştürüldü ve temizlendi.")
        return df

    def _load_to_db(self, df: pd.DataFrame) -> None:
        """
        DataFrame'deki verileri veritabanına toplu olarak ekler.
        """
        session = self.Session()
        try:
            records = df.to_dict(orient="records")
            salary_entries = [SalarySurvey(**record) for record in records]
            session.bulk_save_objects(salary_entries)
            session.commit()
            print(f"✅ {len(salary_entries)} kayıt başarıyla veritabanına aktarıldı.")
        except Exception as e:
            session.rollback()
            print("Veritabanına veri aktarılırken hata oluştu:", e)
        finally:
            session.close()


if __name__ == "__main__":
    csv_file = "salary-form.csv"

    engine = create_engine(db_url)
    Base.metadata.create_all(engine)

    importer = CSVImporter(csv_file=csv_file, db_url=db_url)
    importer.import_csv()
