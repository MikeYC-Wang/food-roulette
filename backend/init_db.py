import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from main import Base, Restaurant, User, SpinHistory, CustomRestaurant
from main import Base, Restaurant, User, SpinHistory, CustomRestaurant, FavoriteRestaurant

# ⚠️ 這裡非常重要：必須引入你在 main.py 定義的 Base 與所有資料表模型
# 新增了 User 和 SpinHistory，這樣 SQLAlchemy 才知道要建這三張表
from main import Base, Restaurant, User, SpinHistory

# 載入 .env 環境變數
load_dotenv()

# 取得資料庫連線設定 (邏輯與 main.py 一致)
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
        print("開始建立資料表...")
        
        # 讓 SQLAlchemy 自動比對並建立所有繼承自 Base 的資料表
        await conn.run_sync(Base.metadata.create_all)
        
    print("✅ 資料表 'restaurants', 'users', 'spin_history' 建立/更新成功！")
    
    # 釋放連線資源
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())