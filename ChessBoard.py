import copy
from ChessPiece import *

class ChessBoard:

    MaxRound = 300
    MidRound = 50

    def __init__(self):
        self.Pieces = dict()
        self.PieceSelected = None
        self.Status = 0
        self.Round = 0
        self.LastMove = [(-1,-1), (-1,-1)]

    def __str__(self):
        info = ""
        for piece in self.Pieces.values():
            info += str(piece)
            info += " "
        return info

    def __deepcopy__(self, memodict={}):
        newBoard = ChessBoard()
        if self.PieceSelected:
            newBoard.PieceSelected = self.PieceSelected.__deepcopy__()
        newBoard.Status = self.Status
        newBoard.Round = self.Round
        newBoard.LastMove = self.LastMove
        for key in self.Pieces.keys():
            newBoard.Pieces[key] = self.Pieces[key].__deepcopy__()
            # newBoard.Pieces[key] = copy.deepcopy(self.Pieces[key])
        return newBoard

    @staticmethod
    def Move_Info(x, y):
        ascii = ["a", "b", "c", "d", "e", "f", "g", "h"]
        x = int(x) % 8
        return ascii[x] + str(int(y) + 1)

    def Is_Legal_Move(self, x, y, dx, dy):
        return self.Pieces[x, y].Is_Legal_Move(self, dx, dy)

    def Move(self, x, y, dx, dy):
        self.LastMove = [(x, y), (x + dx, y + dy)]
        return self.Pieces[x, y].Move(self, dx, dy)

    def Move_(self, position, move):
        self.LastMove = [position, move]
        return self.Pieces[position].Move(self, move[0] - position[0], move[1] - position[1])

    def remove(self, x, y):
        del self.Pieces[x, y]

    def select(self, x, y, camp):
        if not self.PieceSelected:
            if (x, y) in self.Pieces and self.Pieces[x, y].BlackOrWhite == camp:
                self.Pieces[x, y].IsSelected = True
                self.PieceSelected = self.Pieces[x, y]
            return ""

        moves = self.PieceSelected.Get_Move_Locs(self)

        if (x, y) in moves:
            self.Pawn_Eat_Pawn_Pass_By(x, y) # Only for preparation to eat pawn passing by

        if not (x, y) in self.Pieces.keys():
            if self.PieceSelected:
                ox, oy = self.PieceSelected.x, self.PieceSelected.y
                #moves = self.PieceSelected.Get_Move_Locs(self)
                if (x, y) in moves: # self.Is_Legal_Move(ox, oy, x-ox, y-oy):
                    move_info = ""
                    if self.PieceSelected.IsKing \
                            and self.PieceSelected.Moved == False \
                            and self.Can_Castling(x, y):
                        move_info = self.Castling(x, y)
                    else:
                        self.Move(ox, oy, x-ox, y-oy)
                        if self.PieceSelected.PieceType == 5:
                            Piece_Type_Promotion = 1
                            if self.Pawn_Promotion(x, y, Piece_Type_Promotion):
                                self.PieceSelected.Name = ChessPiece.Get_Name(Piece_Type_Promotion)
                        if self.KingUnderAttack(not self.PieceSelected.BlackOrWhite):
                            move_info = self.PieceSelected.Name + " " + ChessBoard.Move_Info(ox, oy) \
                                        + " + " + ChessBoard.Move_Info(x, y)
                        else:
                            move_info = self.PieceSelected.Name + " " + ChessBoard.Move_Info(ox, oy) \
                                        + " - " + ChessBoard.Move_Info(x, y)
                    self.PieceSelected.Moved = True
                    self.PieceSelected.IsSelected = False
                    self.PieceSelected = None
                    return move_info
                else:
                    self.PieceSelected = None
            return ""

        if self.Pieces[x, y].BlackOrWhite != camp:
            ox, oy = self.PieceSelected.x, self.PieceSelected.y
            if (x, y) in moves:
                self.Move(ox, oy, x-ox, y-oy)
                if self.PieceSelected.PieceType == 5:
                    Piece_Type_Promotion = 1
                    if self.Pawn_Promotion(x, y, Piece_Type_Promotion):
                        self.PieceSelected.Name = ChessPiece.Get_Name(Piece_Type_Promotion)
                if self.KingUnderAttack(not self.PieceSelected.BlackOrWhite):
                    move_info = self.PieceSelected.Name + " " + ChessBoard.Move_Info(ox, oy) \
                                + " X+" + ChessBoard.Move_Info(x, y)
                else:
                    move_info = self.PieceSelected.Name + " " + ChessBoard.Move_Info(ox, oy) \
                                + " X " + ChessBoard.Move_Info(x, y)
                self.PieceSelected.Moved = True
                self.PieceSelected.IsSelected = False
                self.PieceSelected = None
                return move_info
            return ""

        for key in self.Pieces.keys():
            self.Pieces[key].IsSelected = False
        self.Pieces[x, y].IsSelected = True
        self.PieceSelected = self.Pieces[x,y]
        return ""

    def Select_For_AI(self, position, move):
        x, y = move[0], move[1]
        self.PieceSelected = self.Pieces[position]
        if self.Pieces[position].IsKing and self.PieceSelected.Moved == False and self.Can_Castling(x, y):
            self.Castling(x, y)
        else:
            self.Pawn_Eat_Pawn_Pass_By(x, y)
            self.Move_(position, move)
            if self.PieceSelected.PieceType == 5:
                Piece_Type_Promotion = 1
                self.Pawn_Promotion(x, y, Piece_Type_Promotion)

    def IsStalemate(self):
        if len(self.Pieces) == 2:
            return True
        elif len(self.Pieces) == 3:
            for piece in self.Pieces.values():
                if piece.PieceType == 3 or piece.PieceType == 4:
                    return True
        elif len(self.Pieces) == 4:
            i = 0
            pieces_remain = []
            for piece in self.Pieces.values():
                if piece.PieceType != 0:
                    pieces_remain.append(piece)
                    i += 1
            if pieces_remain[0].PieceType == 3 and pieces_remain[1].PieceType == 3:
                if pieces_remain[0].BlackOrWhite != pieces_remain[1].BlackOrWhite:
                    x0 = pieces_remain[0].x
                    y0 = pieces_remain[0].y
                    x1 = pieces_remain[1].x
                    y1 = pieces_remain[1].y
                    if (x0 + y0) % 2 == (x1 + y1) % 2:
                        return True
            return False

    def UpdateStatu(self):
        """0:Gaming; 1:White Win; 2:Black Win; 3: Stalemate; 4:Draw; 5:Perpetual check; """
        Succ_Count_White = Succ_Count_Black = 0

        if self.IsStalemate():
            self.Status = 4
            return

        for piece in self.Pieces.values():
            if piece.BlackOrWhite == False:
                Succ_Count_White += len(piece.Get_Move_Locs(self))
            else:
                Succ_Count_Black += len(piece.Get_Move_Locs(self))

        if Succ_Count_White != 0 and Succ_Count_Black == 0:
            if self.KingUnderAttack(True):
                self.Status = 1
            else:
                self.Status = 3
        elif Succ_Count_Black != 0 and Succ_Count_White == 0:
            if self.KingUnderAttack(False):
                self.Status = 2
            else:
                self.Status = 3
        elif Succ_Count_Black == 0 and Succ_Count_White == 0:
            self.Status = 3
        elif self.Round >= ChessBoard.MaxRound:
            self.Status = 5

    def UnderAttack(self, x, y, camp):
        for piece in self.Pieces.values():
            if piece.BlackOrWhite != camp:
                if piece.Is_Legal_Move(self, x-piece.x, y-piece.y):
                    return True
        return False

    def KingUnderAttack(self, camp):
        x, y = -1, -1
        for piece in self.Pieces.values():
            if piece.IsKing and piece.BlackOrWhite == camp:
                x, y = piece.x, piece.y
                break
        return self.UnderAttack(x, y, camp)

    def Can_Castling(self, x, y):
        if x == 2 and y == 0:
            if (4, 0) in self.Pieces.keys() and (0, 0) in self.Pieces.keys():
                if self.Pieces[(4, 0)].PieceType == 0 and self.Pieces[(4, 0)].Moved == False:
                    if self.Pieces[(0, 0)].PieceType == 2 and self.Pieces[(0, 0)].Moved == False:
                        for i in range(1, 5):
                            if self.UnderAttack(i, 0, False):
                                return False
                        return True
        elif x == 6 and y == 0:
            if (4, 0) in self.Pieces.keys() and (7, 0) in self.Pieces.keys():
                if self.Pieces[(4, 0)].PieceType == 0 and self.Pieces[(4, 0)].Moved == False:
                    if self.Pieces[(7, 0)].PieceType == 2 and self.Pieces[(7, 0)].Moved == False:
                        for i in range(4, 8):
                            if self.UnderAttack(i, 0, False):
                                return False
                        return True
        elif x == 2 and y == 7:
            if (4, 7) in self.Pieces.keys() and (0, 7) in self.Pieces.keys():
                if self.Pieces[(4, 7)].PieceType == 0 and self.Pieces[(4, 7)].Moved == False:
                    if self.Pieces[(0, 7)].PieceType == 2 and self.Pieces[(0, 7)].Moved == False:
                        for i in range(1, 5):
                            if self.UnderAttack(i, 7, True):
                                return False
                        return True
        elif x == 6 and y == 7:
            if (4, 7) in self.Pieces.keys() and (7, 7) in self.Pieces.keys():
                if self.Pieces[(4, 7)].PieceType == 0 and self.Pieces[(4, 7)].Moved == False:
                    if self.Pieces[(7, 7)].PieceType == 2 and self.Pieces[(7, 7)].Moved == False:
                        for i in range(4, 8):
                            if self.UnderAttack(i, 7, True):
                                return False
                        return True

    def Castling(self, x, y):
        if x == 2 and y == 0:
            self.Pieces[(4, 0)].Move(self, -2, 0)
            self.Pieces[(0, 0)].Move(self, 3, 0)
            return "0-0-0"
        elif x == 6 and y == 0:
            self.Pieces[(4, 0)].Move(self, 2, 0)
            self.Pieces[(7, 0)].Move(self, -2, 0)
            return "0-0"
        elif x == 2 and y == 7:
            self.Pieces[(4, 7)].Move(self, -2, 0)
            self.Pieces[(0, 7)].Move(self, 3, 0)
            return "0-0-0"
        elif x == 6 and y == 7:
            self.Pieces[(4, 7)].Move(self, 2, 0)
            self.Pieces[(7, 7)].Move(self, -2, 0)
            return "0-0"
        return ""

    def Pawn_Promotion(self, x, y, pieceType = 1):
        if self.Pieces[(x,y)].PieceType == 5 and y == 0 or y == 7:
            camp = self.Pieces[(x,y)].BlackOrWhite
            switch = {
                1: Queen(x, y, camp),
                2: Rook(x, y, camp),
                3: Bishop(x, y, camp),
                4: Knight(x, y, camp),
            }
            self.Pieces[(x,y)] = switch.get(pieceType, Queen(x, y, camp))
            return True
        return False

    def Pawn_Eat_Pawn_Pass_By(self, x, y):
        if self.PieceSelected.BlackOrWhite == False and self.PieceSelected.PieceType == 5:
            if self.PieceSelected.y == 4:
                if self.Pieces[self.LastMove[1]].PieceType == 5:
                    if self.LastMove[1][1] == 4 and self.LastMove[0][1] == 6:
                        if x == self.LastMove[1][0] and y == 5:
                            if abs(self.PieceSelected.x - x) == 1:
                                self.Move_(self.LastMove[1], (x, y))
                                return True
        elif self.PieceSelected.BlackOrWhite == True and self.PieceSelected.PieceType == 5:
            if self.PieceSelected.y == 3:
                if self.Pieces[self.LastMove[1]].PieceType == 5:
                    if self.LastMove[1][1] == 3 and self.LastMove[0][1] == 1:
                        if x == self.LastMove[1][0] and y == 2:
                            if abs(self.PieceSelected.x - x) == 1:
                                self.Move_(self.LastMove[1], (x, y))
                                return True
        return False

    def Board_Clear(self):
        self.Pieces.clear()

    def Board_Initialization(self, dis = 0):
        self.Pieces = dict()
        self.PieceSelected = None
        self.Status = 0
        self.Round = 0

        if dis == 0:
            self.Game_Standard()
        elif dis == 1:
            self.Game_Test_SingleRook()
        elif dis == 2:
            self.Game_Test_Eat_Pawn_Pass_By()
        else:
            raise Exception("ChessBoard::Board_Initialization(): No such opening!")

    def Game_Void(self):
        pass

    def Game_Standard(self):
        self.Board_Clear()

        self.Pieces[(4, 0)] = King(4, 0, False)
        self.Pieces[(3, 0)] = Queen(3, 0, False)
        self.Pieces[(0, 0)] = Rook(0, 0, False)
        self.Pieces[(7, 0)] = Rook(7, 0, False)
        self.Pieces[(2, 0)] = Bishop(2, 0, False)
        self.Pieces[(5, 0)] = Bishop(5, 0, False)
        self.Pieces[(1, 0)] = Knight(1, 0, False)
        self.Pieces[(6, 0)] = Knight(6, 0, False)
        for i in range(8):
            self.Pieces[(i, 1)] = Pawn(i, 1, False)

        self.Pieces[(4, 7)] = King(4, 7, True)
        self.Pieces[(3, 7)] = Queen(3, 7, True)
        self.Pieces[(0, 7)] = Rook(0, 7, True)
        self.Pieces[(7, 7)] = Rook(7, 7, True)
        self.Pieces[(2, 7)] = Bishop(2, 7, True)
        self.Pieces[(5, 7)] = Bishop(5, 7, True)
        self.Pieces[(1, 7)] = Knight(1, 7, True)
        self.Pieces[(6, 7)] = Knight(6, 7, True)
        for i in range(8):
            self.Pieces[(i, 6)] = Pawn(i, 6, True)

    def Game_Test_SingleRook(self):
        self.Board_Clear()

        self.Pieces[(4, 1)] = King(4, 1, False)
        self.Pieces[(4, 6)] = King(4, 6, True)
        self.Pieces[(0, 5)] = Rook(0, 5, True)
        self.Pieces[(4, 1)].Moved = True
        self.Pieces[(4, 6)].Moved = True
        self.Pieces[(0, 5)].Moved = True

    def Game_Test_Eat_Pawn_Pass_By(self):
        self.Board_Clear()

        self.Pieces[(1, 1)] = King(1, 1, False)
        self.Pieces[(7, 3)] = King(7, 3, True)
        self.Pieces[(0, 3)] = Rook(0, 3, False)
        self.Pieces[(4, 3)] = Pawn(4, 3, True)
        self.Pieces[(5, 1)] = Pawn(5, 1, False)
        self.Pieces[(4, 3)].Moved = True

    def Evaluation_Material(self, camp):
        eva = 0
        for piece in self.Pieces.values():
            if piece.BlackOrWhite == camp:
                eva += piece.Material()
            else:
                eva -= piece.Material()
        return eva

    def Evaluation_Position(self, camp):
        eva = 0
        for piece in self.Pieces.values():
            if piece.BlackOrWhite == camp: # My side
                if piece.BlackOrWhite == False:
                    eva += piece.Position_Evaluation(piece.y, piece.x, self.Round, self.MidRound)
                else:
                    eva += piece.Position_Evaluation(7 - piece.y, piece.x, self.Round, self.MidRound)
            else: # Enemy side
                if piece.BlackOrWhite == False:
                    eva -= piece.Position_Evaluation(piece.y, piece.x, self.Round, self.MidRound)
                else:
                    eva -= piece.Position_Evaluation(7 - piece.y, piece.x, self.Round, self.MidRound)
        return eva