import requests
from bs4 import BeautifulSoup
from database import DBHelper

boj_url = "https://www.acmicpc.net"
solved_url = "https://solved.ac"
db = DBHelper('.mylogin.cnf')
tier_to_exp = dict()
tag_id_to_name = dict()
current_tag_set = set()

def initialize():
    res = db.query('select * from tier_exp')
    for row in res:
        tier_to_exp[row['tier']] = row['exp']
    res = db.query('select * from tag')
    for row in res:
        tag_id_to_name[row['id']] = row['name']
        current_tag_set.add(row['name'])


def get_last_problem():
    url = "https://www.acmicpc.net/problemset?sort=no_desc"
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    last_num = int(soup.find('table', id='problemset').find('tbody').find('tr').find('td').text)
    return last_num


def update_problems():
    # can get problem by id array with query param at most 100
    start_num = 1000
    last_num = get_last_problem()
    lookup_url = solved_url + "/api/v3/problem/lookup"
    batch_size = 100
    tag_set = set()
    for pid in range(start_num, last_num+1, batch_size):
        id_list = ",".join([str(i) for i in range(pid, pid+batch_size)])
        payload = {"problemIds":id_list}
        r = requests.get(lookup_url, params=payload)
        for problem in r.json():
            problem_id = problem['problemId']
            name = problem['titleKo']
            tier = problem['level']
            exp = tier_to_exp[exp]
            query_string = f'INSERT INTO problem (id, tier, exp, name) \
                                    VALUES ({problem_id}, {tier}, {exp}, \'{name}\'}) \
                                    ON DUPLICATE KEY UPDATE \
                                    tier={tier}, \
                                    exp={exp}, \
                                    name=\'{name}\''
            db.query(query_string)
            tag_in_db = set(db.get_problem_tags(problem_id)['tags'])
            for tag in problem['tags']:
                tag_name = tag['key']
                tag_set.append(tag_name)



if __name__ == "__main__":
    initialize()