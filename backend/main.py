from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import random

app = FastAPI()

# 1. 設定 CORS，允許前端 Vite 預設的 5173 連接埠存取
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 定義資料結構 (Pydantic Model)
class SpinRequest(BaseModel):
    lat: float
    lng: float
    distance: int
    types: List[str]
    avoids: List[str]

# 3. 撰寫第一個接口：接收定位與條件，回傳隨機餐廳名單
@app.post("/api/spin")
async def get_roulette_data(req: SpinRequest):
    print(f"收到請求 - 定位: ({req.lat}, {req.lng}), 距離: {req.distance}m")
    print(f"篩選條件 - 想要: {req.types}, 避雷: {req.avoids}")

    # 模擬資料庫查詢結果 (下一階段我們會串接真實資料庫)
    all_mock_restaurants = [
        {"name": "老王控肉飯"}, {"name": "金仙排骨飯"}, 
        {"name": "強尼健康餐"}, {"name": "阿明乾麵"}, 
        {"name": "隔壁素食"}, {"name": "巷口大腸麵線"},
        {"name": "極品紅燒肉"}, {"name": "超值便當店"}
    ]
    
    # 隨機挑選 6 個回傳給前端
    selected = random.sample(all_mock_restaurants, 6)
    
    return {
        "status": "success",
        "results": selected
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)