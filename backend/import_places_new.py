import os
import asyncio
import httpx
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
# 新版 API 的 Nearby Search 端點
PLACES_URL = "https://places.googleapis.com/v1/places:searchNearby"

async def fetch_restaurants_from_google(lat, lng, radius=1000.0):
    # 關鍵：X-Goog-FieldMask 新增了 places.priceLevel
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.rating,places.location,places.types,places.priceLevel"
    }

    # 搜尋條件：指定餐廳、範圍與地點
    payload = {
        "includedTypes": ["restaurant"],
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": radius
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(PLACES_URL, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"❌ API 請求失敗: {response.text}")
            return []
        
        return response.json().get("places", [])

async def main():
    # 以南港展覽館附近為例
    places = await fetch_restaurants_from_google(25.0589, 121.6117)
    
    if not places:
        print("查無餐廳資料，請檢查 API Key 是否正確。")
        return

    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        for p in places:
            # 解析新版 API 格式
            place_id = p.get("id")
            name = p.get("displayName", {}).get("text", "未知餐廳")
            rating = p.get("rating", 0.0)
            loc = p.get("location", {})
            p_lat, p_lng = loc.get("latitude"), loc.get("longitude")
            
            # 取得價位資料 (若無則預設為 None)
            price_level = p.get("priceLevel")
            
            # 取得主類別
            p_types = p.get("types", ["restaurant"])
            p_type = p_types[0] if p_types else "restaurant"

            # 插入資料庫：更新 SQL 加入 price_level
            sql = text("""
                INSERT INTO restaurants (google_place_id, name, type, rating, price_level, geom)
                VALUES (:place_id, :name, :type, :rating, :price_level, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
                ON CONFLICT (google_place_id) 
                DO UPDATE SET 
                    rating = EXCLUDED.rating, 
                    name = EXCLUDED.name,
                    price_level = EXCLUDED.price_level;
            """)
            
            await conn.execute(sql, {
                "place_id": place_id,
                "name": name,
                "type": p_type,
                "rating": rating,
                "price_level": price_level, # 傳入價位參數
                "lng": p_lng,
                "lat": p_lat
            })
            print(f"✅ 已匯入：{name} ({rating}星, 價位: {price_level})")

    print(f"\n🎉 同步完成！共匯入 {len(places)} 筆真實餐廳。")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())