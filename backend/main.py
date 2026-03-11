import os
import random
import json
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
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

# 暫存驗證碼的字典 (以記憶體暫存)
verification_codes = {}

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

# 歷史轉盤紀錄資料表
class SpinHistory(Base):
    __tablename__ = "spin_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    restaurant_name: Mapped[str] = mapped_column()
    google_place_id: Mapped[Optional[str]] = mapped_column()
    spin_time: Mapped[datetime] = mapped_column(default=func.now())

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

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
app = FastAPI(title="食來運轉 API - 資安升級版")

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
    # 產生 6 位數隨機驗證碼
    code = str(random.randint(100000, 999999))
    verification_codes[req.email] = code

    try:
        # 設定信件內容
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = req.email
        msg['Subject'] = "食來運轉 - 您的註冊驗證碼"
        
        body = f"歡迎加入食來運轉！\n\n您的註冊驗證碼是：【 {code} 】\n\n請在頁面上輸入此驗證碼完成註冊。\n如果這不是您的操作，請直接忽略此信件。"
        msg.attach(MIMEText(body, 'plain'))
        
        # 透過 Gmail SMTP 寄信
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
    # 1. 基本的 Email 格式防呆檢查
    if "@" not in user.email or "." not in user.email:
        raise HTTPException(status_code=400, detail="無效的電子郵件格式")

    # 2. 檢查驗證碼是否正確
    if user.email not in verification_codes or verification_codes[user.email] != user.code:
        raise HTTPException(status_code=400, detail="驗證碼錯誤或已失效")

    # 3. 檢查帳號是否重複
    result_user = await db.execute(select(User).where(User.username == user.username))
    if result_user.scalars().first():
        raise HTTPException(status_code=400, detail="此帳號已被註冊")
        
    # 4. 檢查 Email 是否重複
    result_email = await db.execute(select(User).where(User.email == user.email))
    if result_email.scalars().first():
        raise HTTPException(status_code=400, detail="此 Email 已被註冊")
    
    # 將密碼進行 Bcrypt 雜湊加密後存入資料庫
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(new_user)
    await db.commit()

    # 註冊成功後，清除暫存的驗證碼
    if user.email in verification_codes:
        del verification_codes[user.email]

    return {"message": "註冊成功！請前往登入。"}

@app.post("/api/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # 驗證帳號
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()
    
    # 驗證密碼 (比對明碼與資料庫的雜湊碼)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 核發 JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}

# ==========================================
# API 路由：取得目前登入使用者資料
# ==========================================
@app.get("/api/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at.strftime("%Y-%m-%d")
    }

# ==========================================
# API 路由：歷史紀錄 (需要 JWT Token 才能訪問)
# ==========================================
class HistoryCreate(BaseModel):
    restaurant_name: str
    google_place_id: Optional[str] = None

@app.post("/api/history")
async def save_spin_history(
    history: HistoryCreate, 
    current_user: User = Depends(get_current_user), # 資安守門員：必須攜帶 Token
    db: AsyncSession = Depends(get_db)
):
    new_history = SpinHistory(
        user_id=current_user.id,
        restaurant_name=history.restaurant_name,
        google_place_id=history.google_place_id
    )
    db.add(new_history)
    await db.commit()
    return {"message": "歷史紀錄已儲存"}

@app.get("/api/history")
async def get_user_history(
    current_user: User = Depends(get_current_user), # 資安守門員：必須攜帶 Token
    db: AsyncSession = Depends(get_db)
):
    # 撈出該使用者的所有歷史紀錄，依時間倒序排列
    result = await db.execute(
        select(SpinHistory)
        .where(SpinHistory.user_id == current_user.id)
        .order_by(SpinHistory.spin_time.desc())
        .limit(20) # 預設回傳最近 20 筆
    )
    histories = result.scalars().all()
    return {
        "user": current_user.username,
        "history": [
            {
                "id": h.id,
                "restaurant_name": h.restaurant_name,
                "google_place_id": h.google_place_id,
                "spin_time": h.spin_time.strftime("%Y-%m-%d %H:%M:%S")
            } for h in histories
        ]
    }

# ==========================================
# 轉盤 API
# ==========================================
class SpinRequest(BaseModel):
    lat: float
    lng: float
    distance: int
    types: List[str]
    features: List[str] = []
    priceLevels: List[str] = []
    spinCount: int = 6

@app.post("/api/spin")
async def get_roulette_data(req: SpinRequest, db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("TRUNCATE TABLE restaurants RESTART IDENTITY CASCADE;"))
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": "places.id,places.displayName,places.rating,places.location,places.types,places.priceLevel,places.regularOpeningHours"
        }

        # 將「想吃什麼」與「加分條件」組合起來，發揮 Google 搜尋的最大威力
        query_parts = []
        if req.types:
            query_parts.extend(req.types)
        if req.features:
            query_parts.extend(req.features)

        if query_parts:
            places_url = "https://places.googleapis.com/v1/places:searchText"
            query_str = " ".join(query_parts)
            payload = {
                "textQuery": f"{query_str} 餐廳", 
                "maxResultCount": req.spinCount, # 嚴格依照使用者選擇的數量抓取
                "languageCode": "zh-TW",
                "locationRestriction": {
                    "circle": {
                        "center": {"latitude": req.lat, "longitude": req.lng},
                        "radius": float(req.distance)
                    }
                }
            }
        else:
            places_url = "https://places.googleapis.com/v1/places:searchNearby"
            payload = {
                "includedTypes": ["restaurant"],
                "maxResultCount": req.spinCount, # 嚴格依照使用者選擇的數量抓取
                "languageCode": "zh-TW",
                "locationRestriction": {
                    "circle": {
                        "center": {"latitude": req.lat, "longitude": req.lng},
                        "radius": float(req.distance)
                    }
                }
            }

        async with httpx.AsyncClient() as client:
            resp = await client.post(places_url, json=payload, headers=headers)
            if resp.status_code == 200:
                places_data = resp.json().get("places", [])
                for p in places_data:
                    place_id = p.get("id")
                    name = p.get("displayName", {}).get("text", "未知餐廳")
                    rating = p.get("rating", 0.0)
                    loc = p.get("location", {})
                    p_lat, p_lng = loc.get("latitude"), loc.get("longitude")
                    price_level = p.get("priceLevel")
                    p_types = p.get("types", ["restaurant"])
                    p_type = p_types[0] if p_types else "restaurant"
                    opening_hours_str = json.dumps(p.get("regularOpeningHours", {}), ensure_ascii=False)

                    sql = text("""
                        INSERT INTO restaurants (google_place_id, name, type, rating, price_level, opening_hours, geom)
                        VALUES (:place_id, :name, :type, :rating, :price_level, :opening_hours, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
                        ON CONFLICT (google_place_id) DO NOTHING;
                    """)
                    await db.execute(sql, {
                        "place_id": place_id, "name": name, "type": p_type,
                        "rating": rating, "price_level": price_level, 
                        "opening_hours": opening_hours_str,
                        "lng": p_lng, "lat": p_lat
                    })
                await db.commit()

        user_point = ST_SetSRID(ST_MakePoint(req.lng, req.lat), 4326)
        from sqlalchemy import cast
        from geoalchemy2 import Geography

        query = select(Restaurant).where(
            func.ST_DWithin(cast(Restaurant.geom, Geography), cast(user_point, Geography), float(req.distance))
        )

        if req.priceLevels and len(req.priceLevels) > 0:
            query = query.where(Restaurant.price_level.in_(req.priceLevels))

        db_result = await db.execute(query)
        restaurants = db_result.scalars().all()

        formatted_list = [
            {
                "id": r.google_place_id,
                "name": r.name, 
                "type": r.type, 
                "rating": float(r.rating),
                "priceLevel": r.price_level,
                "openingHours": json.loads(r.opening_hours) if r.opening_hours else None
            } 
            for r in restaurants
        ]

        if not formatted_list:
            formatted_list = [{"name": "附近沒找到符合條件的美食", "type": "N/A", "rating": 0}]

        # 直接回傳結果，不需要再用 random.sample 抽樣，因為數量已經剛好了
        return {
            "status": "success",
            "results": formatted_list
        }

    except Exception as e:
        print(f"後端發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)