import click

class Node:
    def __init__(self, x, y, code):
        self.x = x
        self.y = y
        self.code = code.split("\n")
        self.acc = 0
        self.bak = 0
        self.dir = ['RIGHT', 'UP', 'LEFT', 'DOWN']
        self.last = 'N/A'
        self.step = 1
        self.cycle = 0
        self.length = len(self.code)
        self.curline = self.cycle % self.length
        self.label = {}
    
    def self.add(value):
        try:
            self.acc = int(value)
        except ValueError:
            if self.value == 'ACC':
                self.acc += self.acc
                return
            if self.value == 'NIL':
                self.acc += 0
              
    
    def parse_code(self, line)
        line = [x.upper for x in line.split(', ')]
        if line[0][0] == '#':
            return
        if line[0] == 'NOP':
            return
        if line[0] == 'MOV':
            self.mov(line[1], line[2])
            return
        if line[0] == 'SWP':
            self.acc, self.bak = self.bak, self.acc
            return
        if line[0] == 'SAV':
            self.bak = self.acc
            return
        if line[0] == 'ADD':
            self.add(line[1])
            return
        if line[0] == 'SUB':
            self.sub(line[1])
            return
        if line[0] == 'NEG':
            self.acc *= -1
            return
        if line[0] == 'JMP':
            self.curline = self.label[line[1]]
            return
        if line[0] == 'JEZ':
            if self.acc == 0:
                self.curline = self.label[line[1]]
            return
        if line[0] == 'JNZ':
            if self.acc != 0:
                self.curline = self.label[line[1]]
            return
        if line[0] == 'JGZ':
            if self.acc > 0:
                self.curline = self.label[line[1]]
            return
        if line[0] == 'JLZ':
            if self.acc < 0:
                self.curline = self.label[line[1]]
            return
        if line[0] == 'JRO':
            self.jro(line[1])
            return
        if line[0][-1] == ':':
            self.label[line[:-1]] = self.curline
            return
        else:
            pass
            
    