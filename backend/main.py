import os
import random
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

# 載入 .env 環境變數
load_dotenv()

# 資料庫連線設定
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "food_roulette_db")
    DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# 建立非同步引擎
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# 定義餐廳資料表模型
class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    google_place_id: Mapped[Optional[str]] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column()
    rating: Mapped[float] = mapped_column()
    # 👉 新增 price_level 欄位
    price_level: Mapped[Optional[str]] = mapped_column()
    geom: Mapped[any] = mapped_column(Geometry("POINT", srid=4326))

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

app = FastAPI(title="食來運轉 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👉 定義前端請求的資料結構，加入 priceLevels
class SpinRequest(BaseModel):
    lat: float
    lng: float
    distance: int
    types: List[str]
    avoids: List[str]
    priceLevels: List[str] = [] # 預設為空陣列

@app.get("/")
async def root():
    return {"message": "食來運轉後端 (PostGIS 版) 正常運作中！"}

@app.post("/api/spin")
async def get_roulette_data(req: SpinRequest, db: AsyncSession = Depends(get_db)):
    try:
        user_point = ST_SetSRID(ST_MakePoint(req.lng, req.lat), 4326)

        from sqlalchemy import cast
        from geoalchemy2 import Geography

        query = select(Restaurant).where(
            func.ST_DWithin(
                cast(Restaurant.geom, Geography),
                cast(user_point, Geography),
                float(req.distance)
            )
        )

        # 類型篩選
        if req.types and len(req.types) > 0:
            query = query.where(Restaurant.type.in_(req.types))
            
        # 價位篩選
        if req.priceLevels and len(req.priceLevels) > 0:
            query = query.where(Restaurant.price_level.in_(req.priceLevels))

        # 避雷篩選
        for avoid in req.avoids:
            if avoid == "不吃辣":
                query = query.where(~Restaurant.name.contains("辣"))
            elif avoid == "排除連鎖店":
                chains = ["麥當勞", "肯德基", "必勝客", "摩斯漢堡"]
                for chain in chains:
                    query = query.where(~Restaurant.name.contains(chain))

        db_result = await db.execute(query)
        restaurants = db_result.scalars().all()

        # 格式化輸出，加入 priceLevel 回傳給前端
        formatted_list = [
            {
                "id": r.google_place_id,
                "name": r.name, 
                "type": r.type, 
                "rating": float(r.rating),
                "priceLevel": r.price_level
            } 
            for r in restaurants
        ]

        if not formatted_list:
            formatted_list = [{"name": "附近沒找到美食", "type": "N/A", "rating": 0}]

        sample_size = min(len(formatted_list), 6)
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