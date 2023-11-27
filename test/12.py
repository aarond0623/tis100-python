import sys
sys.path.append('..')

import cluster
import random

in_a = []
out = []
while True:
    seq = [random.randint(10, 99) for _ in range(random.randint(0, 5))]
    if (len(in_a) + len(seq)) > 38:
        break
    in_a += seq
    in_a += [0]
    out += seq[::-1]
    out += [0]
seq = [random.randint(10, 99) for _ in range(38 - len(in_a))]
in_a += seq
in_a += [0]
out += seq[::-1]
out += [0]

c = cluster.NodeCluster(4, 3,
                        inputs={(2,0): in_a},
                        outputs=[(3,4)],
                        test_outputs={(3,4): out},
                        dead=[(1,3)],
                        memory=[(3,1),(2,3)],
                        filename="12.txt")
c.run()
