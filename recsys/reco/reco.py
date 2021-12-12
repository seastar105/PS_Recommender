import os
import json
import sys
import math
import bisect
import random

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from n2 import HnswIndex
from utils import DBHelper

core_tag = [1, 2, 3, 4, 5, 6, 7, 9, 13, 14, 15, 20, 22, 23, 24, 27, 38, 41, 52, 53]
idx2tag = {1:"math", 2:"implementation", 3:"dp", 4:"graphs", 5:"data_structures",
            6:"string", 7:"greedy", 9:"bruteforcing", 14:"geometry", 13:"number_theory",
            15:"binary_search", 20:"combinatorics", 23:"ad_hoc", 22:"constructive", 24:"bitmask",
            27:"divide_and_conquer", 38:"flow", 41:"game_theory", 53:"probability", 52:"hashing"}
tag2idx = {v:k for k,v in idx2tag.items()}
exp_table = [480, 672, 954, 1374, 1992,
            2909, 4276, 6329, 9430, 14145, 
            21288, 32145, 48699, 74023, 112885,
            172714, 265117, 408280, 630792, 977727,
            1520366, 2371771, 3711822, 5827560, 9178407,
            14501883, 22985485, 36546921, 58292339, 93267742]

class Model(object):
    def __init__(self):
        self.u = HnswIndex(179, 'angular')
        self.u.load('./reco/userModel.n2')

        self.idx2handle = dict()
        self.handle2idx = dict()

        fin = open('./reco/handle2idx', 'r')

        for _ in range(39839):
            idx, handle = fin.readline().split()
            self.idx2handle[idx] = handle.lower()
            self.handle2idx[handle.lower()] = idx
        
        self.problem_tags = []
        for _ in range(1000):
            self.problem_tags.append([])
        
        last_num = db.query('SELECT id FROM problem ORDER BY id DESC LIMIT 1')[0]['id']
        
        for pid in range(1000, last_num + 1):
            if db.query(f'SELECT * FROM problem WHERE id = \'{pid}\'') == False:
                self.problem_tags.append([])
            tags = db.get_problem_tags(pid)
            #print(pid, tags)
            self.problem_tags.append(tags)
    
    def getNeighbors(self, handle:str):
        handle = handle.lower()
        targetRank = int(self.handle2idx[handle]) - 1

        k = 11
        strong_neighbor_ids = self.u.search_by_id(targetRank, k)

        strong = []
        for idx in strong_neighbor_ids:
            if idx == targetRank:
                continue
            strong.append(self.idx2handle[str(idx + 1)])

        weak = []
        for idx in range(max(targetRank-9,1), min(targetRank+12, 39840)):
            if idx == targetRank + 1:
                continue
            weak.append(self.idx2handle[str(idx)])

        return strong, weak

    def strong_weak(self, handle:str):
        strong = []
        weak = []

        targetRank = int(self.handle2idx[handle])
        fpath = './reco/userVec.json'

        userList = []
        with open(fpath, 'r') as json_file:
            json_data = json.load(json_file)
            for i in range(max(targetRank-10, 1), min(targetRank+11, 39840)):
                lst = [i] + json_data[str(i)]
                userList.append(lst)
        
        for tagidx in core_tag:
            tagavg = []
            myavg = 0
            for user in userList:
                S = 0
                for x in range(1, len(user)):
                    if x in core_tag:
                        S += user[x]
                tagavg.append(user[tagidx] / S)
                if user[0] == targetRank:
                    if user[tagidx] == 0: 
                        break
                    myavg = user[tagidx] / S

            if len(tagavg) == 0 or user[tagidx] == 0:
                continue
            avg = sum(tagavg) / len(tagavg)
            if avg < myavg:
                strong.append((myavg, tagidx))
            else:
                weak.append((myavg, tagidx))
        
        strong.sort()
        strong.reverse()
        weak.sort()
        ret_strong = []
        ret_weak = []
        for x in strong:
            ret_strong.append(idx2tag[x[1]])
            if len(ret_strong) == 5:
                break
        for x in weak:
            ret_weak.append(idx2tag[x[1]])
            if len(ret_weak) == 5:
                break
        
        return ret_strong, ret_weak

    def recommend(self, handle:str):
        strong_neighbors, weak_neighbors = self.getNeighbors(handle)
        strong_tags, weak_tags = self.strong_weak(handle)

        unsolved = set()
        solved = db.get_user_problems(handle)
        for neighbors in strong_neighbors:
            unsolved |= set(db.get_user_problems(neighbors))
        for neighbors in weak_neighbors:
            unsolved |= set(db.get_user_problems(neighbors))
        unsolved -= set(solved)


        strong_list = [[] for _ in range(len(strong_tags))]
        weak_list = [[] for _ in range(len(weak_tags))]

        strong_exps = [0 for _ in range(len(strong_tags))]
        strong_cnt = [0 for _ in range(len(strong_tags))]
        weak_exps = [0 for _ in range(len(weak_tags))]
        weak_cnt = [0 for _ in range(len(weak_tags))]
        weaks = [[] for _ in range(len(weak_tags))]

        topKproblems = db.topk_problems(handle, 200)
        for problem in topKproblems:
            #print(problem)
            tags = self.problem_tags[problem['id']]
            for tag in tags['tags']:
                if idx2tag.get(tag) == None:
                    continue
                if idx2tag[tag] in strong_tags:
                    strong_exps[strong_tags.index(idx2tag[tag])] += problem['exp']
                    strong_cnt[strong_tags.index(idx2tag[tag])] += 1
        
        
        for problem in solved:
           tags = self.problem_tags[problem]
           for tag in tags['tags']:
                if idx2tag.get(tag) == None:
                    continue
                if idx2tag[tag] in weak_tags:
                    weaks[weak_tags.index(idx2tag[tag])].append(exp_table.index(db.get_problem_exp(problem)[0]['exp']) + 1)
                    weak_cnt[weak_tags.index(idx2tag[tag])] += 1
        
        for i in range(len(strong_exps)):
            if strong_cnt[i] != 0:
                strong_exps[i] /= strong_cnt[i]        
        for i in range(len(weak_exps)):
            weaks[i].sort()
            if weak_cnt[i]//2 != 0:
                weak_exps[i] = sum(weaks[i][(len(weaks[i])+1)//2:])
                weak_exps[i] /= (weak_cnt[i]//2)
                weak_exps[i] = int(weak_exps[i])
            else:
                weak_exps[i] = weaks[i][0]
        
        for x in range(len(strong_exps)):
            strong_exps[x] = bisect.bisect_left(exp_table, strong_exps[x])

        for problem in unsolved:
            tags = self.problem_tags[problem]
            for tag in tags['tags']:
                if idx2tag.get(tag) == None:
                    continue
                if idx2tag[tag] in strong_tags:
                    strong_list[strong_tags.index(idx2tag[tag])].append((exp_table.index(tags['exp'])+1, problem))
                elif idx2tag[tag] in weak_tags:
                    weak_list[weak_tags.index(idx2tag[tag])].append((tags['exp'], problem))
        
        for i in range(len(strong_list)):
            strong_list[i].sort()
        for i in range(len(weak_list)):
            weak_list[i].sort()
        for l in weak_list:
            l.sort()
        
        ret_all = {}

        best_recommend = []
        for i in range(len(strong_list)):
            l = bisect.bisect_left(strong_list[i], (max(strong_exps[i] - 5, 1),0))
            r = bisect.bisect_right(strong_list[i], (min(strong_exps[i] + 2, 30),0))
            strong_list[i] = strong_list[i][l:r+1]
            batch = len(strong_list[i]) // 5
            if batch < 5:
                batch = 1

            lst = []
            
            cnt = 5
            for j in range(0, len(strong_list[i]), batch):
                if cnt < 0:
                    break
                if cnt == 1:
                    best_recommend.append(strong_list[i][j][1])
                else:
                    lst.append(strong_list[i][j][1])
                cnt -= 1
            #ret_strong[strong_tags[i]] = lst
            ret_all[strong_tags[i]] = lst
            
            

        for i in range(len(weak_list)):
            l = bisect.bisect_left(weak_list[i], (exp_table[max(weak_exps[i] - 5, 1)],0))
            r = bisect.bisect_right(weak_list[i], (exp_table[min(weak_exps[i] + 1, 30)],0))
            weak_list[i] = weak_list[i][l:r+1]
            batch = len(weak_list[i]) // 5
            if batch < 5:
                batch = 1
            lst = []

            cnt = 5
            for j in range(0, len(weak_list[i]), batch):
                if cnt < 0:
                    break
                if cnt == 1:
                    best_recommend.append(weak_list[i][j][1])
                else: 
                    lst.append(weak_list[i][j][1])
                cnt -= 1
            #ret_weak[weak_tags[i]] = lst
            ret_all[weak_tags[i]] = lst
        ret_all['all'] = best_recommend
        return strong_tags, weak_tags, ret_all


db = DBHelper('.mylogin.cnf')

def main():
    model = Model()
    handle = 'raararaara'
    print(handle)
    print(model.recommend(handle), sep='\n')

if __name__ == "__main__":
    main()