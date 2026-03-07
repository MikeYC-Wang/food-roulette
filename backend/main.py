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

# 資料庫連線設定 (優先從環境變數讀取)
DATABASE_URL = os.getenv("DATABASE_URL")

# 如果 DATABASE_URL 未在 .env 定義，則手動組裝
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

# SQLAlchemy 模型基底
class Base(DeclarativeBase):
    pass

# 定義餐廳資料表模型
class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    # 新增 google_place_id 並設定為唯一值
    google_place_id: Mapped[Optional[str]] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column()
    rating: Mapped[float] = mapped_column()
    # 使用 Geometry 型別存放經緯度點位 (SRID 4326)
    geom: Mapped[any] = mapped_column(Geometry("POINT", srid=4326))

# 相依注入：取得資料庫連線
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

app = FastAPI(title="食來運轉 API")

# 設定 CORS 允許前端存取 (包含 5173 與 5174)
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

# 定義前端請求的資料結構
class SpinRequest(BaseModel):
    lat: float
    lng: float
    distance: int
    types: List[str]
    avoids: List[str]

@app.get("/")
async def root():
    return {"message": "食來運轉後端 (PostGIS 版) 正常運作中！"}

# 核心介面：抽籤邏輯
@app.post("/api/spin")
async def get_roulette_data(req: SpinRequest, db: AsyncSession = Depends(get_db)):
    try:
        # 1. 建立使用者目前座標點
        user_point = ST_SetSRID(ST_MakePoint(req.lng, req.lat), 4326)

        # 2. 建立空間查詢
        # 將 geometry 轉型為 geography，ST_DWithin 就會自動以「公尺」為單位
        from sqlalchemy import cast
        from geoalchemy2 import Geography

        query = select(Restaurant).where(
            func.ST_DWithin(
                cast(Restaurant.geom, Geography),
                cast(user_point, Geography),
                float(req.distance)  # 直接傳入公尺數，例如 500
            )
        )

        # 3. 套用類型篩選 (複選)
        if req.types and len(req.types) > 0:
            query = query.where(Restaurant.type.in_(req.types))

        # 4. 套用避雷篩選
        for avoid in req.avoids:
            if avoid == "不吃辣":
                query = query.where(~Restaurant.name.contains("辣"))
            elif avoid == "排除連鎖店":
                # 排除常見連鎖關鍵字 (範例)
                chains = ["麥當勞", "肯德基", "必勝客", "摩斯漢堡"]
                for chain in chains:
                    query = query.where(~Restaurant.name.contains(chain))

        # 執行查詢
        db_result = await db.execute(query)
        restaurants = db_result.scalars().all()

        # 格式化輸出
        formatted_list = [
            {"name": r.name, "type": r.type, "rating": float(r.rating)} 
            for r in restaurants
        ]

        # 如果找不到符合條件的餐廳，回傳預設項目避免輪盤空白
        if not formatted_list:
            formatted_list = [{"name": "附近沒找到美食", "type": "N/A", "rating": 0}]

        # 5. 從結果中隨機挑選最多 6 個
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
    # 固定使用 8001 埠號啟動
    uvicorn.run(app, host="127.0.0.1", port=8001)