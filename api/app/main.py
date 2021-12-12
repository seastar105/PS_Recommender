from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from database import DBHelper
import datetime
from model import Recommend, User
from rec_models import RecModel

db = DBHelper('./.mylogin.cnf')
model = RecModel()
origins = [
    "*"
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/rec/{handle}")
def get_recommend(handle: str, response: Response) -> Recommend:

    # NOTE : Why fastapi Middleware not working????
    response.headers["Access-Control-Allow-Origin"] = "*"

    user = User(id=handle)
    res = Recommend(
        code=404,
        datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user=user
    )

    rec = model.inference(handle)

    if rec is None:
        return res

    # Available user, status code 200
    res.code = 200
    res.tag, res.problems = rec

    return res
