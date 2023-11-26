import cluster
import node
import glob
import os
import re
import readline

def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)

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
        cmd = re.split('[,\s]+', cmd.strip())
        if cmd[0].upper() in ('SAVE', 'LOAD'):
            cmd[0] = cmd[0].upper()
        else:
            cmd = [x.upper() for x in cmd]
        if cmd[0] == 'INIT':
            try:
                width, height = check_numeric('INIT', cmd[1:], 2, 1)
            except TypeError:
                continue
            c = cluster.NodeCluster(width, height)
            current_node = c.nodes[1][1]
            current_code = {}
            all_code = {}
            test_outputs = {}
        elif cmd[0] in ['MEM', 'DEAD', 'NODE', 'OUTPUT', 'INPUT', 'LIST', 'DELETE',
            'AUTO', 'RENUM', 'RUN', 'STEP', 'FAST', 'LOAD', 'SAVE', 'TEST', 'IMAGE', 'IMAGE_TEST'] or cmd[0].isnumeric():
            try:
                c
            except NameError:
                print("CLUSTER UNINITIALIZED")
                continue
        elif cmd[0] == 'EXIT':
            break
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
            c.memory.append((x, y))
            c.nodes[y][x].instructions = []
            c.nodes[y][x].memory = True

        if cmd[0] == 'DEAD':
            try:
                x, y = check_numeric('DEAD', cmd[1:], 2, 1)
            except TypeError:
                continue
            try:
                assert x <= c.width
                assert y <= c.height
            except AssertionError:
                print("X, Y OUT OF RANGE")
                continue
            c.dead.append((x, y))
            c.nodes[y][x].instructions = []
            c.nodes[y][x].dead = True

        if cmd[0] == 'NODE':
            if len(cmd) == 1:
                print(f"CURRENT NODE: {current_node.x}, {current_node.y}")
                continue
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
            current_code = all_code.get((x, y), {})

        if cmd[0].isnumeric():
            current_code[int(cmd[0])] = " ".join(cmd[1:])
            current_node.code = ""
            for i in sorted(current_code.keys()):
                current_node.code += current_code[i]
                current_node.code += "\n"
            try:
                current_node.parse_code()
                all_code[(current_node.x, current_node.y)] = current_code
            except Exception:
                print(f"INVALID COMMAND: {' '.join(cmd[1:])}")
                del current_code[int(cmd[0])]
                current_node.code = ""
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
                assert (x == 0 or y == 0) or (x == c.width + 1 or y == c.height + 1)
            except AssertionError:
                print("X, Y OUT OF RANGE")
                continue
            c.outputs.append((x, y))
            c.nodes[y][x].code = c.create_output(x, y)
            c.nodes[y][x].parse_code()
            c.nodes[y][x].acc = None
            c.output_lists[(x, y)] = []

        if cmd[0] == 'IMAGE':
            try:
                x, y = check_numeric('IMAGE', cmd[1:], 2)
            except TypeError:
                continue
            try:
                assert (x, y) in c.outputs
            except AssertionError:
                print(f"{x}, {y} NOT AN OUTPUT")
                continue
            c.image_port = (x, y)
            c.image = [[0] * c.image_dim[0] for _ in range(c.image_dim[1])]

        if cmd[0] == 'IMAGE_TEST':
            try:
                x, y = check_numeric('IMAGE_TEST', cmd[1:], 2)
            except TypeError:
                continue
            try:
                assert (x, y) == c.image_port
            except AssertionError:
                print(f"{x}, {y} NOT AN IMAGE PORT")
                continue
            outputs = []
            done = False
            for y in range(c.image_dim[1]):
                for x in range(c.image_dim[0]):
                    current_input = input(">> ")
                    if current_input == "":
                        done = True
                        break
                    try:
                        outputs.append(int(current_input))
                    except ValueError:
                        try:
                            with open(current_input, 'r') as file:
                                outputs = [[int(n) for n in line.strip()] for line in file.readlines() if line != ""]
                                done = True
                                break
                        except (ValueError, FileNotFoundError):
                            print("TEST OUTPUT MUST BE INTEGER")
                            continue
                if done:
                    break
            c.test_image = outputs

        if cmd[0] == 'INPUT':
            try:
                x, y = check_numeric('INPUT', cmd[1:], 2)
            except TypeError:
                continue
            try:
                assert x <= (c.width + 1)
                assert y <= (c.height + 1)
                assert (x == 0 or y == 0) or (x == c.width + 1 or y == c.height + 1)
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
                    try:
                        with open(current_input, 'r') as file:
                            inputs = [int(line.strip()) for line in file.readlines() if line != ""]
                        break
                    except (ValueError, FileNotFoundError):
                        print("INPUT MUST BE INTEGER")
                        continue
            c.inputs[(x, y)] = inputs
            c.nodes[y][x].code = c.create_input(x, y)
            c.nodes[y][x].parse_code()

        if cmd[0] == 'TEST':
            try:
                x, y = check_numeric('TEST', cmd[1:], 2)
            except TypeError:
                continue
            try:
                assert x <= (c.width + 1)
                assert y <= (c.height + 1)
                assert (x == 0 or y == 0) or (x == c.width + 1 or y == c.height + 1)
            except AssertionError:
                print("X, Y OUT OF RANGE")
                continue
            try:
                assert (x, y) in c.outputs
            except AssertionError:
                print("X, Y NOT AN OUTPUT")
                continue
            outputs = []
            while True:
                current_input = input(">> ")
                if current_input == "":
                    break
                try:
                    outputs.append(int(current_input))
                except ValueError:
                    try:
                        with open(current_input, 'r') as file:
                            outputs = [int(line.strip()) for line in file.readlines() if line != ""]
                        break
                    except (ValueError, FileNotFoundError):
                        print("TEST OUTPUT MUST BE INTEGER")
                        continue
            test_outputs[(x, y)] = outputs
            c.test_outputs = test_outputs

        if cmd[0] == 'LIST':
            print(f"NODE {current_node.x}, {current_node.y}")
            try:
                max_chars = len(str(sorted(current_code.keys())[-1]))
            except IndexError:
                max_chars = 1
            for i in sorted(current_code.keys()):
                print(f"{i:>{max_chars}}: {current_code[i]}")

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
                    all_code[(current_node.x, current_node.y)] = current_code
                except Exception:
                    print(f"INVALID COMMAND: {current_code[current_line]}")
                    del current_code[current_line]
                    current_node.code = ""
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

        if cmd[0] == 'SAVE':
            try:
                c.save(cmd[1])
            except IndexError:
                filename = ""
                while filename == "":
                    filename = input("FILENAME: ")
                c.save(filename)

        if cmd[0] == 'LOAD':
            try:
                filename = cmd[1]
            except IndexError:
                filename = ""
                while filename == "":
                    filename = input("FILENAME: ")
            try:
                c.load(filename)
            except FileNotFoundError:
                print(f"FILE `{filename}' NOT FOUND")
                continue
            for row in c.nodes:
                for n in row:
                    i = 10
                    all_code[(n.x, n.y)] = {}
                    for line in n.code.split('\n'):
                        all_code[n.x, n.y][i] = line
                        i += 10
            current_code = all_code[(current_node.x, current_node.y)]

        if cmd[0] == 'RUN':
            c.run()

        if cmd[0] == 'STEP':
            speed = c.speed
            c.speed = 0
            c.run()
            c.speed = speed

        if cmd[0] == 'FAST':
            speed = c.speed
            c.speed = 5000
            c.run()
            c.speed = speed

        if cmd[0] == 'EXIT':
            break


if __name__ == '__main__':
    prompt()
