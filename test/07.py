import sys
sys.path.append('..')

import cluster
import random

in_a = []
out_s = []
out_l = []
while True:
    seq = [random.randint(10, 99) for _ in range(random.randint(0, 5))]
    if (len(in_a) + len(seq)) > 38:
        break
    in_a += seq
    in_a += [0]
    out_s += [sum(seq)]
    out_l += [len(seq)]
seq = [random.randint(10, 99) for _ in range(38 - len(in_a))]
in_a += seq
in_a += [0]
out_s += [sum(seq)]
out_l += [len(seq)]

c = cluster.NodeCluster(4, 3,
                        inputs={(2,0): in_a},
                        outputs=[(2,4), (3,4)],
                        test_outputs={(2,4): out_s, (3,4): out_l},
                        dead=[(4,1)],
                        filename="07.txt")
c.run()
