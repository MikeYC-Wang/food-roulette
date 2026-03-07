import os
import asyncio
import httpx
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

# 從 .env 讀取設定
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# 新版 API 的端點 (Nearby Search)
ENDPOINT = "https://places.googleapis.com/v1/places:searchNearby"

async def fetch_real_restaurants(lat: float, lng: float, radius: float = 1000.0):
    """使用 Places API (New) 抓取餐廳"""
    
    # 關鍵：FieldMask。新版 API 強制要求此 Header，且這決定了你的費用
    # 我們只選取基本欄位，確保開發成本最低
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.rating,places.location,places.types"
    }

    # 設定搜尋條件
    payload = {
        "includedTypes": ["restaurant"], # 指定餐廳
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": radius
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(ENDPOINT, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"API 出錯: {response.text}")
            return []
        
        data = response.json()
        return data.get("places", [])

async def sync_to_db():
    # 以南港座標執行測試
    places = await fetch_real_restaurants(25.0589, 121.6117)
    
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        for p in places:
            # 注意新版的 displayName 是個物件
            name = p.get("displayName", {}).get("text", "未知店名")
            rating = p.get("rating", 0.0)
            loc = p.get("location", {})
            p_lat, p_lng = loc.get("latitude"), loc.get("longitude")
            
            # 取得主類別
            types = p.get("types", ["restaurant"])
            main_type = types[0] if types else "restaurant"

            # 插入或更新
            sql = text("""
                INSERT INTO restaurants (name, type, rating, geom)
                VALUES (:name, :type, :rating, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
                ON CONFLICT (name) DO UPDATE SET rating = EXCLUDED.rating;
            """)
            
            await conn.execute(sql, {
                "place_id": p.get("id"),
                "name": name,
                "type": main_type,
                "rating": rating,
                "lng": p_lng,
                "lat": p_lat
            })
            print(f"✅ 已存入: {name}")

    print("--- 真實資料同步完成 ---")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(sync_to_db())