import sys
sys.path.append('..')

import cluster
import random

in_a = [0,32,30,27,24,28,37,33,24,13,9,13,9,
        13,12,14,23,21,23,19,9,18,8,-3,6,3,
        14,25,15,14,3,1,2,-1,1,-10,-7,-7,-11]
out = [0,1,0,0,0,0,0,0,0,1,0,0,0,
       0,0,0,0,0,0,0,1,0,1,1,0,0,
       1,1,1,0,1,0,0,0,0,1,0,0,0]
c = cluster.NodeCluster(4, 3,
                        inputs={(2,0): in_a},
                        outputs=[(3,4)],
                        test_outputs={(3,4): out},
                        dead=[(1,3)],
                        filename="08.txt")
c.run()
