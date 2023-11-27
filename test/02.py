import sys
sys.path.append('..')

import cluster
import random

in_a = [random.randint(10, 99) for _ in range(39)]
out_a = [2 * x for x in in_a]

c = cluster.NodeCluster(4, 3,
                        inputs={(2,0): in_a},
                        outputs=[(3,4)],
                        test_outputs={(3,4): out_a},
                        dead=[(4,1), (1,3)],
                        filename="02.txt")
c.run()
