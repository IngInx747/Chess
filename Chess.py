from ChessGame import *

def readCommand( argv ):

    from optparse import OptionParser

    usage = " "
    parser = OptionParser()

    parser.add_option("-m", "--mode", dest="Mode", type="int", action="store", default=1)
    parser.add_option("-o", "--opening", dest="Distribution", type="int", action="store", default=0)
    parser.add_option("-i", "--moveInfo", dest="ShowMove", action="store_true", default=False)
    parser.add_option("-I", "--searchInfo", dest="ShowSearch", action="store_true", default=False)
    parser.add_option("-a", "--auto", dest="auto", action="store_true", default=False)
    parser.add_option("-d", "--depth_0", dest="depth_0", type="int", action="store", default=3)
    parser.add_option("-D", "--depth_1", dest="depth_1", type="int", action="store", default=3)
    parser.add_option("-p", "--pos_eva_0", dest="use_pos_0", action="store_true", default=False)
    parser.add_option("-P", "--pos_eva_1", dest="use_pos_1", action="store_true", default=False)
    parser.add_option("-s", "--save", dest="SaveInfo", action="store_true", default=False)

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception("Command line input not understood: " + str(otherjunk))
    args = dict()

    args["mode"] = options.Mode
    args["dis"] = options.Distribution
    args["depth_0"] = options.depth_0
    args["depth_1"] = options.depth_1

    if options.ShowMove == True:
        args["showMove"] = True
    else:
        args["showMove"] = False
    if options.ShowSearch != True:
        args["showSearch"] = False
    else:
        args["showSearch"] = True

    if options.auto == True:
        args["showGUI"] = False
        args["mode"] = 2
    else:
        args["showGUI"] = True

    if options.use_pos_0 == True:
        args["use_pos_0"] = True

    if options.use_pos_1 == True:
        args["use_pos_1"] = True

    if options.SaveInfo == True:
        args["saveInfo"] = True

    return args

if __name__ == '__main__':

    import sys
    args = readCommand(sys.argv[1:])  # Get game components based on input
    game = ChessGame()
    game.Set(**args)
    game.start()