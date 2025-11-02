#! /usr/bin/env python3

import argparse
import re
import sys
import time
import cluster

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TIS-100 Emulator', add_help=False)
    parser.add_argument('-s', '--speed', type=int,
        help="Clock speed in Hz (default 50).", default=50)
    parser.add_argument('-w', '--width', type=int,
        help="Width of the node cluster (default 4).", default=4)
    parser.add_argument('-h', '--height', type=int,
        help="Height of the node cluster (default 3).", default=3)
    parser.add_argument('-l', '--layout', type=argparse.FileType('r'),
        help="File with layout data. If this option is specified, all other layout options are ignored.")
    parser.add_argument('-i', '--input', type=int, action='append', default=[],
        help="Node index that has an input connected to it. Nodes must be on the cluster boundary. This argument can be used multiple times.")
    parser.add_argument('--data', type=argparse.FileType('r'), default=(None if sys.stdin.isatty() else sys.stdin),
        help="File with input data. Data is read one input per line. Defaults to stdin.")
    parser.add_argument('-o', '--output', type=int, action='append', default=[],
        help="Node index that has an output connected to it. Nodes must be on the cluster boundary. This argument can be used multiple times.")
    parser.add_argument('--output_image', type=int,
        help="Node index to be treated as an image output. Only one image output is supported.")
    parser.add_argument('--test_data', type=argparse.FileType('r'),
        help="File with test data to compare outputs against.")
    parser.add_argument('--test_image', type=argparse.FileType('r'),
        help="File with image test data to compare image output against.")
    parser.add_argument('-m', '--memory', type=int, action='append', default=[],
        help="Node index that is a stack memory node. This argument can be used multiple times.")
    parser.add_argument('-d', '--dead', type=int, action='append', default=[],
        help="Node index of a dead node. This argument can be used multiple times.")
    parser.add_argument('-g', '--gui', action='store_true',
        help="Use this flag to display the graphical interface.")
    parser.add_argument('file', type=str,
        help="Name of file to load as a program.")
    parser.add_argument('--help', action='help',
        help='Show this help message and exit.')

    args = parser.parse_args()

    data = None
    test = None
    test_image = []

    if args.layout:
        lines = args.layout.read().splitlines()
        size = re.findall(r'\d+', lines[0])
        try:
            args.width = int(size[0])
            args.height = int(size[1])
        except IndexError:
            print("Invalid size definition in layout file.")
            sys.exit()
        args.input = []
        args.output = []
        args.output_image = None
        args.memory = []
        args.dead = []
        i = 0
        for line in lines[1:args.height+1]:
            for c in line.ljust(args.width, 'C'):
                if c.upper() == 'M':
                    args.memory.append(i)
                if c.upper() == 'D':
                    args.dead.append(i)
                i += 1
        data_dict = {}
        test_dict = {}
        for line in lines[args.height+1:]:
            input_re = re.compile(r'^I(\d+)(?:\s+([A-Za-z]+))?(?:\s+(-?\d+(?:\s+-?\d+)*))?$')
            output_re = re.compile(r'^O(\d+)(?:\s+([A-Za-z]+))?(?:\s+(-?\d+(?:\s+-?\d+)*))?$')
            image_re = re.compile(r'^(\d+)$')
            match = input_re.match(line)
            if match:
                args.input.append(int(match.group(1)))
                if match.group(3):
                    data_dict[int(match.group(1))] = match.group(3)
            match = output_re.match(line)
            if match:
                if match.group(2) and match.group(2) == "IMAGE":
                    args.output_image = (args.height - 1) * args.width + int(match.group(1))

                else:
                    args.output.append((args.height - 1) * args.width + int(match.group(1)))
                if match.group(3):
                    test_dict[int(match.group(1))] = match.group(3)
            match = image_re.match(line)
            if match:
                test_image.append([int(x) for x in match.group(1)])


        if data_dict.keys():
            data = []
            for i in sorted(data_dict.keys()):
                data.append(data_dict[i])
        if test_dict.keys():
            test = []
            for i in sorted(test_dict.keys()):
                test.append(test_dict[i])

    if not data and args.data:
        data = args.data.read().splitlines()

    if not test and args.test_data:
        test = args.test_data.read().splitlines()
    if not test_image and args.test_image:
        try:
            test_image = args.test_image.read().splitlines()
            test_image = [[int(x) for x in line] for line in test_image]
        except:
            test_image = []

    c = cluster.NodeCluster(args.width, args.height, speed=args.speed, gui=args.gui, test_image=test_image)

    for i, node in enumerate(sorted(args.input)):
        x = node % args.width + 1
        y = node // args.width + 1
        if y == 1:
            y = 0
        elif y == args.height:
            y = args.height + 1
        elif x == 1:
            x = 0
        elif x == args.width:
            x = args.width + 1
        try:
            c.inputs[(x, y)] = [int(x) for x in re.findall(r'-?\d+', data[i])]
        except:
            print(f"Cound not load data for input {node}.")
            time.sleep(1)
            c.inputs[(x, y)] = []
        c.nodes[y][x].code = c.create_input(x, y)
        c.nodes[y][x].parse_code()

    for i, node in enumerate(sorted(args.output)):
        x = node % args.width + 1
        y = node // args.width + 1
        if y == 1:
            y = 0
        elif y == args.height:
            y = args.height + 1
        elif x == 1:
            x = 0
        elif x == args.width:
            x = args.width + 1
        c.outputs.append((x, y))
        try:
            c.test_outputs[(x, y)] = [int(x) for x in re.findall(r'-?\d+', test[i])]
        except:
            pass
        c.nodes[y][x].code = c.create_output(x, y)
        c.nodes[y][x].parse_code()
        c.nodes[y][x].acc = None
        c.output_lists[(x, y)] = []

    if args.output_image:
        x = args.output_image % args.width + 1
        y = args.output_image // args.width + 1
        if y == 1:
            y = 0
        elif y == args.height:
            y = args.height + 1
        elif x == 1:
            x = 0
        elif x == args.width:
            x = args.width + 1
        c.outputs.append((x, y))
        c.nodes[y][x].code = c.create_output(x, y)
        c.nodes[y][x].parse_code()
        c.nodes[y][x].acc = None
        c.output_lists[(x, y)] = []
        c.image_port = (x, y)
        c.image = [[0] * c.image_dim[0] for _ in range(c.image_dim[1])]

    for node in args.memory:
        x = node % args.width + 1
        y = node // args.width + 1
        c.memory.append((x, y))
        c.nodes[y][x].memory = True

    for node in args.dead:
        x = node % args.width + 1
        y = node // args.width + 1
        c.dead.append((x, y))
        c.nodes[y][x].dead = True

    try:
        c.load(args.file)
        c.run()
    except FileNotFoundError:
        print(f"File `{filename}' not found.")

