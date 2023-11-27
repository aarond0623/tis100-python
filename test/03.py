import sys
sys.path.append('..')

import cluster
import random

in_a = [random.randint(10, 99) for _ in range(39)]
in_b = [random.randint(10, 99) for _ in range(39)]
out_p = [a - b for a, b in zip(in_a, in_b)]
out_n = [b - a for a, b in zip(in_a, in_b)]

print(in_a)
print(in_b)
print(out_p)
print(out_n)

c = cluster.NodeCluster(4, 3,
                        inputs={(2,0): in_a, (3,0): in_b},
                        outputs=[(2,4), (3,4)],
                        test_outputs={(2,4): out_p, (3,4): out_n},
                        dead=[(4,2)],
                        filename="03.txt")
c.run()
