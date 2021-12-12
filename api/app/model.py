from pydantic import BaseModel
from typing import Optional, List, Dict


class User(BaseModel):
    id: Optional[str] = None
    school: Optional[str] = None
    tier: Optional[str] = None
    ranking: Optional[int] = None
    solved: Optional[int] = None
    rating: Optional[int] = None


class Tag(BaseModel):
    strong: List[str]
    weak: List[str]


class Problem(BaseModel):
    id: int
    tier: int
    tag: List[str]


class Recommend(BaseModel):
    code: int
    datetime: str
    user: User
    tag: Optional[Tag]
    problems: Optional[Dict[str, List[Problem]]]