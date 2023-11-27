import sys
sys.path.append('..')

import cluster
import random

in_x = [random.randint(10, 99) for _ in range(39)]
in_a = [random.randint(10, 99) for _ in range(39)]
out_x = in_x
out_a = in_a

c = cluster.NodeCluster(4, 3,
                        inputs={(1,0): in_x, (4,0): in_a},
                        outputs=[(1,4), (4,4)],
                        test_outputs={(1,4): out_x, (4,4): out_a},
                        dead=[(2,1), (2,2), (2,3), (4,2)],
                        filename="01.txt")
c.run()
