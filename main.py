# main.py
from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel

app = FastAPI()

# Pydantic 모델 정의
class Item(BaseModel):
    name: str
    description: str

# 데이터베이스 함수
def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn

# API 엔드포인트
@app.post("/items/", response_model=dict)
async def create_item(item: Item):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, description) VALUES (?, ?)",
                   (item.name, item.description))
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return {"id": item_id, "name": item.name, "description": item.description}

@app.get("/items/{item_id}", response_model=dict)
async def read_item(item_id: int):
    conn = get_db_connection()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item["id"], "name": item["name"], "description": item["description"]}


@app.put("/items/{item_id}", response_model=dict)
async def update_item(item_id: int, item: Item):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET name = ?, description = ? WHERE id = ?", (item.name, item.description, item_id))
    if cursor.rowcount == 0:
        cursor.execute("INSERT INTO items (name, description) VALUES (?, ?)", (item.name, item.description))
    conn.commit()
    conn.close()
    return {"id":item_id, "name":item.name, "description":item.description}

@app.delete("/items/{item_id}", response_model=dict)
async def delete_item(item_id:int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code = 404, detail="Item not found")
    return {"message": f"Item with id {item_id} deleted successfully"}

