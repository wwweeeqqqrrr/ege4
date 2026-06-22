from pydantic import BaseModel, ConfigDict
from typing import List
class WordCreate(BaseModel):
    word: str
    accent_index: int
    

class WordResponse(BaseModel):
    id: int
    word: str
    accent_index: int
    
    model_config = ConfigDict(from_attributes=True)

class SessionStats(BaseModel):
    user_id: int
    all_words: List[int]
    mistaken_words: List[int]