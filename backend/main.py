import os
import random
import json
import httpx
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

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

class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    google_place_id: Mapped[Optional[str]] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column()
    rating: Mapped[float] = mapped_column()
    price_level: Mapped[Optional[str]] = mapped_column()
    # 👉 新增：將營業時間存為 JSON 字串，避免資料庫相容性問題
    opening_hours: Mapped[Optional[str]] = mapped_column(nullable=True)
    geom: Mapped[any] = mapped_column(Geometry("POINT", srid=4326))

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

app = FastAPI(title="食來運轉 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👉 更新：加入 spinCount (轉幾家餐廳)
class SpinRequest(BaseModel):
    lat: float
    lng: float
    distance: int
    types: List[str]
    avoids: List[str]
    priceLevels: List[str] = []
    spinCount: int = 6 # 預設 6 家

@app.get("/")
async def root():
    return {"message": "食來運轉後端 (動態抓取版) 正常運作中！"}

@app.post("/api/spin")
async def get_roulette_data(req: SpinRequest, db: AsyncSession = Depends(get_db)):
    try:
        # 1. 清空舊資料
        await db.execute(text("TRUNCATE TABLE restaurants RESTART IDENTITY CASCADE;"))
        
        # 2. 即時打 Google Places API
        places_url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": "places.id,places.displayName,places.rating,places.location,places.types,places.priceLevel,places.regularOpeningHours"
        }

        payload = {
            "includedTypes": ["restaurant"],
            "maxResultCount": req.spinCount,
            "languageCode": "zh-TW",
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": req.lat, "longitude": req.lng},
                    "radius": req.distance
                }
            }
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(places_url, json=payload, headers=headers)
            if resp.status_code == 200:
                places_data = resp.json().get("places", [])
                
                # ==========================================
                # 步驟 3: 將最新資料接到資料庫
                # ==========================================
                for p in places_data:
                    place_id = p.get("id")
                    name = p.get("displayName", {}).get("text", "未知餐廳")
                    rating = p.get("rating", 0.0)
                    loc = p.get("location", {})
                    p_lat, p_lng = loc.get("latitude"), loc.get("longitude")
                    price_level = p.get("priceLevel")
                    
                    p_types = p.get("types", ["restaurant"])
                    p_type = p_types[0] if p_types else "restaurant"
                    
                    # 處理營業時間轉為字串
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
                await db.commit() # 確認儲存

        # ==========================================
        # 步驟 4: 從資料庫進行條件篩選
        # ==========================================
        user_point = ST_SetSRID(ST_MakePoint(req.lng, req.lat), 4326)
        from sqlalchemy import cast
        from geoalchemy2 import Geography

        query = select(Restaurant).where(
            func.ST_DWithin(cast(Restaurant.geom, Geography), cast(user_point, Geography), float(req.distance))
        )

        if req.types and len(req.types) > 0:
            query = query.where(Restaurant.type.in_(req.types))
        if req.priceLevels and len(req.priceLevels) > 0:
            query = query.where(Restaurant.price_level.in_(req.priceLevels))

        for avoid in req.avoids:
            if avoid == "不吃辣":
                query = query.where(~Restaurant.name.contains("辣"))
            elif avoid == "排除連鎖店":
                for chain in ["麥當勞", "肯德基", "必勝客", "摩斯漢堡"]:
                    query = query.where(~Restaurant.name.contains(chain))

        db_result = await db.execute(query)
        restaurants = db_result.scalars().all()

        formatted_list = [
            {
                "id": r.google_place_id,
                "name": r.name, 
                "type": r.type, 
                "rating": float(r.rating),
                "priceLevel": r.price_level,
                "openingHours": json.loads(r.opening_hours) if r.opening_hours else None # 👉 回傳營業時間物件
            } 
            for r in restaurants
        ]

        if not formatted_list:
            formatted_list = [{"name": "附近沒找到美食", "type": "N/A", "rating": 0}]

        # ==========================================
        # 步驟 5: 根據使用者設定的 spinCount 決定數量
        # ==========================================
        sample_size = min(len(formatted_list), req.spinCount)
        final_selection = random.sample(formatted_list, sample_size) if formatted_list else []

        return {
            "status": "success",
            "results": final_selection
        }

    except Exception as e:
        print(f"後端發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)