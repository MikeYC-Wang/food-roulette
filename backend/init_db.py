import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

from main import Base, Restaurant, User, SpinHistory, CustomRestaurant, FavoriteRestaurant, DietRecord

# 載入 .env 環境變數
load_dotenv()

# 取得資料庫連線設定
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "food_roulette_db")
    DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

async def init_database():
    print("正在準備連線至資料庫...")
    
    # 建立非同步引擎
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        print("⚠️ 正在刪除舊資料表 (為了讓新欄位順利套用)...")
        # 先 Drop 掉所有舊表
        await conn.run_sync(Base.metadata.drop_all)
        
        print("開始建立全新資料表...")
        # 再重新 Create，這樣就會包含最新的 DietRecord 欄位了
        await conn.run_sync(Base.metadata.create_all)
        
    print("✅ 所有資料表已重新建立，結構完美同步！")
    
    # 釋放連線資源
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())