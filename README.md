Salary Survey Uygulaması
Bu proje, FastAPI tabanlı bir backend ve Vue 3 + Vuetify 3 tabanlı bir frontend’ten oluşmaktadır.
Kullanıcılar maaş ve şirket bilgileri gibi filtrelerle sorgulama yaparak ortalama maaş hesabı ve maaş aralığı özetlerini görüntüleyebilir.

Data için teşekkürler : https://linktr.ee/Dogandagdelen

Proje Yapısı
bash
Kopyala
salary/
 ┣ be/          # Backend kodları (FastAPI)
 ┃ ┣ Dockerfile
 ┃ ┣ requirements.txt
 ┃ ┣ main.py
 ┃ ┗ ...
 ┗ fe/          # Frontend kodları (Vue 3 + Vuetify 3)
   ┣ Dockerfile
   ┣ package.json
   ┣ vite.config.js
   ┣ src/
   ┗ ...
Backend (FastAPI)
be/requirements.txt içerisinde gerekli Python paketleri tanımlı.
main.py içerisinde FastAPI uygulaması başlatılır ve gerekli endpoint’ler tanımlanır.
Veritabanı bağlantısı, CORS ayarları, modeller vs. be klasöründe düzenlenir.
Kurulum & Çalıştırma (Yerel)
bash
Kopyala
cd be
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
Uygulama varsayılan olarak http://localhost:8000 adresinde çalışacaktır.

Docker ile Çalıştırma
bash
Kopyala
cd be
docker build -t salary-backend .
docker run -p 8000:8000 salary-backend
Frontend (Vue 3 + Vuetify 3)
fe/package.json içerisinde gerekli Node paketleri tanımlı.
src/ klasöründe Vue bileşenleri ve servisleri bulunur.
vite.config.js içerisinde Vite yapılandırması yapılır.
Kurulum & Çalıştırma (Yerel)
bash
Kopyala
cd fe
npm install
npm run dev
Uygulama http://localhost:5173 adresinde çalışacaktır (port numarası değişebilir).

Docker ile Çalıştırma
bash
Kopyala
cd fe
docker build -t salary-frontend .
docker run -p 80:80 salary-frontend
Ortak Notlar
CORS: FastAPI uygulamasında CORS middleware ayarlarını yapman gerekir. (Örneğin CORSMiddleware ile allow_origins=["*"]).
API URL: Frontend tarafında services/salaryService.js içinde, backend API URL’si (http://localhost:8000 gibi) ayarlanmalıdır.
.env Dosyaları: Gerekliyse backend ve frontend için ayrı .env dosyalarıyla konfigürasyon yapılabilir.
Deploy
Heroku Container Registry veya benzeri platformlar kullanarak Dockerize edilmiş uygulamayı yayınlayabilirsin.
Backend ve Frontend için ayrı Dockerfile’lar bulunur.
Detaylı kurulum adımları için Dockerfile açıklamalarına ve Heroku dokümantasyonuna bakabilirsin.
Katkıda Bulunma
Bu repoyu forklayın.
Yeni bir branch oluşturun (git checkout -b feature/ozellik).
Değişikliklerinizi yapın ve commit edin (git commit -m 'Özellik ekledim').
Branch’i push edin (git push origin feature/ozellik).
Pull Request açın.
Lisans
Bu projeyi istediğiniz gibi kullanabilirsiniz. (Buraya MIT, Apache, GPL veya özel lisans notu ekleyebilirsin.)