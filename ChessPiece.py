import copy

class ChessPiece:

    def __init__(self, x, y, Type, camp):
        self.x = x
        self.y = y
        self.BlackOrWhite = camp
        self.PieceType = Type
        self.IsKing = False
        self.IsSelected = False
        self.IsKing = False
        self.Moved = False
        self.Name = ""

    def __str__(self):
        return ("Black:" if self.BlackOrWhite else "White:") + ChessPiece.Get_Name(self.PieceType) \
               + "(" + str(self.x) + "," + str(self.y) + ")"

    def __deepcopy__(self, memodict={}):
        newPiece = ChessPiece(self.x, self.y, self.PieceType, self.BlackOrWhite)
        newPiece.IsSelected = self.IsSelected
        newPiece.IsKing = self.IsKing
        newPiece.Moved = self.Moved
        return newPiece

    @staticmethod
    def Get_Name(i):
        names = ["K", "Q", "R", "B", "N", " "]
        return names[i]

    def Is_Legal_Move(self, board, dx, dy):
        raise Exception("ChessPiece::Is_Legal_Move(..) : Virtual method is called.")

    def Get_Move_Locs(self, board):
        moves = []
        for x in xrange(8):
            for y in xrange(8):
                if (x,y) in board.Pieces and board.Pieces[x,y].BlackOrWhite == self.BlackOrWhite:
                    continue
                if self.Is_Legal_Move(board, x-self.x, y-self.y):
                    piece_copy = self.__deepcopy__()
                    board_copy = board.__deepcopy__()
                    board_copy.PieceSelected = piece_copy
                    board_copy.Pawn_Eat_Pawn_Pass_By(x, y)
                    piece_copy.Move(board_copy, x-self.x, y-self.y)
                    if board_copy.KingUnderAttack(piece_copy.BlackOrWhite) == False:
                        IsCastlingPosition = (x == 2 and y == 0) \
                                             or (x == 6 and y == 0) \
                                             or (x == 2 and y == 7) \
                                             or (x == 6 and y == 7)
                        if self.IsKing \
                                and self.Moved == False \
                                and IsCastlingPosition \
                                and board.Can_Castling(x, y) == False:
                            continue
                        else:
                            moves.append((x, y))
        return moves

    def Move(self, board, dx, dy):
        nx, ny = self.x + dx, self.y + dy
        if (nx, ny) in board.Pieces:
            board.remove(nx, ny)
        board.remove(self.x, self.y)
        # print 'Move a chessman from (%d,%d) to (%d,%d)'%(self.x, self.y, self.x+dx, self.y+dy)
        self.x += dx
        self.y += dy
        board.Pieces[self.x, self.y] = self
        return True

    def Count_Pieces_Between(self, board, x, y, dx, dy):
        sx = dx/abs(dx) if dx!=0 else 0
        sy = dy/abs(dy) if dy!=0 else 0
        nx, ny = x + dx, y + dy
        x, y = x + sx, y + sy
        cnt = 0
        while x != nx or y != ny:
            if (x, y) in board.Pieces:
                cnt += 1
            x += sx
            y += sy
        return cnt

    def Material(self):
        raise Exception("ChessPiece::Material() : Virtual method is called.")

    def Position_Evaluation(self, x, y, Round, mid = 100):
        raise Exception("ChessPiece::Position_Evaluation(..) : Virtual method is called.")

class King(ChessPiece):

    Value_Material = 20000

    Piece_Position_Eva_0 = [
        [20, 50, 10,  0,  0, 10, 50, 20],
        [20, 20,  0,  0,  0,  0, 20, 20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30]
    ]

    Piece_Position_Eva_1 = [
        [-50,-40,-30,-20,-20,-30,-40,-50],
        [-30,-30,  0,  0,  0,  0,-30,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-20,-10,  0,  0,-10,-20,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30]
    ]

    def __init__(self, x, y, camp):
        ChessPiece.__init__(self, x, y, 0, camp)
        self.IsKing = True
        self.Name = "K"

    def __deepcopy__(self, memodict={}):
        newPiece = King(self.x, self.y, self.BlackOrWhite)
        newPiece.IsSelected = self.IsSelected
        newPiece.IsKing = self.IsKing
        newPiece.Moved = self.Moved
        newPiece.Name = self.Name
        return newPiece

    def get_image_file_name(self):
        if self.IsSelected:
            if self.BlackOrWhite:
                return "images/blackking.gif"
            else:
                return "images/whiteking.gif"
        else:
            if self.BlackOrWhite:
                return "images/blackking.gif"
            else:
                return "images/whiteking.gif"

    def Is_Legal_Move(self, board, dx, dy):
        if self.Moved == False:
            if self.BlackOrWhite == False and self.x == 4 and self.y == 0:
                if dx == 2 and dy == 0:
                    if self.Count_Pieces_Between(board, 4, 0, 3, 0) == 0:
                        return True
                elif dx == -2 and dy == 0:
                    if self.Count_Pieces_Between(board, 4, 0, -4, 0) == 0:
                        return True
            elif self.BlackOrWhite == True and self.x == 4 and self.y == 7:
                if dx == 2 and dy == 0:
                    if self.Count_Pieces_Between(board, 4, 7, 3, 0) == 0:
                        return True
                elif dx == -2 and dy == 0:
                    if self.Count_Pieces_Between(board, 4, 7, -4, 0) == 0:
                        return True
        if dx>1 or dy>1 or dx<-1 or dy<-1:
            return False
        return True

    def Material(self):
        return King.Value_Material

    def Position_Evaluation(self, x, y, Round, mid = 100):
        if Round <= mid:
            return King.Piece_Position_Eva_0[x][y]
        else:
            return King.Piece_Position_Eva_1[x][y]

class Queen(ChessPiece):

    Value_Material = 925

    Piece_Position_Eva_0 = [
        [-20,-10,-10, -5, -5,-10,-10,-20],
        [-10,  0,  5,  0,  0,  0,  0,-10],
        [-10,  5,  5,  5,  5,  5,  0,-10],
        [0,  0,  5,  5,  5,  5,  0, -5],
        [-5,  0,  5,  5,  5,  5,  0, -5],
        [-10,  0,  5,  5,  5,  5,  0,-10],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-20,-10,-10, -5, -5,-10,-10,-20]
    ]

    Piece_Position_Eva_1 = [
        [-20, -10, -10, -5, -5, -10, -10, -20],
        [-10, 0, 5, 0, 0, 0, 0, -10],
        [-10, 5, 5, 5, 5, 5, 0, -10],
        [0, 0, 5, 5, 5, 5, 0, -5],
        [-5, 0, 5, 5, 5, 5, 0, -5],
        [-10, 0, 5, 5, 5, 5, 0, -10],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20]
    ]

    def __init__(self, x, y, camp):
        ChessPiece.__init__(self, x, y, 1, camp)
        self.Name = "Q"

    def __deepcopy__(self, memodict={}):
        newPiece = Queen(self.x, self.y, self.BlackOrWhite)
        newPiece.IsSelected = self.IsSelected
        newPiece.IsKing = self.IsKing
        newPiece.Moved = self.Moved
        newPiece.Name = self.Name
        return newPiece

    def get_image_file_name(self):
        if self.IsSelected:
            if self.BlackOrWhite:
                return "images/blackqueen.gif"
            else:
                return "images/whitequeen.gif"
        else:
            if self.BlackOrWhite:
                return "images/blackqueen.gif"
            else:
                return "images/whitequeen.gif"

    def Is_Legal_Move(self, board, dx, dy):
        if dx!=dy and dx!=-dy and dx!=0 and dy!=0:
            return False
        cnt = self.Count_Pieces_Between(board, self.x, self.y, dx, dy)
        if cnt != 0:
            return False
        return True

    def Material(self):
        return Queen.Value_Material

    def Position_Evaluation(self, x, y, Round, mid = 100):
        if Round <= mid:
            return Queen.Piece_Position_Eva_0[x][y]
        else:
            return Queen.Piece_Position_Eva_1[x][y]

class Rook(ChessPiece):

    Value_Material = 500

    Piece_Position_Eva_0 = [
        [0,  0,  0,  5,  5,  0,  0,  0],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [5, 10, 10, 10, 10, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0]
    ]

    Piece_Position_Eva_1 = [
        [0, 0, 0, 5, 5, 0, 0, 0],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [5, 10, 10, 10, 10, 10, 10, 5],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    def __init__(self, x, y, camp):
        ChessPiece.__init__(self, x, y, 2, camp)
        self.Name = "R"

    def __deepcopy__(self, memodict={}):
        newPiece = Rook(self.x, self.y, self.BlackOrWhite)
        newPiece.IsSelected = self.IsSelected
        newPiece.IsKing = self.IsKing
        newPiece.Moved = self.Moved
        newPiece.Name = self.Name
        return newPiece

    def get_image_file_name(self):
        if self.IsSelected:
            if self.BlackOrWhite:
                return "images/blackrook.gif"
            else:
                return "images/whiterook.gif"
        else:
            if self.BlackOrWhite:
                return "images/blackrook.gif"
            else:
                return "images/whiterook.gif"

    def Is_Legal_Move(self, board, dx, dy):
        if (dx != 0) and (dy != 0):
            return False
        cnt = self.Count_Pieces_Between(board, self.x, self.y, dx, dy)
        if cnt != 0:
            return False
        return True

    def Material(self):
        return Rook.Value_Material

    def Position_Evaluation(self, x, y, Round, mid = 100):
        if Round <= mid:
            return Rook.Piece_Position_Eva_0[x][y]
        else:
            return Rook.Piece_Position_Eva_1[x][y]

class Bishop(ChessPiece):

    Value_Material = 325

    Piece_Position_Eva_0 = [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20]
    ]

    Piece_Position_Eva_1 = [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10, 5, 0, 0, 0, 0, 5, -10],
        [-10, 10, 10, 10, 10, 10, 10, -10],
        [-10, 0, 10, 10, 10, 10, 0, -10],
        [-10, 5, 5, 10, 10, 5, 5, -10],
        [-10, 0, 5, 10, 10, 5, 0, -10],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20]
    ]

    def __init__(self, x, y, camp):
        ChessPiece.__init__(self, x, y, 3, camp)
        self.Name = "B"

    def __deepcopy__(self, memodict={}):
        newPiece = Bishop(self.x, self.y, self.BlackOrWhite)
        newPiece.IsSelected = self.IsSelected
        newPiece.IsKing = self.IsKing
        newPiece.Moved = self.Moved
        newPiece.Name = self.Name
        return newPiece

    def get_image_file_name(self):
        if self.IsSelected:
            if self.BlackOrWhite:
                return "images/blackbishop.gif"
            else:
                return "images/whitebishop.gif"
        else:
            if self.BlackOrWhite:
                return "images/blackbishop.gif"
            else:
                return "images/whitebishop.gif"

    def Is_Legal_Move(self, board, dx, dy):
        if dx!=dy and dx!=-dy:
            return False
        cnt = self.Count_Pieces_Between(board, self.x, self.y, dx, dy)
        if cnt != 0:
            return False
        return True

    def Material(self):
        return Bishop.Value_Material

    def Position_Evaluation(self, x, y, Round, mid = 100):
        if Round <= mid:
            return Bishop.Piece_Position_Eva_0[x][y]
        else:
            return Bishop.Piece_Position_Eva_1[x][y]

class Knight(ChessPiece):

    Value_Material = 300

    Piece_Position_Eva_0 = [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50]
    ]

    Piece_Position_Eva_1 = [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20, 0, 5, 5, 0, -20, -40],
        [-30, 5, 10, 15, 15, 10, 5, -30],
        [-30, 0, 15, 20, 20, 15, 0, -30],
        [-30, 5, 15, 20, 20, 15, 5, -30],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50]
    ]

    def __init__(self, x, y, camp):
        ChessPiece.__init__(self, x, y, 4, camp)
        self.Name = "N"

    def __deepcopy__(self, memodict={}):
        newPiece = Knight(self.x, self.y, self.BlackOrWhite)
        newPiece.IsSelected = self.IsSelected
        newPiece.IsKing = self.IsKing
        newPiece.Moved = self.Moved
        newPiece.Name = self.Name
        return newPiece

    def get_image_file_name(self):
        if self.IsSelected:
            if self.BlackOrWhite:
                return "images/blackknight.gif"
            else:
                return "images/whiteknight.gif"
        else:
            if self.BlackOrWhite:
                return "images/blackknight.gif"
            else:
                return "images/whiteknight.gif"

    def Is_Legal_Move(self, board, dx, dy):
        if abs(dx) == 1 and abs(dy) == 2:
            return True
        elif abs(dx) == 2 and abs(dy) == 1:
            return True
        return False

    def Material(self):
        return Knight.Value_Material

    def Position_Evaluation(self, x, y, Round, mid = 100):
        if Round <= mid:
            return Knight.Piece_Position_Eva_0[x][y]
        else:
            return Knight.Piece_Position_Eva_1[x][y]

class Pawn(ChessPiece):

    Value_Material = 100

    Piece_Position_Eva_0 = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 10, 10, -20, -20, 10, 10, 5],
        [5, -5, -10, 0, 0, -10, -5, 5],
        [0, 0, 0, 20, 20, 0, 0, 0],
        [5, 5, 10, 25, 25, 10, 5, 5],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [900, 900, 900, 900, 900, 900, 900, 900]
    ]

    Piece_Position_Eva_1 = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 10, 10, -20, -20, 10, 10, 5],
        [5, -5, -10, 0, 0, -10, -5, 5],
        [0, 0, 0, 20, 20, 0, 0, 0],
        [5, 5, 10, 25, 25, 10, 5, 5],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [900, 900, 900, 900, 900, 900, 900, 900]
    ]

    def __init__(self, x, y, camp):
        ChessPiece.__init__(self, x, y, 5, camp)
        self.Name = " "

    def __deepcopy__(self, memodict={}):
        newPiece = Pawn(self.x, self.y, self.BlackOrWhite)
        newPiece.IsSelected = self.IsSelected
        newPiece.IsKing = self.IsKing
        newPiece.Moved = self.Moved
        newPiece.Name = self.Name
        return newPiece

    def get_image_file_name(self):
        if self.IsSelected:
            if self.BlackOrWhite:
                return "images/blackpawn.gif"
            else:
                return "images/whitepawn.gif"
        else:
            if self.BlackOrWhite:
                return "images/blackpawn.gif"
            else:
                return "images/whitepawn.gif"

    def Is_Legal_Move(self, board, dx, dy):
        if self.BlackOrWhite == False:
            if dy == 1 and dx == 0:
                if not (self.x + dx, self.y + dy) in board.Pieces.keys():
                    return True
            if dy == 1 and abs(dx) == 1:
                if (self.x + dx, self.y + dy) in board.Pieces.keys():
                    return True
                elif self.y == 4:
                    if board.Pieces[board.LastMove[1]].PieceType == 5:
                        if board.LastMove[1][1] == 4 and board.LastMove[0][1] == 6:
                            if board.LastMove[1][0] == self.x + dx:
                                return True
            if self.Moved == False and dy == 2 and dx == 0:
                if not (self.x + dx, self.y + dy) in board.Pieces.keys():
                    cnt = self.Count_Pieces_Between(board, self.x, self.y, dx, dy)
                    if cnt == 0:
                        return True
        else:
            if dy == -1 and dx == 0:
                if not (self.x + dx, self.y + dy) in board.Pieces.keys():
                    return True
            if dy == -1 and abs(dx) == 1:
                if (self.x + dx, self.y + dy) in board.Pieces.keys():
                    return True
                elif self.y == 3:
                    if board.Pieces[board.LastMove[1]].PieceType == 5:
                        if board.LastMove[1][1] == 3 and board.LastMove[0][1] == 1:
                            if board.LastMove[1][0] == self.x + dx:
                                return True
            if self.Moved == False and dy == -2 and dx == 0:
                if not (self.x + dx, self.y + dy) in board.Pieces.keys():
                    cnt = self.Count_Pieces_Between(board, self.x, self.y, dx, dy)
                    if cnt == 0:
                        return True
        return False

    def Material(self):
        return Pawn.Value_Material

    def Position_Evaluation(self, x, y, Round, mid = 100):
        if Round <= mid:
            return Pawn.Piece_Position_Eva_0[x][y]
        else:
            return Pawn.Piece_Position_Eva_1[x][y]