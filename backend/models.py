from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional, Dict

class Settings(BaseModel):
    """
    Settings for model training API
    """
    PORT: int = Field(default=8000)
    HOST: str = Field(default='0.0.0.0')


class Genedr(str, Enum):
    m = "M"
    f = "Ж"


class SavedMessages(BaseModel):
    text_info: List[Dict]  # {"rank": i + 1, "text": text, "relevance": round(s, 3), "index": idx}


class UserBase(BaseModel):
    login: str
    name: str
    gender: Optional[Genedr] = None
    age: Optional[int] = None
    saved: Optional[SavedMessages] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    login: str
    password: str


class SearchType(str, Enum):
    w2v = "w2v"
    tfidf = "tfidf"


class SearchRequest(BaseModel):
    query: str
    quantity: int #= Field(..., gt=0, description="Количество результатов")
    search_type: SearchType


class SearchResult(BaseModel):
    text_info: List[Dict]  # {"rank": i + 1, "text": text, "relevance": round(s, 3), "index": idx}
    quantity: int
    query: str
    search_type: SearchType
    time: str


class SaveRequest(BaseModel):
    message_id: str
    user_name: str
    saved_query: Optional[str] = None


class CorporaInfo(BaseModel):
    num_texts: int
    num_tokens: int
