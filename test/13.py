import sys
sys.path.append('..')

import cluster
import random

in_a = [random.randint(0, 8) for _ in range(39)]
in_b = [random.randint(0, 8) for _ in range(39)]
out = [a * b for a, b in zip(in_a, in_b)]

c = cluster.NodeCluster(4, 3,
                        inputs={(2,0): in_a, (3,0):in_b},
                        outputs=[(3,4)],
                        test_outputs={(3,4): out},
                        dead=[(1,3)],
                        memory=[(1,2),(4,2)],
                        filename="13.txt")
c.run()
