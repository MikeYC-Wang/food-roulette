import os
import random
import json
import httpx
import smtplib
import uuid      # 用於 OAuth 產生隨機狀態與密碼
import base64    # 用於解析 LINE 的 Token
import shutil # 用於儲存檔案
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse # 用於第三方登入跳轉
from pydantic import BaseModel
from sqlalchemy import select, func, text, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

# 資安相關套件
from passlib.context import CryptContext
import jwt

load_dotenv()

# ==========================================
# 資安與 JWT 設定
# ==========================================
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-please-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # Token 效期設為 7 天

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# ==========================================
# 資料庫設定與模型
# ==========================================
DATABASE_URL = os.getenv("DATABASE_URL")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# 讀取 SMTP 寄信設定
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# 讀取第三方登入設定
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
LINE_CLIENT_ID = os.getenv("LINE_CLIENT_ID")
LINE_CLIENT_SECRET = os.getenv("LINE_CLIENT_SECRET")
LINE_REDIRECT_URI = os.getenv("LINE_REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# 暫存驗證碼的字典 (以記憶體暫存)
verification_codes = {}
# 暫存重設密碼驗證碼
reset_codes = {}

if not DATABASE_URL:
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "food_roulette_db")
    DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# 餐廳暫存表
class Restaurant(Base):
    __tablename__ = "restaurants"
    id: Mapped[int] = mapped_column(primary_key=True)
    google_place_id: Mapped[Optional[str]] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column()
    rating: Mapped[float] = mapped_column()
    price_level: Mapped[Optional[str]] = mapped_column()
    opening_hours: Mapped[Optional[str]] = mapped_column(nullable=True)
    geom: Mapped[any] = mapped_column(Geometry("POINT", srid=4326))

# 使用者資料表
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    is_verified: Mapped[bool] = mapped_column(default=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(nullable=True)

# 歷史轉盤紀錄資料表
class SpinHistory(Base):
    __tablename__ = "spin_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    restaurant_name: Mapped[str] = mapped_column()
    google_place_id: Mapped[Optional[str]] = mapped_column()
    spin_time: Mapped[datetime] = mapped_column(default=func.now())

class CustomRestaurant(Base):
    __tablename__ = "custom_restaurants"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# 我的最愛資料表
class FavoriteRestaurant(Base):
    __tablename__ = "favorite_restaurants"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    restaurant_name: Mapped[str] = mapped_column()
    google_place_id: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.now())

# ==========================================
# 資安輔助函式 (密碼驗證與 Token 產生)
# ==========================================
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 解析 Token 並取得當前使用者的依賴注入函式
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證身份，請重新登入",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

# ==========================================
# FastAPI 初始化
# ==========================================
app = FastAPI(title="食來運轉 API - 完整功能版")

# 建立存放圖片的資料夾
UPLOAD_DIR = "static/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 讓外部可以透過 http://localhost:8001/static/avatars 看到圖片
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# API 路由：註冊與登入
# ==========================================
class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    code: str

class SendCodeRequest(BaseModel):
    email: str

@app.post("/api/send-code")
async def send_verification_code(req: SendCodeRequest):
    code = str(random.randint(100000, 999999))
    verification_codes[req.email] = code

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = req.email
        msg['Subject'] = "食來運轉 - 您的註冊驗證碼"
        
        body = f"歡迎加入食來運轉！\n\n您的註冊驗證碼是：【 {code} 】\n\n請在頁面上輸入此驗證碼完成註冊。\n如果這不是您的操作，請直接忽略此信件。"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return {"message": "驗證碼已發送至您的信箱！"}
    except Exception as e:
        print(f"寄信失敗: {str(e)}")
        raise HTTPException(status_code=500, detail="發送驗證碼失敗，請稍後再試")

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    if "@" not in user.email or "." not in user.email:
        raise HTTPException(status_code=400, detail="無效的電子郵件格式")

    if user.email not in verification_codes or verification_codes[user.email] != user.code:
        raise HTTPException(status_code=400, detail="驗證碼錯誤或已失效")

    result_user = await db.execute(select(User).where(User.username == user.username))
    if result_user.scalars().first():
        raise HTTPException(status_code=400, detail="此帳號已被註冊")
        
    result_email = await db.execute(select(User).where(User.email == user.email))
    if result_email.scalars().first():
        raise HTTPException(status_code=400, detail="此 Email 已被註冊")
    
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        is_verified=True
    )
    db.add(new_user)
    await db.commit()

    if user.email in verification_codes:
        del verification_codes[user.email]

    return {"message": "註冊成功！請前往登入。"}

@app.post("/api/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}

# ==========================================
# API 路由：第三方登入 (Google & LINE)
# ==========================================

@app.get("/api/auth/google")
def google_login():
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid email profile"
    )
    return RedirectResponse(url)

@app.get("/api/auth/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        # 換 Token
        resp = await client.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        token_data = resp.json()
        
        # 換資料
        user_resp = await client.get("https://www.googleapis.com/oauth2/v2/userinfo", 
                                     headers={"Authorization": f"Bearer {token_data.get('access_token')}"})
        user_info = user_resp.json()

    email = user_info.get("email")
    name = user_info.get("name", "GoogleUser")
    picture = user_info.get("picture")

    # 檢查或自動註冊
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        user = User(
            username=name,
            email=email,
            hashed_password=get_password_hash(str(uuid.uuid4())),
            is_verified=True,
            avatar_url=picture
        )
        db.add(user)
    else:
        user.avatar_url = picture

    await db.commit()
    await db.refresh(user)

    token = create_access_token(data={"sub": user.username})
    return RedirectResponse(f"{FRONTEND_URL}/login?token={token}")

@app.get("/api/auth/line")
def line_login():
    url = (
        f"https://access.line.me/oauth2/v2.1/authorize?"
        f"response_type=code&"
        f"client_id={LINE_CLIENT_ID}&"
        f"redirect_uri={LINE_REDIRECT_URI}&"
        f"state={uuid.uuid4()}&"
        f"scope=profile openid email"
    )
    return RedirectResponse(url)

@app.get("/api/auth/line/callback")
async def line_callback(code: str, db: AsyncSession = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://api.line.me/oauth2/v2.1/token", data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": LINE_REDIRECT_URI,
            "client_id": LINE_CLIENT_ID,
            "client_secret": LINE_CLIENT_SECRET,
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        token_data = resp.json()
        
        # 解析 ID Token 拿 Email
        id_token = token_data.get("id_token")
        payload = json.loads(base64.b64decode(id_token.split('.')[1] + '==').decode())
        email = payload.get("email", f"{payload.get('sub')}@line.me")
        line_name = payload.get("name", "LINE使用者")
        picture = payload.get("picture")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        user = User(
            username=line_name,
            email=email,
            hashed_password=get_password_hash(str(uuid.uuid4())),
            is_verified=True,
            avatar_url=picture
        )
        db.add(user)
    else:
        user.avatar_url = picture

    await db.commit()
    await db.refresh(user)

    token = create_access_token(data={"sub": user.username})
    return RedirectResponse(f"{FRONTEND_URL}/login?token={token}")

@app.post("/api/user/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. 檢查檔案格式
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只允許上傳圖片檔案")
    
    # 2. 決定檔名 (使用使用者 ID 避免碰撞)
    extension = file.filename.split(".")[-1]
    file_name = f"user_{current_user.id}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    # 3. 儲存檔案
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 4. 更新資料庫裡的網址 (改為後端提供的網址路徑)
    avatar_url = f"http://127.0.0.1:8001/static/avatars/{file_name}"
    current_user.avatar_url = avatar_url
    await db.commit()
    
    return {"message": "頭像上傳成功", "avatar_url": avatar_url}

# ==========================================
# API 路由：其他功能 (me, history, custom-list, favorites, search, spin)
# ==========================================

@app.get("/api/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
        "created_at": current_user.created_at.strftime("%Y-%m-%d")
    }

class HistoryCreate(BaseModel):
    restaurant_name: str
    google_place_id: Optional[str] = None

@app.post("/api/history")
async def save_spin_history(history: HistoryCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_history = SpinHistory(
        user_id=current_user.id,
        restaurant_name=history.restaurant_name,
        google_place_id=history.google_place_id
    )
    db.add(new_history)
    await db.commit()
    return {"message": "歷史紀錄已儲存"}

@app.get("/api/history")
async def get_user_history(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SpinHistory).where(SpinHistory.user_id == current_user.id).order_by(SpinHistory.spin_time.desc()).limit(20))
    histories = result.scalars().all()
    return {
        "user": current_user.username,
        "history": [{"id": h.id, "restaurant_name": h.restaurant_name, "google_place_id": h.google_place_id, "spin_time": h.spin_time.strftime("%Y-%m-%d %H:%M:%S")} for h in histories]
    }

class CustomListUpdate(BaseModel):
    restaurants: List[str]

@app.get("/api/custom-list")
async def get_custom_list(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CustomRestaurant.name).where(CustomRestaurant.user_id == current_user.id).order_by(CustomRestaurant.id))
    names = result.scalars().all()
    return {"custom_list": names}

@app.post("/api/custom-list")
async def update_custom_list(req: CustomListUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(text("DELETE FROM custom_restaurants WHERE user_id = :uid"), {"uid": current_user.id})
    for name in req.restaurants:
        db.add(CustomRestaurant(user_id=current_user.id, name=name))
    await db.commit()
    return {"message": "自訂名單已儲存"}

class FavoriteToggle(BaseModel):
    restaurant_name: str
    google_place_id: str

@app.post("/api/favorites/toggle")
async def toggle_favorite(fav: FavoriteToggle, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FavoriteRestaurant).where(FavoriteRestaurant.user_id == current_user.id).where(FavoriteRestaurant.google_place_id == fav.google_place_id))
    existing = result.scalars().first()
    if existing:
        await db.delete(existing)
        await db.commit()
        return {"message": "已取消收藏", "status": "removed"}
    else:
        db.add(FavoriteRestaurant(user_id=current_user.id, restaurant_name=fav.restaurant_name, google_place_id=fav.google_place_id))
        await db.commit()
        return {"message": "已加入收藏", "status": "added"}

@app.get("/api/favorites")
async def get_favorites(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FavoriteRestaurant).where(FavoriteRestaurant.user_id == current_user.id).order_by(FavoriteRestaurant.created_at.desc()))
    favs = result.scalars().all()
    return {
        "favorites": [{"id": f.id, "restaurant_name": f.restaurant_name, "google_place_id": f.google_place_id, "created_at": f.created_at.strftime("%Y-%m-%d %H:%M:%S")} for f in favs]
    }

@app.get("/api/search-location")
async def search_location(query: str):
    try:
        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {"Content-Type": "application/json", "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY, "X-Goog-FieldMask": "places.displayName,places.location,places.formattedAddress"}
        payload = {"textQuery": query, "languageCode": "zh-TW", "maxResultCount": 5}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                places = resp.json().get("places", [])
                results = [{"name": p.get("displayName", {}).get("text"), "address": p.get("formattedAddress"), "lat": p.get("location", {}).get("latitude"), "lng": p.get("location", {}).get("longitude")} for p in places if p.get("location")]
                return {"status": "success", "results": results}
            return {"status": "error", "message": "Google API 錯誤"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class SpinRequest(BaseModel):
    lat: float
    lng: float
    distance: int
    types: List[str]
    features: List[str] = []
    priceLevels: List[str] = []
    spinCount: int = 6
    openNow: bool = False
    highRating: bool = False

@app.post("/api/spin")
async def get_roulette_data(req: SpinRequest, db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("TRUNCATE TABLE restaurants RESTART IDENTITY CASCADE;"))
        headers = {"Content-Type": "application/json", "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY, "X-Goog-FieldMask": "places.id,places.displayName,places.rating,places.location,places.types,places.priceLevel,places.regularOpeningHours"}
        query_parts = req.types + req.features
        query_str = " ".join(query_parts) if query_parts else "美食"
        fetch_count = min(req.spinCount + 10, 20)
        payload = {"textQuery": f"{query_str} 餐廳", "maxResultCount": fetch_count, "languageCode": "zh-TW", "locationBias": {"circle": {"center": {"latitude": req.lat, "longitude": req.lng}, "radius": float(req.distance)}}}
        if req.openNow: payload["openNow"] = True
        if req.highRating: payload["minRating"] = 4.0

        async with httpx.AsyncClient() as client:
            resp = await client.post("https://places.googleapis.com/v1/places:searchText", json=payload, headers=headers)
            if resp.status_code == 200:
                places_data = resp.json().get("places", [])
                for p in places_data:
                    loc = p.get("location", {})
                    sql = text("INSERT INTO restaurants (google_place_id, name, type, rating, price_level, opening_hours, geom) VALUES (:place_id, :name, :type, :rating, :price_level, :opening_hours, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)) ON CONFLICT (google_place_id) DO NOTHING;")
                    await db.execute(sql, {"place_id": p.get("id"), "name": p.get("displayName", {}).get("text"), "type": p.get("types", ["restaurant"])[0], "rating": p.get("rating", 0.0), "price_level": p.get("priceLevel"), "opening_hours": json.dumps(p.get("regularOpeningHours", {}), ensure_ascii=False), "lng": loc.get("longitude"), "lat": loc.get("latitude")})
                await db.commit()

        user_point = ST_SetSRID(ST_MakePoint(req.lng, req.lat), 4326)
        from sqlalchemy import cast
        from geoalchemy2 import Geography
        query = select(Restaurant).where(func.ST_DWithin(cast(Restaurant.geom, Geography), cast(user_point, Geography), float(req.distance)))
        if req.priceLevels: query = query.where(Restaurant.price_level.in_(req.priceLevels))
        if req.highRating: query = query.where(Restaurant.rating >= 4.0)

        db_result = await db.execute(query)
        restaurants = db_result.scalars().all()
        formatted_list = [{"id": r.google_place_id, "name": r.name, "type": r.type, "rating": float(r.rating), "priceLevel": r.price_level, "openingHours": json.loads(r.opening_hours) if r.opening_hours else None} for r in restaurants]
        if not formatted_list: return {"status": "success", "results": [{"name": "太挑剔囉！附近沒找到符合的餐廳", "type": "N/A", "rating": 0}]}
        
        return {"status": "success", "results": random.sample(formatted_list, min(len(formatted_list), req.spinCount))}
    except Exception as e:
        print(f"後端錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# ==========================================
# API 路由：忘記密碼
# ==========================================
class PasswordResetRequest(BaseModel):
    email: str

@app.post("/api/password-reset/request")
async def request_password_reset(req: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    # 1. 檢查這個信箱有沒有註冊過
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="找不到此電子郵件對應的帳號")
    
    # 2. 產生 6 位數驗證碼並暫存
    code = str(random.randint(100000, 999999))
    reset_codes[req.email] = code
    
    # 3. 寄出重設信件
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = req.email
        msg['Subject'] = "食來運轉 - 密碼重設驗證碼"
        
        body = f"您好！\n\n您的密碼重設驗證碼是：【 {code} 】\n\n請在頁面上輸入此驗證碼以設定新密碼。\n如果您並未要求重設密碼，請直接忽略此信件。"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return {"message": "密碼重設驗證碼已發送至您的信箱！"}
    except Exception as e:
        print(f"寄信失敗: {str(e)}")
        raise HTTPException(status_code=500, detail="發送驗證碼失敗，請稍後再試")

class PasswordResetConfirm(BaseModel):
    email: str
    code: str
    new_password: str

@app.post("/api/password-reset/confirm")
async def confirm_password_reset(req: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    # 1. 檢查驗證碼
    if reset_codes.get(req.email) != req.code:
        raise HTTPException(status_code=400, detail="驗證碼錯誤或已失效")
        
    # 2. 找出使用者
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="找不到此電子郵件對應的帳號")
        
    # 3. 更新密碼 (記得要雜湊加密)
    user.hashed_password = get_password_hash(req.new_password)
    await db.commit()
    
    # 4. 清除驗證碼
    if req.email in reset_codes:
        del reset_codes[req.email]
        
    return {"message": "密碼重設成功！請使用新密碼登入。"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)