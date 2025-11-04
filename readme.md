# TIS-100 Emulator in Python

This is a TIS-100 emulator written in Python. It is designed to be able to run standard saves from the game in the following form:

    @0  # Node ID
    MOV UP, DOWN  # Commands

    @4
    MOV UP, ACC
    ADD ACC
    MOV ACC, DOWN

    @8
    MOV UP, DOWN

By default, the emulator uses a 4x3 compute node layout. These can be customized with either a layout file or with command-line options.

A layout file looks like the following

    4 3  # The size of the emulator
    CDCC
    CDCM
    CDCC
    # The board layout, where C is a compute node, D is a dead node, and M is a
    # memory node.
    #
    # List of inputs. The number refers to the node along the top they are
    # connected to.
    I0 1 2 3
    I3 4 5 6
    # List of outputs. You can optionally also include test data after.
    O0 2 4 6
    O2 8 10 12
    O3 IMAGE  # An output can be an image node. Test image data can optionally
              # be included. Colors are numbered 0 through 4. The size of the
              # image is 30x18.
    000000000000000000000000000000
    000000000000000000000000000000
    000000000000000000000000000000
    000000000000000000000000000000
    000000000000030000000000000000
    000000000000333000000000000000
    000000000003333300000000000000
    000000000033333330000000000000
    000000000000000000000000000000
    000000000000000000000000000000
    000000000000000000000000000000
    000000000000000000000000000000
    000000000000000000000000000000
    000000000000000000000000000000
    000000000000000000000000000000
    000000000000000000000000000000
    000000000000000000000000000000
    000000000000000000000000000000

If a layout file is not used, options can be specified from the command line. These options can also be seen with `--help`.

`-s, --speed`: The speed of the emulation in Hz. Defaults to 50 Hz. This only takes effect when used with `--gui`. When the program is run without `--gui`, the program runs as fast as possible.

`-w, --width`: The width of the emulation. Defaults to 4.

`-h, --height`: The height of the emulation. Defaults to 3.

`-l, --layout`: A file with layout data, specified above. If this option is specified, all options aside from `--speed` and `--gui` are ignored.

`-i, --input`: A node index that has an input connected to it. The node must be on the boundary, and inputs are placed above, to the left, below, and to the right, in that order of precedence. This argument can be used multiple times to define multiple inputs.

`--data`: A file with input data. Data is read one input per line. Can also read from stdin.

`-o, --output`: A node index that has an output connected to it. The node must be on the boundary, and outputs are placed below, to the right, above, and to the left, in that order of precedence. This argument can be used multiple times to define multiple outputs. Note that that this index differs from the number used in the layout file; an output below node 8 on a 4x3 emulator would use `-o 8`, but in the layout file, this would be `O0`.

`--output_image`: A node index that has an image output connected to it. Works the same as the `--output` argument, but there can only be one image output. Images are 30x18 in size.

`--test_data`: A file with test output data, one output per line, to compare the outputs against.

`--test_image`: A file with test image data to compare the output image against.

`-m, --memory`:  A node index that is a stack memory node. This argument can be used multiple times to define multiple memory nodes.

`-d, --dead`: A node index that is a dead node. This argument can be used multiple times to define multiple dead nodes.

`-g, --gui`: Shows the graphical user interface when running.

`--help`: Shows the help message.

Node indices specified via command line options are numbered from 0 starting in the upper left and going across then down. In the program file, indices skip all memory and dead nodes, but when specifying indices, these are not skipped.
