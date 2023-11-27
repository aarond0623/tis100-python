import sys
sys.path.append('..')

import cluster
import random

in_a = [random.randint(10, 99) for _ in range(13)]
in_b = [random.randint(10, 99) for _ in range(13)]
out = []
for a, b in zip(in_a, in_b):
    out += [min(a, b), max(a, b), 0]

print(in_a)
print(in_b)
print(out)

c = cluster.NodeCluster(4, 3,
                        inputs={(2,0): in_a, (3,0): in_b},
                        outputs=[(3,4)],
                        test_outputs={(3,4): out},
                        dead=[(2,3)],
                        filename="06.txt")
c.run()
