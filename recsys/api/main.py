import os
import sys
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import datetime
from api.model import Recommend, User, Tag, Problem
from reco.reco import Model

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from utils import DBHelper

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


db = DBHelper('./.mylogin.cnf')
model = Model()

@app.get("/")
def read_root():
    return {"Hello": "World"}


def get_problem_tag_names(problem_id):
    query_string = f'\
                SELECT tag.name \
                FROM tag join (\
                    SELECT tag_id \
                    FROM problem join problem_tag on problem.id = problem_tag.problem_id \
                    WHERE problem.id = {problem_id}) as t1 on tag.id = t1.tag_id'
    return [row['name'] for row in db.query(query_string)]

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
    if not db.check_user(handle):
        return res

    # Available user, status code 200
    res.code = 200

    strong_tag, weak_tag, problems = model.recommend(handle)
    res.tag = Tag(
        strong=strong_tag,
        weak=weak_tag
    )

    res.problems = dict()
    for k, v in problems.items():
        res.problems[k] = list()
        for problem_id in v:
            row = db.query(f'SELECT * FROM problem where id={problem_id}')[0]
            res.problems[k].append(Problem(
                id=problem_id,
                name=row['name'],
                tier=row['tier'],
                tag=get_problem_tag_names(problem_id)
            ))

    return res
