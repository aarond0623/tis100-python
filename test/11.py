import sys
sys.path.append('..')

import cluster
import random

in_a = []
out_i = []
out_a = []
while True:
    seq = [random.randint(10, 99) for _ in range(random.randint(1, 5))]
    if (len(in_a) + len(seq)) > 36:
        break
    in_a += seq
    in_a += [0]
    out_i += [min(seq)]
    out_a += [max(seq)]
seq = [random.randint(10, 99) for _ in range(38 - len(in_a))]
in_a += seq
in_a += [0]
out_i += [min(seq)]
out_a += [max(seq)]

c = cluster.NodeCluster(4, 3,
                        inputs={(2,0): in_a},
                        outputs=[(2,4), (3,4)],
                        test_outputs={(2,4): out_i, (3,4): out_a},
                        dead=[(4,2)],
                        filename="11.txt")
c.run()
