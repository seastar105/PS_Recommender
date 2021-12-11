<<<<<<< Updated upstream
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from database import DBHelper
import datetime
from model import Response, Problem
from rec_models import RecModel
db = DBHelper('./.mylogin.cnf')
model = RecModel()

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@repeat_every(seconds=60*60)    # every an hour
def update_batch():
    pass


@app.get("/api/rec/{handle}")
def get_recommend(handle: str) -> Response:
    # Basic response body
    res = Response(
        code=404,
        datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    rec = model.inference(handle)

    if rec is None:
        return res

    # Available user, status code 200
    res.code = 200
    res.handle = handle
    res.tag, res.problems = rec

    return res
=======
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from database import DBHelper
import datetime
from model import Response, Problem
from rec_models import RecModel
db = DBHelper('./.mylogin.cnf')
model = RecModel()

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@repeat_every(seconds=60*60)    # every an hour
def update_batch():
    pass


@app.get("/api/rec/{handle}")
def get_recommend(handle: str) -> Response:
    # Basic response body
    res = Response(
        code=404,
        datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    rec = model.inference(handle)

    if rec is None:
        return res

    # Available user, status code 200
    res.code = 200
    res.handle = handle
    res.tag, res.problems = rec

    return res
>>>>>>> Stashed changes
