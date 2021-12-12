import os
import sys
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional, List, Tuple
import time
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils import DBHelper

class Problem(BaseModel):
    id: int
    tier: int
    name: str
    tag: List[str]

class User(BaseModel):
    id: int
    handle: str
    solved: int
    submit: int


boj_url = "https://www.acmicpc.net"
solved_url = "https://solved.ac"
db = DBHelper('.mylogin.cnf')
tier_to_exp = dict()
tag_id_to_name = dict()
tag_name_to_id = dict()
handle_to_id = dict()
id_to_handle = dict()

def initialize():
    res = db.query('select * from tier_exp')
    for row in res:
        tier_to_exp[row['tier']] = row['exp']
    res = db.query('select * from tag')
    for row in res:
        tag_id_to_name[row['id']] = row['name']
        tag_name_to_id[row['name']] = row['id']
    res = db.query('select * from user')
    for row in res:
        handle_to_id[row['handle']] = row['id']
        id_to_handle[row['id']] = row['handle']


def get_last_problem():
    url = "https://www.acmicpc.net/problemset?sort=no_desc"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features='html.parser')
    last_num = int(soup.find('table', id='problemset').find('tbody').find('tr').find('td').text)
    return last_num


def update_problems():
    # can get problem by id array with query param at most 100

    # 1. fetch all problems and tags from db
    problems = db.query('select * from problem')
    db_problem_list = dict()
    db_problem_tags = dict()

    for p in problems:
        db_problem_list[p['id']] = Problem(
            id=p['id'],
            tier=p['tier'],
            name=str(p['name']),
            tag=list()
        )
        db_problem_tags[p['id']] = set()

    for pair in db.query('select * from problem_tag'):
        pid = pair['problem_id']
        tag_id = pair['tag_id']
        tag_name = tag_id_to_name[tag_id]
        db_problem_tags[pid].add(tag_name)

    db_all_tag = set()
    for tag in db.query('select * from tag'):
        db_all_tag.add(tag['name'])

    # 2. fetch problems from solved.ac
    start_num = 1000
    last_num = get_last_problem()
    lookup_url = solved_url + "/api/v3/problem/lookup"
    batch_size = 100

    for batch_start in range(start_num, last_num+1, batch_size):
        id_list = ",".join([str(i) for i in range(batch_start, min(last_num+1,batch_start+batch_size))])
        payload = {"problemIds":id_list}
        r = requests.get(lookup_url, params=payload)
        if r.status_code != 200:
            print("Request Failed")
            print(r.text)
            exit(-1)
        for problem in r.json():
            problem_id = problem['problemId']
            if problem_id == 20307:
                continue # RREF sad
            name = problem['titleKo']
            tier = problem['level']
            exp = tier_to_exp[tier]
            tags = set(d['key'] for d in problem['tags'])

            # check if problem update is necessary
            if problem_id not in db_problem_list:
                # new problem
                db.query(f'INSERT INTO problem (id, tier, exp, name) \
                        VALUES ({problem_id}, {tier}, {exp}, \'{name}\')')

            elif db_problem_list[problem_id].tier != tier or db_problem_list[problem_id].name != name:
                # update problem
                db.query(f'UPDATE problem SET tier={tier}, exp={exp}, name=\'{name}\' WHERE id={problem_id}')

            # check if there's new tag
            for tag_name in tags:
                if tag_name not in db_all_tag:
                    tag_id = len(db_all_tag) + 1
                    db.query(f'INSERT INTO tag(id, name) VALUES({tag_id}, \"{tag_name}\")')
                    tag_name_to_id[tag_name] = tag_id
                    tag_id_to_name[tag_id] = tag_name
                    db_all_tag.add(tag_name)

            # check if tag set is different
            db_tag_set = db_problem_tags.get(problem_id, set())
            if tags != db_tag_set:
                to_be_inserted = tags - db_tag_set
                to_be_deleted = db_tag_set - tags

                for tag_name in to_be_inserted:
                    tag_id = tag_name_to_id[tag_name]
                    db.query(f'INSERT INTO problem_tag(problem_id, tag_id) VALUES({problem_id}, {tag_id})')

                for tag_name in to_be_deleted:
                    tag_id = tag_name_to_id[tag_name]
                    db.query(f'DELETE FROM problem_tag WHERE problem_id={problem_id} AND tag_id={tag_id}')


def get_user_info(r) -> Tuple[int, int, List[int]]:
    soup = BeautifulSoup(r.text, features='html.parser')
    ac_list = list()
    for ac in soup.find("div", {"class": "problem-list"}).find_all('a'):
        ac_list.append(int(ac.text))
    res = soup.find('table', {"id": "statics"}).find_all('tr')
    solved, submit = res[1].find('td').text, res[3].find('td').text
    return solved, submit, set(ac_list)

def update_users():
    # update user and ac
    # fetch all users from db
    all_users = dict()
    for row in db.query('select * from user'):
        all_users[row['handle']] = User(
            id=row['id'],
            handle=row['handle'],
            solved=-1 if row['solved'] is None else row['solved'],
            submit=-1 if row['submit'] is None else row['submit'],
        )

    # filter updating user while iterating rank pages
    update_user = []

    for page_num in range(1, 601):
        r = requests.get(boj_url + f'/ranklist/{page_num}')
        soup = BeautifulSoup(r.text, features='html.parser')
        tables = soup.find('table', id='ranklist')
        rows = tables.find_all('tr')
        for row in rows[1:]:
            info = [elem.text for elem in row.find_all('td')]
            handle, solved, submit = info[1], int(info[3]), int(info[4])
            if handle not in all_users or all_users[handle].solved != solved:
                update_user.append(handle)
        if page_num % 10 == 0:
            print(page_num)
        time.sleep(1)

    print("ranklist done", len(update_user), "will be updated")
    user_cnt = 0
    for handle in update_user:
        r = requests.get(boj_url + f'/user/{handle}')
        if r.status_code != 200:
            print("Request Failed")
            print(handle, r.text)
            exit(-1)
        solved, submit, ac_set = get_user_info(r)
        db_solved = set(db.get_user_problems(handle))

        if not db.check_user(handle):
            db.query(f'INSERT INTO user(handle, solved, submit) VALUES(\'{handle}\', {solved}, {submit})')
            user_id = db.query(f'SELECT * from user where handle=\'{handle}\'')
            handle_to_id[handle] = user_id
            id_to_handle[user_id] = handle
        else:
            db.query(f'UPDATE user SET solved={solved}, submit={submit} WHERE handle = \'{handle}\'')

        user_id = handle_to_id[handle]

        for problem_id in ac_set - db_solved:
            db.query(f'INSERT INTO ac(problem_id, user_id) VALUES({problem_id}, {user_id})')
        user_cnt += 1

        if user_cnt % 10 == 0:
            print(user_cnt)


if __name__ == "__main__":
    initialize()
    # update_problems()
    update_users()
