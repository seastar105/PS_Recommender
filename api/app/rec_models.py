from database import DBHelper
from model import Tag, Problem


class AbsModel(object):
    def __init__(self):
        pass

    def inference(self, handle: str):
        pass


class RecModel(AbsModel):
    def __init__(self):
        self.db = DBHelper('./.mylogin.cnf')
        tags = self.db.query('select * from tag')
        self.tag_name_map = {tag['id']: tag['name'] for tag in tags}

    def inference(self, handle: str):
        if not self.db.check_user(handle):
            return None
        query_string = f' \
            SELECT * \
            FROM tag \
            ORDER BY RAND() \
            LIMIT 6'
        tags = self.db.query(query_string)

        problems = dict()
        for tag in tags:
            tag_id = tag['id']
            tag_name = tag['name']
            query_string = f' \
                SELECT problem.id, problem.tier, problem.exp \
                FROM problem join problem_tag on problem.id = problem_tag.problem_id \
                WHERE problem_tag.tag_id = {tag_id} \
                LIMIT 3'
            problems[tag_name] = list()
            for problem in self.db.query(query_string):
                tag_ids = self.db.get_problem_tags(problem['id'])['tags']
                problems[tag_name].append(Problem(
                    id=problem['id'],
                    tier=problem['tier'],
                    tag=[self.tag_name_map[tag_id] for tag_id in tag_ids]
                ))
        strong_tag = [tag['name'] for tag in tags[:len(tags)//2]]
        weak_tag = [tag['name'] for tag in tags[len(tags)//2:]]
        tags = Tag(
            strong=strong_tag,
            weak=weak_tag
        )

        return tags, problems
