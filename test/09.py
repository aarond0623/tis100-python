import sys
sys.path.append('..')

import cluster
import random

ins = [[0], [0], [0], [0]]
out = [0]
for _ in range(38):
    interrupt = random.randint(0, 4)
    if interrupt == 4:
        out.append(0)
    for i in range(0, 4):
        if i == interrupt:
            ins[i].append((ins[i][-1] + 1) % 2)
            if ins[i][-1] == 1:
                out.append(i+1)
            else:
                out.append(0)
        else:
            ins[i].append(ins[i][-1])

c = cluster.NodeCluster(4, 3,
                        inputs={(1,0): ins[0], (2,0): ins[1],
                                (3,0): ins[2], (4,0): ins[3]},
                        outputs=[(3,4)],
                        test_outputs={(3,4): out},
                        dead=[(1,3)],
                        filename="09.txt")
c.run()
