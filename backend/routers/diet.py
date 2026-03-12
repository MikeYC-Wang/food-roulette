from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

# 從你的 main.py 匯入需要的工具與模型
from main import get_db, get_current_user, User, DietRecord

# 建立一個路由器，並加上前綴與標籤
router = APIRouter(prefix="/api/diet", tags=["Diet"])

# --- 定義接收資料的格式 (Pydantic Schema) ---
class DietRecordCreate(BaseModel):
    record_date: str
    meal_type: str
    food_name: str
    food_category: str
    price: int

# --- API 1: 新增一筆飲食紀錄 ---
@router.post("/record")
async def create_diet_record(
    req: DietRecordCreate, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    try:
        new_record = DietRecord(
            user_id=current_user.id,
            record_date=req.record_date,
            meal_type=req.meal_type,
            food_name=req.food_name,
            food_category=req.food_category,
            price=req.price
        )
        db.add(new_record)
        await db.commit()
        return {"status": "success", "message": "飲食紀錄已成功儲存！"}
    except Exception as e:
        print(f"儲存紀錄失敗: {str(e)}")
        raise HTTPException(status_code=500, detail="儲存失敗")

# --- API 2: 取得特定月份的總覽與花費 ---
@router.get("/stats")
async def get_diet_stats(
    month: str, # 格式例如: "2024-05"
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # 使用 SQL 尋找符合該月份的紀錄
    query = select(DietRecord).where(
        DietRecord.user_id == current_user.id,
        DietRecord.record_date.startswith(month)
    ).order_by(DietRecord.record_date.desc())
    
    result = await db.execute(query)
    records = result.scalars().all()

    # 計算總花費
    total_spent = sum(r.price for r in records)

    # 回傳給前端 (ECharts 會非常喜歡這種格式)
    return {
        "status": "success",
        "total_spent": total_spent,
        "records": [
            {
                "id": r.id,
                "date": r.record_date,
                "meal_type": r.meal_type,
                "name": r.food_name,
                "category": r.food_category,
                "price": r.price
            } for r in records
        ]
    }