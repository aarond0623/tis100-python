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
                if (x, y) in self.outputs:
                    code = self.create_output(x, y)
                if (x, y) in self.memory:
                    row.append(node.Node(self, x, y, code=code, memory=True))
                else:
                    row.append(node.Node(self, x, y, code=code))
                if (x, y) in self.outputs:
                    row[x].acc = None
            self.nodes.append(row)

    def __repr__(self):
        rep = ""
        offset = 1
        if self.debug:
            offset = 0
        lines = len(self.nodes[1][1].__repr__().split('\n'))
        for y in range(offset, self.height+2-offset):
            for i in range(lines):
                for x in range(offset, self.width+2-offset):
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

    def create_output(self, x, y):
        if y == 0:
            direction = 'DOWN'
        elif y == (self.height + 1):
            direction = 'UP'
        elif x == 0:
            direction = 'RIGHT'
        elif x == (self.width + 1):
            direction = 'LEFT'
        code = f"MOV {direction} ACC"
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
                # If this is an output node, check the ACC, add it to the
                # output list, then clear it.
                if (node.x, node.y) in self.outputs and node.acc:
                    self.output_lists[(node.x, node.y)].append(node.acc)
                    node.acc = None
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
        # Set nodes' ready_to_write value if they have a write port and output
        # set.
        for row in self.nodes:
            for node in row:
                # Node just wrote somewhere, step and cycle increase by 1.
                if node.ready_to_write and not(node.write and node.output):
                    node.step += 1
                    node.cycle += 1
                node.ready_to_write = node.write and node.output


