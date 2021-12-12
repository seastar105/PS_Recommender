from n2 import HnswIndex

f = 179
t = HnswIndex(f)

fin = open('userVec', 'r')
for _ in range(39839):
    vec = list(map(int, fin.readline().split()))
    t.add_data(vec)

t.build(m = 20, max_m0 = 40, n_threads = 4)
t.save('userModel.n2')