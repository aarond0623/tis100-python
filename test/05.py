import sys
sys.path.append('..')

import cluster
import random

in_a = [random.randint(-29, 0) for _ in range(39)]
in_s = [random.randint(-1, 1) for _ in range(39)]
in_b = [random.randint(0, 29) for _ in range(39)]
out = [a if s == -1 else b if s == 1 else a + b for a, b, s in zip(in_a, in_b,
                                                                   in_s)]

c = cluster.NodeCluster(4, 3,
                        inputs={(2,0): in_a, (3,0): in_s, (4,0): in_b},
                        outputs=[(3,4)],
                        test_outputs={(3,4): out},
                        dead=[(1,3)],
                        filename="05.txt")
c.run()
