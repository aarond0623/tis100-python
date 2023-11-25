import cluster
import node
import os
import re

def check_numeric(command, arguments, min_arguments, min_value=0, max_value=None):
    try:
        int_arguments = [int(x) for x in arguments]
        assert len(arguments) >= min_arguments
        for x in int_arguments:
            assert x >= min_value
            if max_value is not None:
                assert x <= max_value
    except (ValueError, AssertionError):
        variables = 'XYZ'
        variables = [variables[i%3] for i in range(min_arguments)]
        print(f"INVALID SYNTAX: {command} {' '.join(variables)}")
    else:
        if len(int_arguments) == 0:
            return None
        if len(int_arguments) == 1:
            return int_arguments[0]
        return tuple(int_arguments)

def prompt():
    _ = os.system('cls' if os.name == 'nt' else 'clear')
    print("TESSELLATED INTELLIGENCE SYSTEMS TIS-100 BIOS V1.2")
    print("COPYRIGHT (C) 1972-1975, TESSELLATED INTELLIGENCE SYSTEMS INC.")
    print()
    while True:
        cmd = input("> ")
        cmd = re.split('[,\s]+', cmd.upper().strip())
        if cmd[0] == 'INIT':
            try:
                width, height = check_numeric('INIT', cmd[1:], 2, 1)
            except TypeError:
                continue
            c = cluster.NodeCluster(width, height, speed=0)
            current_node = c.nodes[1][1]
            current_code = {}
        elif cmd[0] in ['MEM', 'NODE', 'OUTPUT', 'INPUT', 'LIST', 'DELETE',
            'AUTO', 'RENUM', 'RUN', 'LOAD', 'SAVE', 'EXIT'] or cmd[0].isnumeric():
            try:
                c
            except NameError:
                print("CLUSTER UNINITIALIZED")
                continue
        else:
            print("UNKNOWN COMMAND")
            continue
        if cmd[0] == 'MEM':
            try:
                x, y = check_numeric('MEM', cmd[1:], 2, 1)
            except TypeError:
                continue
            try:
                assert x <= c.width
                assert y <= c.height
            except AssertionError:
                print("X, Y OUT OF RANGE")
                continue
            c.nodes[y][x].instructions = []
            c.nodes[y][x].memory = True
        if cmd[0] == 'NODE':
            try:
                x, y = check_numeric('NODE', cmd[1:], 2, 1)
            except TypeError:
                continue
            try:
                assert x <= c.width
                assert y <= c.height
            except AssertionError:
                print("X, Y OUT OF RANGE")
                continue
            current_node = c.nodes[y][x]
        if cmd[0].isnumeric():
            current_code[int(cmd[0])] = " ".join(cmd[1:])
            current_node.code = ""
            for i in sorted(current_code.keys()):
                current_node.code += current_code[i]
                current_node.code += "\n"
            try:
                current_node.parse_code()
            except Exception:
                print(f"INVALID COMMAND: {' '.join(cmd[1:])}")
                del current_code[int(cmd[0])]
                for i in sorted(current_code.keys()):
                    current_node.code += current_code[i]
                    current_node.code += "\n"
                current_node.parse_code()

        if cmd[0] == 'OUTPUT':
            try:
                x, y = check_numeric('OUTPUT', cmd[1:], 2)
            except TypeError:
                continue
            try:
                assert x <= (c.width + 1)
                assert y <= (c.height + 1)
            except AssertionError:
                print("X, Y OUT OF RANGE")
                continue
            c.nodes[y][x].instructions = []
            c.outputs.append((x, y))
            c.output_lists[(x, y)] = []
        if cmd[0] == 'INPUT':
            try:
                x, y = check_numeric('INPUT', cmd[1:], 2)
            except TypeError:
                continue
            try:
                assert x <= (c.width + 1)
                assert y <= (c.height + 1)
            except AssertionError:
                print("X, Y OUT OF RANGE")
                continue
            inputs = []
            while True:
                current_input = input(">> ")
                if current_input == "":
                    break
                try:
                    inputs.append(int(current_input))
                except ValueError:
                    print("INPUT MUST BE INTEGER")
                    continue
            c.inputs[x, y] = inputs
            c.nodes[y][x].code = c.create_input(x, y)
            c.nodes[y][x].parse_code()
        if cmd[0] == 'LIST':
            for i in sorted(current_code.keys()):
                print(f"{i}: {current_code[i]}")
        if cmd[0] == 'DELETE':
            try:
                first_line, last_line = check_numeric('DELETE', cmd[1:], 1)
            except ValueError:
                first_line = check_numeric('DELETE', cmd[1:], 1)
                last_line = first_line
            except TypeError:
                continue
            for i in range(first_line, last_line+1):
                if i in current_code:
                    del current_code[i]
        if cmd[0] == 'AUTO':
            skip = check_numeric('AUTO', cmd[1:], 0)
            if skip is None:
                skip = 10
            try:
                current_line = sorted(current_code.keys())[-1]
                current_line = (current_line // skip) * skip
                current_line += skip
            except:
                current_line = skip
            while True:
                code = input(f"{current_line}: ")
                if code == "":
                    break
                current_code[current_line] = code
                current_node.code = ""
                for i in sorted(current_code.keys()):
                    current_node.code += current_code[i]
                    current_node.code += "\n"
                try:
                    current_node.parse_code()
                except Exception:
                    print(f"INVALID COMMAND: {' '.current_code[current_line]}")
                    del current_code[current_line]
                    for i in sorted(current_code.keys()):
                        current_node.code += current_code[i]
                        current_node.code += "\n"
                    current_node.parse_code()
                    continue
                current_line += skip
        if cmd[0] == 'RENUM':
            skip = check_numeric('RENUM', cmd[1:], 0)
            if skip is None:
                skip = 10
            new_code = {}
            current_line = skip
            for i in sorted(current_code.keys()):
                new_code[current_line] = current_code[i]
                current_line += skip
            current_code = new_code
        if cmd[0] == 'RUN':
            c.run()
        if cmd[0] == 'EXIT':
            break


if __name__ == '__main__':
    prompt()
