import sys
sys.path.append('..')

import cluster
import random

in_a = [random.randint(-2, 2) for _ in range(39)]
out_g = [1 if x > 0 else 0 for x in in_a]
out_e = [1 if x == 0 else 0 for x in in_a]
out_l = [1 if x < 0 else 0 for x in in_a]

c = cluster.NodeCluster(4, 3,
                        inputs={(1,0): in_a},
                        outputs=[(2,4), (3,4), (4,4)],
                        test_outputs={(2,4): out_g, (3,4): out_e, (4,4): out_l},
                        dead=[(2,2), (3,2), (4,2)],
                        filename="04.txt")
c.run()
