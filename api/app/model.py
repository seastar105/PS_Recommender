<<<<<<< Updated upstream
from pydantic import BaseModel
from typing import Optional, List, Dict


class Tag(BaseModel):
    strong: List[str]
    weak: List[str]


class Problem(BaseModel):
    id: int
    tier: int
    tag: List[str]


class Response(BaseModel):
    code: int
    datetime: str
    handle: Optional[str]
    tag: Optional[Tag]
=======
from pydantic import BaseModel
from typing import Optional, List, Dict


class Tag(BaseModel):
    strong: List[str]
    weak: List[str]


class Problem(BaseModel):
    id: int
    tier: int
    tag: List[str]


class Response(BaseModel):
    code: int
    datetime: str
    handle: Optional[str]
    tag: Optional[Tag]
>>>>>>> Stashed changes
    problems: Optional[Dict[str, List[Problem]]]