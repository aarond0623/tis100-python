import re

class NodeCluster:
    """ Class for the cluster of notes in the TIS-100, to allow the individual
    nodes to communicate with each other.
    """
    def __init__(self, width, height, inputs=None, outputs=None):
        self.width = width
        self.height = height
        self.inputs = inputs
        self.outputs = outputs
        self.cycle = 0
        self.nodes = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(self.Node(self, x, y))
            self.nodes.append(row)

    def __repr__(self):
        rep = ""
        for row in self.nodes:
            for _ in range(self.width):
                rep += "┌────────┐"
            rep += "\n"
            for node in row:
                rep += f"│ACC: {node.acc:3}│"
            rep += "\n"
            for node in row:
                rep += f"│BAK: {node.bak:3}│"
            rep += "\n"
            for node in row:
                dirs = {
                    'UP': 'UP',
                    'DOWN': 'DWN',
                    'LEFT': 'LFT',
                    'RIGHT': 'RGT',
                    None: 'N/A'
                }
                rep += f"│LST: {dirs[node.last]}│"
            rep += "\n"
            for node in row:
                rep += f"│MOD:    │"
            rep += "\n"
            for _ in range(self.width):
                rep += "└────────┘"
            rep += "\n"
        if rep[-1] == "\n":
            return rep[:-1]
        return rep

    def run(self):
        for row in nodes:
            for node in row:
                node.exec()

    class Node:
        def __init__(self, cluster, x, y, code=""):
            self.x = x
            self.y = y
            self.cluster = cluster
            self.acc = 0
            self.bak = 0
            self.last = None
            self.instructions = self.parse_code(code)
            self.step = 0
            self.cycle = 0
            self.midmove = False
            self.dirs = {
                'UP': (0, -1),
                'DOWN': (0, 1),
                'LEFT': (-1, 0),
                'RIGHT': (1, 0)
            }
            self.rdirs = {
                'UP': "DOWN",
                'DOWN': "UP",
                'LEFT': "RIGHT",
                'RIGHT': "LEFT"
            }
            self.out = {
                'UP': None,
                'DOWN': None,
                'LEFT': None,
                'RIGHT': None
            }

        def get_any(self):
            values = []
            for direction in ['LEFT', 'RIGHT', 'UP', 'DOWN']:
                x, y = self.dirs[direction]
                x += self.x
                y += self.y
                receive = self.rdirs[direction]
                values.append(self.cluster.nodes[y][x].out[receive])
            values = [x for x in values if x is not None]
            try:
                return values[0]
            except IndexError:
                return None

        def get_value(self, value):
            try:
                return int(value)
            except ValueError:
                if value == 'ACC':
                    return self.acc
                if value == 'NIL':
                    return 0
                if value == 'ANY':
                    result = self.get_any()
                    while result is None:
                        self.nop()
                        result = self.get_any()
                    return result
                if value == 'LAST':
                    if self.last is None:
                        return 0
                    else:
                        x, y = self.dirs[self.last]
                        x += self.x
                        y += self.y
                        receive = self.rdirs[value]
                        return self.cluster.nodes[y][x].out[receive]
                if value in self.dirs.keys():
                    x, y = self.dirs[value]
                    x += self.x
                    y += self.y
                    receive = self.rdirs[value]
                    return self.cluster.nodes[y][x].out[receive]
                raise Exception(f"Invalid argument \"{value}\".")

        def nop(self):
            return True

        def mov(self, src, dest):
            src = self.get_value(value)
            if src is None:
                return False
            if dest == 'ACC':
                self.acc = src
                return True
            if dest == 'NIL':
                return True
            return False

        def swp(self):
            self.acc, self.bak = self.bak, self.acc
            return True

        def sav(self):
            self.bak = self.acc
            return True

        def add(self, value):
            result = self.get_value(value)
            if result is not None:
                self.acc += result
                return True
            return False

        def sub(self, value):
            result = self.get_value(value)
            if result is not None:
                self.acc -= result
                return True
            return False

        def neg(self):
            self.acc = -self.acc
            return True

        def jmp(self, label, labels):
            self.step = labels.get(label, self.step+1)
            return True

        def jez(self, label, labels):
            if self.acc == 0:
                self.step = labels.get(label, self.step+1)
            else:
                self.step += 1
            return True

        def jnz(self, label, labels):
            if self.acc != 0:
                self.step = labels.get(label, self.step+1)
            else:
                self.step += 1
            return True

        def jgz(self, label, labels):
            if self.acc > 0:
                self.step = labels.get(label, self.step+1)
            else:
                self.step += 1
            return True

        def jlz(self, label, labels):
            if self.acc < 0:
                self.step = labels.get(label, self.step+1)
            else:
                self.step += 1
            return True

        def jro(self, value):
            result = self.get_value(value)
            if result is not None:
                self.step += result
                return True
            return False

        def exe(self):
            instruction = self.instructions[self.step]
            if len(instruction) > 1:
                result = instruction[0](*instruction[1:])
            else:
                result = instruction()
            if result:
                self.step += 1
            self.cycle += 1

        def strip_comments(self, code):
            code = [line.split('#')[0] for line in code]
            return [line for line in code if line != '']

        def find_labels(self, code):
            labels = {}
            new_code = []
            for line in code:
                label = re.match(r'([^\s:]+):(.*)', line)
                if label:
                    labels[label[1]] = len(new_code)
                    if len(label[2].strip()) > 0:
                        new_code.append(label[2].strip())
                else:
                    new_code.append(line)
            return (labels, new_code)

        def parse_code(self, code):
            code = code.upper().split('\n')
            code = self.strip_comments(code)
            labels, code = self.find_labels(code)
            instructions = []
            for line in code:
                line = re.split('[,\s]+', line)
                if line[0] == 'NOP':
                    instructions.append(self.nop)
                elif line[0] == 'SWP':
                    instructions.append(self.swp)
                elif line[0] == 'SAV':
                    instructions.append(self.sav)
                elif line[0] == 'NEG':
                    instructions.append(self.neg)
                elif line[0] == 'ADD':
                    instructions.append((self.add, line[1]))
                elif line[0] == 'SUB':
                    instructions.append((self.sub, line[1]))
                elif line[0] == 'JMP':
                    instructions.append((self.jmp, line[1], labels))
                elif line[0] == 'JEZ':
                    instructions.append((self.jez, line[1], labels))
                elif line[0] == 'JNZ':
                    instructions.append((self.jnz, line[1], labels))
                elif line[0] == 'JGZ':
                    instructions.append((self.jgz, line[1], labels))
                elif line[0] == 'JLZ':
                    instructions.append((self.jlz, line[1], labels))
                elif line[0] == 'JRO':
                    instructions.append((self.jro, line[1]))
                else:
                    instructions.append(self.nop)
            return instructions
