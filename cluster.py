import node
import curses
import time

class NodeCluster:
    """ Class for the cluster of notes in the TIS-100, to allow the individual
    nodes to communicate with each other.
    """
    def __init__(self, width, height, inputs={}, outputs=[], speed=50, memory=[], debug=False):
        self.width = width
        self.height = height
        # Inputs and outputs will be dictionaries of (x, y): [values]
        self.inputs = inputs
        self.outputs = outputs
        self.output_lists = {}
        for x, y in self.outputs:
            self.output_lists[(x, y)] = []
        self.speed = speed
        self.memory = memory
        self.debug = debug
        self.cycle = 0
        self.nodes = []
        self.go = True
        for y in range(height+2):
            row = []
            for x in range(width+2):
                code = ""
                if (x, y) in self.inputs:
                    code = self.create_input(x, y)
                if (x, y) in self.memory:
                    row.append(node.Node(self, x, y, code=code, memory=True))
                else:
                    row.append(node.Node(self, x, y, code=code))
            self.nodes.append(row)

    def __repr__(self):
        rep = ""
        lines = len(self.nodes[1][1].__repr__().split('\n'))
        for y in range(1, self.height+1):
            for i in range(lines):
                for x in range(1, self.width+1):
                    rep += self.nodes[y][x].__repr__().split('\n')[i]
                rep += "\n"
        for x, y in self.outputs:
            output_list = [str(x) for x in self.output_lists[(x, y)]]
            rep += f"({x}, {y}): {', '.join(output_list)}\n"
        return rep

    def create_input(self, x, y):
        code = ""
        if y == 0:
            direction = 'DOWN'
        elif y == (self.height + 1):
            direction = 'UP'
        elif x == 0:
            direction = 'RIGHT'
        elif x == (self.width + 1):
            direction = 'LEFT'
        for value in self.inputs[(x, y)]:
            code += f"MOV {value} {direction}\n"
        code += "JRO 0"
        return code

    def run(self):
        try:
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(1)
            while(True):
                try:
                    stdscr.addstr(0, 0, f"Cycle: {self.cycle}")
                    stdscr.addstr(1, 0, self.__repr__())
                    stdscr.refresh()
                    # print(self.__repr__())
                    self.run_once()
                    if self.speed == 0:
                        char = stdscr.getch()
                    else:
                        time.sleep(1 / self.speed)
                except KeyboardInterrupt:
                    break
        finally:
            stdscr.keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()

    def run_once(self):
        if not self.go:
            return
        self.cycle += 1
        # Execute instructions
        for row in self.nodes:
            for node in row:
                node.exe()
        # Check any register values
        dirs = {
            'UP': (0, -1),
            'DOWN': (0, 1),
            'LEFT': (-1, 0),
            'RIGHT': (1, 0)
        }
        rdirs = {
            'UP': 'DOWN',
            'DOWN': 'UP',
            'LEFT': 'RIGHT',
            'RIGHT': 'LEFT'
        }
        # Move any values
        for row in self.nodes:
            for node in row:
                if node.read == 'ANY':
                    for direction in ['LEFT', 'RIGHT', 'UP', 'DOWN']:
                        x, y = dirs[direction]
                        x += node.x
                        y += node.y
                        if (rdirs[direction] == self.nodes[y][x].write and
                            self.nodes[y][x].output):
                            node.input = self.nodes[y][x].output
                            node.read = None
                            node.last = direction
                            self.nodes[y][x].output = None
                            self.nodes[y][x].step += 1
                            self.nodes[y][x].cycle += 1
                            break
                        if ('ANY' == self.nodes[y][x].write and
                            self.nodes[y][x].output):
                            node.input = self.nodes[y][x].output
                            node.read = None
                            node.last = direction
                            self.nodes[y][x].output = None
                            self.nodes[y][x].last = rdirs[direction]
                            self.nodes[y][x].step += 1
                            self.nodes[y][x].cycle += 1
                            if self.nodes[y][x].memory:
                                self.nodes[y][x].mode = 'WRTE'
                            break
                elif node.read in ('UP', 'DOWN', 'LEFT', 'RIGHT'):
                    x, y = dirs[node.read]
                    x += node.x
                    y += node.y
                    if (rdirs[node.read] == self.nodes[y][x].write and
                        self.nodes[y][x].output):
                        node.input = self.nodes[y][x].output
                        node.read = None
                        self.nodes[y][x].output = None
                        self.nodes[y][x].step += 1
                        self.nodes[y][x].cycle += 1
                    if ('ANY' == self.nodes[y][x].write and
                        self.nodes[y][x].output):
                        node.input = self.nodes[y][x].output
                        self.nodes[y][x].last = rdirs[node.read]
                        node.read = None
                        self.nodes[y][x].output = None
                        self.nodes[y][x].step += 1
                        self.nodes[y][x].cycle += 1
                        if self.nodes[y][x].memory:
                            self.nodes[y][x].mode = 'WRTE'
                elif (node.x, node.y) in self.outputs:
                    if node.y == 0:
                        direction = 'DOWN'
                    elif node.y == (self.height + 1):
                        direction = 'UP'
                    elif node.x == 0:
                        direction = 'RIGHT'
                    elif node.x == (self.width + 1):
                        direction = 'LEFT'
                    x, y = dirs[direction]
                    x += node.x
                    y += node.y
                    if (rdirs[direction] == self.nodes[y][x].write and
                        self.nodes[y][x].output):
                        self.output_lists[(node.x, node.y)].append(self.nodes[y][x].output)
                        self.nodes[y][x].output = None
                        self.nodes[y][x].step += 1
                        self.nodes[y][x].cycle += 1
                    if ('ANY' == self.nodes[y][x].write and
                        self.nodes[y][x].output and
                        not self.nodes[y][x].memory):
                        self.output_lists[(node.x, node.y)].append(self.nodes[y][x].output)
                        self.nodes[y][x].list = rdirs[direction]
                        self.nodes[y][x].output = None
                        self.nodes[y][x].step += 1
                        self.nodes[y][x].cycle = 1


