import Tkinter

def board_coord(x):
    return 100 * x + 50

class ChessView:
    root = Tkinter.Tk()
    root.title("Chess")
    root.resizable(0, 0)
    can = Tkinter.Canvas(root, width=800, height=800)
    can.pack(expand=Tkinter.YES, fill=Tkinter.BOTH)
    img = Tkinter.PhotoImage(file="images/ChessBoard.gif")
    can.create_image(0, 0, image=img, anchor=Tkinter.NW)
    piece_images = dict()
    move_images = []

    def draw_board(self, board):
        self.piece_images.clear()
        self.move_images = []
        pieces = board.Pieces
        for (x, y) in pieces.keys():
            self.piece_images[x, y] = Tkinter.PhotoImage(file=pieces[x, y].get_image_file_name())
            self.can.create_image(board_coord(x), board_coord(7-y), image=self.piece_images[x, y])
        if board.PieceSelected:
            self.move_images.append(Tkinter.PhotoImage(file="images/select.gif"))
            self.can.create_image(board_coord(board.PieceSelected.x), board_coord(7 - board.PieceSelected.y), image=self.move_images[-1])
            for (x, y) in board.PieceSelected.Get_Move_Locs(board):
                self.move_images.append(Tkinter.PhotoImage(file="images/select.gif"))
                self.can.create_image(board_coord(x), board_coord(7-y), image=self.move_images[-1])

    def showMsg(self, msg):
        self.root.title(msg)

    def __init__(self, control):
        self.control = control
        self.can.bind('<Button-1>', self.control.callback)

    def start(self):
        Tkinter.mainloop()
