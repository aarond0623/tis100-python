import sys
sys.path.append('..')

import cluster

row1 = [3, 0] * 15
row2 = [0, 3] * 15
image = []
for _ in range(9):
    image.append(row1)
    image.append(row2)

c = cluster.NodeCluster(4, 3,
                        outputs=[(3,4)],
                        image_port=(3,4),
                        test_image=image,
                        dead=[(1,1)],
                        filename="15.txt")
c.run()
