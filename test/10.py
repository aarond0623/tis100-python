import sys
sys.path.append('..')

import cluster
import random

in_a = random.choices(range(6), weights=[75, 5, 5, 5, 5, 5], k=39)
out = [0, 0]

for i in range(3, len(in_a)+1):
    if in_a[i-3:i] == [0, 0, 0]:
        out.append(1)
    else:
        out.append(0)

c = cluster.NodeCluster(4, 3,
                        inputs={(2,0): in_a},
                        outputs=[(3,4)],
                        test_outputs={(3,4): out},
                        dead=[(4,1)],
                        filename="10.txt")
c.run()
