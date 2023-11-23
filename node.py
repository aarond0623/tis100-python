import re

MAX_N = 999
MIN_N = -999

class Node:
    def __init__(self, cluster, x, y, code="", memory=False):
        self.x = x
        self.y = y
        self.cluster = cluster
        self.acc = 0
        self.bak = 0
        self.last = None
        self.instructions = []
        self.parse_code(code)
        self.step = 0
        self.cycle = 0
        self.mode = 'IDLE'
        # Output register. Outgoing values are stored here.
        self.output = None

        # Input register. Incoming values are stored here.
        self.input = None

        # The register this node is writing to.
        self.write = None

        # The register this node is reading from.
        self.read = None

        # For stack memory nodes.
        self.memory = memory
        self.stack = []

    def get_stack(self, i):
        if i >= len(self.stack):
            return "N/A"
        else:
            return self.stack[-i - 1]

    def get_value(self, src):
        try:
            value = max(min(int(src), MAX_N), MIN_N)
            self.mode = 'RUN'
            return value
        except ValueError:
            if src == 'ACC':
                self.mode = 'RUN'
                return self.acc
            if src == 'NIL':
                self.mode = 'RUN'
                return 0
            # On TIS-100, reading a value from LAST when it is not set returns
            # 0.
            if src == 'LAST':
                if self.last is None:
                    self.mode = 'RUN'
                    return 0
                else:
                    src = self.last
            # Otherwise, we are expecting or will expect a value.
            if src in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'ANY']:
                self.mode = 'READ'
                # When input is set, we just had a move. Return that and clear.
                value = None
                if self.input:
                    value = self.input
                    self.input = None
                self.read = src
                return value
            raise Exception(f"Invalid argument \"{value}\"")

    # TIS-100 OPCODES
    # Operations will return True if they are able to execute and False if they
    # will cause a hang (e.g. trying to retrieve a value from a node that is
    # not attempting to send a value).
    def nop(self):
        # NOP - Do nothing.
        self.mode = 'RUN'
        self.step += 1
        self.cycle += 1

    def mov(self, src, dest):
        # MOV - Move a value
        src = self.get_value(src)
        if src is None:
            # Was not able to retrieve a value -- FAIL.
            return
        # Already writing: FAIL
        if self.write and self.output:
            return
        # Just finished a move
        if self.write and not self.output:
            self.write = None
            self.mode = 'RUN'
            return
        if dest == 'ACC':
            self.mode = 'RUN'
            self.acc = src
            self.step += 1
            self.cycle += 1
            return
        if dest == 'NIL':
            # Send the value nowhere. Always succeed.
            self.mode = 'RUN'
            self.step += 1
            self.cycle += 1
        # Attempting to send to LAST when it is not set will cause a hang.
        if dest == 'LAST':
            if self.last is None:
                self.mode = 'WRTE'
                return
            else:
                dest = self.last
        # For all other moves, set our write and output.
        if dest in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'ANY']:
            self.mode = 'WRTE'
            self.write = dest
            self.output = src
            return


    def swp(self):
        # SWP - Swap BAK and ACC
        self.acc, self.bak = self.bak, self.acc
        self.mode = 'RUN'
        self.step += 1
        self.cycle += 1

    def sav(self):
        # SAV - Copy ACC to BAK
        self.bak = self.acc
        self.mode = 'RUN'
        self.step += 1
        self.cycle += 1

    def add(self, value):
        # ADD - Add to ACC
        result = self.get_value(value)
        if result is not None:
            self.acc = max(min(self.acc + result, MAX_N), MIN_N)
            self.step += 1
            self.cycle += 1

    def sub(self, value):
        # SUB - Subtract from ACC
        result = self.get_value(value)
        if result is not None:
            self.acc = max(min(self.acc - result, MAX_N), MIN_N)
            self.step += 1
            self.cycle += 1

    def neg(self):
        # NEG - Reverse sign of ACC
        self.mode = 'RUN'
        self.acc = -self.acc
        self.step += 1
        self.cycle += 1

    def jmp(self, label, labels):
        # Set step to the label value.
        self.mode = 'RUN'
        if label not in labels:
            raise Exception(f"Undefined label \"{label}\"")
        self.step = labels[label]
        self.cycle += 1

    def jez(self, label, labels):
        # Conditional JMP if ACC = 0
        self.mode = 'RUN'
        self.cycle += 1
        if self.acc == 0:
            if label not in labels:
                raise Exception(f"Undefined label \"{label}\"")
            self.step = labels[label]
        else:
            self.step += 1

    def jnz(self, label, labels):
        # Conditional JMP if ACC != 0
        self.mode = 'RUN'
        self.cycle += 1
        if self.acc != 0:
            if label not in labels:
                raise Exception(f"Undefined label \"{label}\"")
            self.step = labels[label]
        else:
            self.step += 1

    def jgz(self, label, labels):
        # Conditional JMP if ACC > 0
        self.mode = 'RUN'
        self.cycle += 1
        if self.acc > 0:
            if label not in labels:
                raise Exception(f"Undefined label \"{label}\"")
            self.step = labels[label]
        else:
            self.step += 1

    def jlz(self, label, labels):
        # Conditional JMP if ACC < 0
        self.mode = 'RUN'
        self.cycle += 1
        if self.acc < 0:
            if label not in labels:
                raise Exception(f"Undefined label \"{label}\"")
            self.step = labels[label]
        else:
            self.step += 1

    def jro(self, value):
        # JMP based on a relative offset.
        self.mode = 'RUN'
        result = self.get_value(value)
        step_mod = self.step % len(self.instructions)
        if result is not None:
            self.step = max(min(step_mod + result, len(self.instructions)-1), 0)
            self.cycle += 1

    def hcf(self):
        self.cluster.go = False

    def exe(self):
        if self.memory:
            if self.input:
                self.stack.append(self.input)
                self.input = None
                self.read = None
            else:
                self.input = None
                self.read = 'ANY'
            if self.stack:
                self.write = 'ANY'
                if self.mode == 'WRTE':
                    self.stack.pop()
                    self.mode = 'IDLE'
                else:
                    self.output = self.stack[-1]
            else:
                self.write = None
        if len(self.instructions) == 0:
            return
        instruction = self.instructions[self.step % len(self.instructions)]
        if type(instruction) is tuple:
            instruction[0](*instruction[1:])
        else:
            instruction()

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
        code = [line.strip() for line in code]
        labels, code = self.find_labels(code)
        instructions = []
        for line in code:
            line = re.split('[,\s]+', line)
            if line[0] == 'NOP':
                instructions.append(self.nop)
            elif line[0] == 'MOV':
                instructions.append((self.mov, line[1], line[2]))
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
            elif line[0] == 'HCF':
                instructions.append(self.hcf)
            else:
                instructions.append(self.nop)
        self.instructions = instructions
