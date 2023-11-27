import sys
sys.path.append('..')

import cluster

image = [[3] * 30 for _ in range(18)]

c = cluster.NodeCluster(4, 3,
                        outputs=[(3,4)],
                        image_port=(3,4),
                        test_image=image,
                        dead=[(1,2)],
                        filename="14.txt")
c.run()
