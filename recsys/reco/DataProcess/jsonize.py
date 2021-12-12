import json

json
fpath = '../userVec.json'

data = {}
fin = open('../userVec', 'r')

for i in range(39839):
    vec = list(map(int, fin.readline().split()))
    data[i+1] = vec

with open(fpath, 'w') as fout:
    json.dump(data, fout, indent = 4)