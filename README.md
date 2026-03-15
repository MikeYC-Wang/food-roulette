# 🍱 食來運轉 (Food Roulette) 

> **「還在煩惱等一下要吃什麼嗎？」**
> 
> 專為選擇障礙者打造的美食轉盤 App！結合 Google Maps 定位與豐富的圖表分析，不僅幫你決定下一餐吃什麼，還能幫你記錄日常飲食花費與打卡足跡。

🌐 **[線上體驗連結 (Live Demo)](https://food-roulette-ruby.vercel.app/)**

---

# ✨ 核心功能 (Features)

## 🎯 智慧美食轉盤
自動獲取使用者定位，透過 **Google Maps API** 搜尋附近符合條件的餐廳：

- 距離
- 評價
- 是否營業中  

並進行 **隨機抽選餐廳**。

---

## 🥤 專屬飲料模式
不僅找飯吃！

一鍵切換 **「飲料模式」**，幫你抽出附近的 **手搖飲店**。

---

## 📝 自訂口袋名單
想吃幾家店但選不出來？

- 自己輸入餐廳清單
- 交給命運幫你抽出今晚要吃哪家

---

## 🔐 多元會員系統

支援多種登入方式：

- Email 註冊 / 忘記密碼
- Google OAuth 登入
- LINE OAuth 登入

---

## 📊 專屬飲食手札

### 🔥 熱力圖打卡
直觀呈現你的 **外食與手搖飲狂熱程度**

### 📊 吃貨雷達與花費分析
透過 **ECharts 圖表分析**

- 每月飲食花費
- 各類型餐點比例

包含：

- 圓餅圖
- 柱狀圖

---

## ❤️ 我的最愛與歷史紀錄

- 一鍵收藏喜歡的餐廳
- 保留每一次抽中的餐廳紀錄
- 隨時回顧你的美食足跡

---

## 🔗 無縫導航與分享

抽中餐廳後可以：

- 直接開啟 **Google Maps 導航**
- 產生 **分享文案**傳給朋友

---

# 🛠️ 技術棧 (Tech Stack)

## 前端 (Frontend)

- Framework: **Vue 3 (Composition API) + Vite**
- Styling: **Tailwind CSS**（自定義 Bento 便當盒 UI 風格）
- Data Visualization: **Apache ECharts**
- Routing & State: **Vue Router**
- Deployment: **Vercel**

---

## 後端 (Backend)

- Framework: **FastAPI (Python)**
- Database: **PostgreSQL**（Neon 雲端資料庫）
- ORM: **SQLAlchemy (Async) + asyncpg**
- Authentication:
  - JWT (JSON Web Tokens)
  - OAuth 2.0 (Google / LINE)
- Deployment: **Render**

---

# 🚀 本地開發環境架設 (Local Development)

請確認電腦已安裝：

- **Node.js (建議 v18+)**
- **Python (建議 3.10+)**

---

# 1️⃣ 取得專案代碼

```bash
git clone https://github.com/MikeYC-Wang/food-roulette.git
cd food-roulette
```

---

# 2️⃣ 後端設定 (Backend)

進入 backend 目錄：

```bash
cd backend
```

## 建立虛擬環境

```bash
python -m venv venv
```

### 啟動虛擬環境

Windows：

```bash
venv\Scripts\activate
```

Mac / Linux：

```bash
source venv/bin/activate
```

---

## 安裝依賴套件

```bash
pip install -r requirements.txt
```

---

## 建立環境變數 `.env`

在 **backend 目錄**建立 `.env`

```env
# 資料庫連線
DATABASE_URL=postgresql+asyncpg://<你的資料庫帳號>:<密碼>@<資料庫位置>/<資料庫名稱>?ssl=require

# JWT 密鑰
SECRET_KEY=你的隨機JWT密鑰

# Google Maps API
GOOGLE_MAPS_API_KEY=你的Google_Maps_API_Key

# OAuth 第三方登入
GOOGLE_CLIENT_ID=你的Google_Client_ID
GOOGLE_CLIENT_SECRET=你的Google_Client_Secret

LINE_CLIENT_ID=你的LINE_Channel_ID
LINE_CLIENT_SECRET=你的LINE_Channel_Secret

# 前端網址
FRONTEND_URL=http://localhost:5173

# Email 驗證設定
MAIL_USERNAME=你的Gmail
MAIL_PASSWORD=你的Gmail應用程式密碼
MAIL_FROM=你的Gmail
```

---

## 初始化資料庫

```bash
python init_db.py
```

---

## 啟動 FastAPI 伺服器

```bash
uvicorn main:app --reload --port 8001
```

API 文件（Swagger UI）：

```
http://127.0.0.1:8001/docs
```

---

# 3️⃣ 前端設定 (Frontend)

開啟新的終端機

```bash
cd frontend
```

---

## 安裝依賴

```bash
npm install
```

---

## 建立 `.env`

在 frontend 目錄建立 `.env`

```env
VITE_API_BASE_URL=http://127.0.0.1:8001
```

---

## 啟動前端開發伺服器

```bash
npm run dev
```

打開瀏覽器：

```
http://localhost:5173
```

即可開始體驗完整功能 🎉

---

# 📱 畫面截圖 (Screenshots)

## 美食轉盤首頁

（放截圖）

## 飲食手札分析

（放圖表截圖）

建議將圖片放在：

```
frontend/public/
```

然後在 README 使用圖片連結。

---

# 👨‍💻 作者 (Author)

**Mike Wang**

GitHub:  
https://github.com/MikeYC-Wang

---

如果這個專案對你有幫助  
歡迎幫我點個 ⭐️ **Star** 支持一下！
