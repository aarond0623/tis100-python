import node
import curses
from datetime import datetime
import textwrap
import time

class NodeCluster:
    """ Class for the cluster of notes in the TIS-100, to allow the individual
    nodes to communicate with each other.
    """
    def __init__(self, width, height, inputs={}, outputs=[], image_port=None, image_dim=(30, 18), test_image=[], filename=None, test_outputs={}, speed=50, memory=[], dead=[], debug=False):
        self.screen = None
        self.width = width
        self.height = height
        # Inputs and outputs will be dictionaries of (x, y): [values]
        self.inputs = inputs
        self.outputs = outputs
        self.output_lists = {}
        for x, y in self.outputs:
            self.output_lists[(x, y)] = []
        self.test_outputs = test_outputs
        self.speed = speed
        self.memory = memory
        self.dead = dead
        self.debug = debug
        self.cycle = 0
        self.nodes = []
        self.go = True
        self.image_port = image_port
        self.image_dim = image_dim
        self.test_image = test_image
        self.image_pos = [None, None]
        self.image = None
        if self.image_port:
            self.image = [[0] * image_dim[0] for _ in range(image_dim[1])]
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
                elif (x, y) in self.dead:
                    row.append(node.Node(self, x, y, code=code, dead=True))
                else:
                    row.append(node.Node(self, x, y, code=code))
                if (x, y) in self.outputs:
                    row[x].acc = None
            self.nodes.append(row)
        if filename:
            self.load(filename)

    def __repr__(self):
        rep = ""
        offset = 1
        if self.debug:
            offset = 0
            for x, y in self.inputs.keys():
                input_list = [str(x) for x in self.inputs[(x, y)]]
                rep += f"({x}, {y}): {' '.join(input_list)}\n"
        lines = len(self.nodes[1][1].__repr__().split('\n'))
        for y in range(offset, self.height+2-offset):
            for i in range(lines):
                for x in range(offset, self.width+2-offset):
                    rep += self.nodes[y][x].__repr__().split('\n')[i]
                rep += "\n"
        for x, y in self.outputs:
            if self.debug:
                test_list = [str(x) for x in self.test_outputs[(x, y)]]
                rep += f"({x}, {y}): {' '.join(test_list)}\n"
            output_list = [str(x) for x in self.output_lists[(x, y)]]
            if self.debug:
                rep += textwrap.fill(f"({x}, {y}): {' '.join(output_list)}", self.screen.getmaxyx()[1]) + "\n"
            else:
                rep += textwrap.fill(f"{' '.join(output_list)}", self.screen.getmaxyx()[1]) + "\n"

        return rep

    def load(self, filename):
        code = {}
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line[0] == '@':
                    current_node = int(line[1:])
                    code[current_node] = ""
                elif line != "":
                    code[current_node] += line
        i = 0
        for y in range(1, self.height+1):
            for x in range(1, self.width+1):
                if (x, y) in self.dead or (x, y) in self.memory:
                    continue
                self.nodes[y][x] = node.Node(self, x, y, code=code.get(i, ""))
                i += 1

    def save(self, filename):
        with open(filename, 'w') as file:
            i = 0
            for y in range(1, self.height+1):
                for x in range(1, self.width+1):
                    if (x, y) in self.dead or (x, y) in self.memory:
                        continue
                    file.write(f"@{i}\n")
                    if self.nodes[y][x].code == "":
                        file.write("\n\n")
                    else:
                        file.write(self.nodes[y][x].code)
                        if self.nodes[y][x].code[-1] == "\n":
                            file.write("\n")
                        else:
                            file.write("\n\n")
                    i += 1

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

    def write_color(self, y, x, color):
        width = len(self.nodes[1][1].__repr__().split('\n')[0])
        width *= self.width
        curses.init_pair(1, 0, 0)
        curses.init_pair(2, 7, 0)
        curses.init_pair(3, -1, -1)
        curses.init_pair(4, 0, 1)
        try:
            if color == 0:
                self.screen.addstr(y, width+x, " ")
                return
            if color == 1:
                self.screen.addstr(y, width+x, " ", curses.color_pair(1))
                return
            if color == 2:
                self.screen.addstr(y, width+x, " ", curses.color_pair(2) | curses.A_REVERSE)
                return
            if color == 3:
                self.screen.addstr(y, width+x, " ", curses.color_pair(3) | curses.A_REVERSE)
                return
            if color == 4:
                self.screen.addstr(y, width+x, " ", curses.color_pair(4))
                return
        except:
            return

    def draw_image(self, value):
        if value < 0:
            self.image_pos = [None, None]
            return
        if self.image_pos[0] is None:
            self.image_pos[0] = value
            return
        if self.image_pos[1] is None:
            self.image_pos[1] = value
            return
        if self.image_pos[0] >= self.image_dim[0]:
            return
        if self.image_pos[1] >= self.image_dim[1]:
            return
        self.image[self.image_pos[1]][self.image_pos[0]] = value
        self.image_pos[0] = self.image_pos[0] + 1

    def run(self):
        try:
            self.screen = curses.initscr()
            curses.start_color()
            curses.use_default_colors()
            self.screen.clear()
            curses.noecho()
            curses.cbreak()
            self.screen.keypad(1)
            curses.curs_set(0);
            last = datetime.now()
            while(True):
                try:
                    self.screen.clear()
                    # Monitor the node cycles, so we can stop if nothing changes.
                    old_cycles = []
                    for row in self.nodes[1:-1]:
                        for n in row:
                            old_cycles.append(n.cycle)
                    self.screen.addstr(0, 0, f"Cycle: {self.cycle}")
                    tis = self.__repr__().split('\n')
                    for i, line in enumerate(tis):
                        try:
                            self.screen.addstr(i+1, 0, line)
                        except:
                            pass
                    for i, row in enumerate(self.image):
                        for j, value in enumerate(row):
                            self.write_color(i, j, value)
                    self.screen.refresh()
                    self.run_once()
                    cycles = []
                    for row in self.nodes[1:-1]:
                        for n in row:
                            cycles.append(n.cycle)
                    if old_cycles == cycles and self.cycle > 1:
                        if self.go:
                            self.cycle -= 1
                        self.go = False
                    if self.speed == 0:
                        self.screen.getch()
                    else:
                        delta, last = (datetime.now() - last), datetime.now()
                        delta = delta.seconds + delta.microseconds/1000000
                        time.sleep(max((1 / self.speed) - delta, 1 / self.speed))
                except KeyboardInterrupt:
                    break
        finally:
            self.screen.keypad(0)
            curses.flushinp()
            curses.echo()
            curses.nocbreak()
            curses.endwin()
            curses.curs_set(1);
            self.cycle = 0
            self.go = True
            for (x, y) in self.outputs:
                self.output_lists[(x, y)] = []
            for row in self.nodes:
                for n in row:
                    n.__init__(self, n.x, n.y, code=n.code, memory=n.memory, dead=n.dead)
                    if (n.x, n.y) in self.outputs:
                        n.acc = None
            self.image_pos = [None, None]
            if self.image_port:
                self.image = [[0] * self.image_dim[0] for _ in range(self.image_dim[1])]

    def run_once(self):
        # Check if test_outputs is equal to output_lists and stop
        if self.test_outputs == self.output_lists:
            self.go = False
        if self.image == self.test_image:
            self.go = False
        if not self.go and self.speed > 0:
            char = self.screen.getch()
            if char == ord('r'):
                self.go = True
            else:
                self.cycle -= 1
        self.cycle += 1
        # Execute instructions
        for row in self.nodes:
            for n in row:
                if self.speed > 0 and len(n.instructions) > 0 and (n.step % len(n.instructions)) in n.breakpoints:
                    self.go = False
                    char = self.screen.getch()
                    if char == ord('r'):
                        self.go = True
                n.exe()
                # If this is an output node, check the ACC, add it to the
                # output list, then clear it.
                if (n.x, n.y) in self.outputs and (n.acc is not None):
                    self.output_lists[(n.x, n.y)].append(n.acc)
                    if (n.x, n.y) == self.image_port:
                        self.draw_image(n.acc)
                    n.acc = None
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
            for n in row:
                # Node just wrote somewhere, step and cycle increase by 1.
                if n.ready_to_write and not(n.write and (n.output is not None)):
                    n.step += 1
                    n.cycle += 1
                n.ready_to_write = n.write and (n.output is not None)
