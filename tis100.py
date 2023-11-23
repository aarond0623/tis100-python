import cluster
import node

c = cluster.NodeCluster(3, 1, speed=50, memory=[(2,1)])
print(c)
c.nodes[1][1].parse_code("""
mov 1 right
mov 2 right
mov 3 right
mov 4 right
mov 5 right
jro 0
""")
c.nodes[1][3].parse_code("""
mov -5 acc
repeat:
add 1
jlz repeat
mov left acc
jro -1
""")
print(c.nodes[1][3].instructions)
c.run()
