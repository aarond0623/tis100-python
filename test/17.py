import sys
sys.path.append('..')

import cluster

in_a = [8, 10, 10, 10, 13, 15, 13, 12, 4, 6, 13, 11, 13, 15, 14, 12, 11, 10, 9,
        10, 11, 12, 11, 10, 9, 9, 9, 9, 4, 5]

image = [[0] * 30 for _ in range(18)]

for x, n in enumerate(in_a):
    for y in range(n):
        image[17-y][x] = 3

c = cluster.NodeCluster(4, 3,
                        inputs={(2,0): in_a},
                        outputs=[(3,4)],
                        image_port=(3,4),
                        test_image=image,
                        dead=[(1,3)],
                        filename="17.txt",
                        speed=500)
c.run()
