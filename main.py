from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from models import Word
from sqlalchemy import update
from typing import List
from sqlalchemy import select, func
from fastapi import HTTPException,Header,status
from fastapi.middleware.cors import CORSMiddleware
from database import get_db
import os
import secrets
import schemas

app = FastAPI(title="EGE-4 API")

async def verify_admin(x_admin_key: str = Header(None)):
    secret = os.getenv("ADMIN_SECRET")
    

    if not secret:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка конфигурации сервера"
        )
  
    if not x_admin_key or not secrets.compare_digest(x_admin_key, secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="У вас нет прав для выполнения этого действия"
        )

origins = [
    "http://localhost",
    "http://localhost:8000",
     "http://127.0.0.1:5500",
    "http://localhost:5500"
    "https://ege4-production.up.railway.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], #
)
@app.post("/words/bulk", response_model=List[schemas.WordResponse])
async def add_multiple_words(words_list: List[schemas.WordCreate], db: AsyncSession = Depends(get_db),_ = Depends(verify_admin)):
    """
    Эндпоинт для добавления сразу нескольких слов (массива).
    """
    new_words = [Word(word=item.word, accent_index=item.accent_index) for item in words_list]
    db.add_all(new_words)
  
    
    try:

        await db.commit()
        for word in new_words:
            await db.refresh(word)
            
        return new_words
        
    except Exception as e:
        await db.rollback()
        print(f"Ошибка массового добавления: {e}")
        raise HTTPException(
            status_code=400, 
            detail="Ошибка при сохранении. Возможно, одно или несколько слов уже существуют в базе"
        )
    


@app.post("/words/", response_model=schemas.WordResponse)
async def add_word(word: schemas.WordCreate, db: AsyncSession = Depends(get_db),_ = Depends(verify_admin)):

    new_word = Word(word=word.word,accent_index=word.accent_index)
    db.add(new_word)
    await db.commit()
    await db.refresh(new_word)
    print(new_word)
    return new_word



@app.get("/words/random", response_model=List[schemas.WordResponse])
async def get_random_words(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт выдает случайную партию слов для тренировки.
    По умолчанию 20 штук, но можно запросить любое количество (limit)
    """
    

    query = select(Word).order_by(func.random()).limit(limit)
    
    result = await db.execute(query)
    
    words = result.scalars().all()
    print(words)
    return words

@app.delete("/words/{word_id}")
async def delete_word_by_id(word_id: int, db: AsyncSession = Depends(get_db), _ = Depends(verify_admin)):
    """
    Эндпоинт для удаления конкретного слова по его ID из базы данных.
    Доступно только администратору.
    """
  
    word_to_delete = await db.get(Word, word_id)
    
    
    if not word_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Слово с ID {word_id} не найдено"
        )
    
 
    await db.delete(word_to_delete)
    await db.commit()
    
    return {"message": f"Слово '{word_to_delete.word}' (ID: {word_id}) успешно удалено"}

@app.post("/danger/reset-db")
async def danger_reset_db(db: AsyncSession = Depends(get_db), _ = Depends(verify_admin)):
    await db.execute(text("TRUNCATE TABLE words RESTART IDENTITY"))
    await db.commit()
    return {"message": "Таблица слов очищена"}

