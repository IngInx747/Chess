from ChessBoard import *
from ChessView import ChessView
from AI import *
import time, threading

def real_coord(x):
    if x <= 100:
        return 0
    else:
        return (x-100)/100 + 1

def board_coord(x):
    return 100 * x + 50

class ChessGame:

    Distribution_Info = ["Standard Opening", "Single Rook Kill", "Pawn eat pawn passing by"]
    Game_Mode_Info = ["Human vs Human", "Human vs AI", "AI vs AI"]

    def __init__(self, mode = 1, dis = 0, showMove = True, showSearch = False, showGUI = True, saveInfo = False):
        self.board = ChessBoard()
        self.Player_Side = False
        self.GameMode = mode
        self.distribution = dis

        self.ai_0 = AI()
        self.ai_1 = AI()

        self.ShowMoveInfo = showMove
        self.ShowSearchInfo = showSearch
        self.ShowGraphUI = showGUI
        self.SaveInfo = saveInfo

        self.view = ChessView(self)

    def Set(self, mode = 1, dis = 0, showMove = True, showSearch = False, showGUI = True,
            saveInfo = False, savePath = r".\Records",
            ai_name_0 = "MinMaxSearch", use_pos_0 = False, depth_0 = 3,
            ai_name_1 = "MinMaxSearch", depth_1 = 3, use_pos_1 = False):
        self.GameMode = mode
        self.distribution = dis
        self.ShowMoveInfo = showMove
        self.ShowSearchInfo = showSearch
        self.ShowGraphUI = showGUI
        self.SaveInfo = saveInfo
        self.SavePath = savePath
        self.SaveFileName = ""
        if ai_name_0 == "MinMaxSearch":
            ai_0 = MinMaxSearchAI(depth_0, True, use_pos_0)
        else:
            ai_0 = RandomMoveAI()
        if ai_name_1 == "MinMaxSearch":
            ai_1 = MinMaxSearchAI(depth_1, True, use_pos_1)
        else:
            ai_1 = RandomMoveAI()
        self.SetAI(ai_0, ai_1)

    def SetGame(self, mode = 1, dis = 0):
        self.GameMode = mode
        self.distribution = dis

    def SetInfo(self, showMove = True, showSearch = False, showGUI = True, saveInfo = False):
        self.ShowMoveInfo = showMove
        self.ShowSearchInfo = showSearch
        self.ShowGraphUI = showGUI
        self.SaveInfo = saveInfo

    def SetAI(self, ai_0, ai_1):
        self.ai_0 = ai_0
        self.ai_1 = ai_1

    def start(self):

        timeInfo = time.strftime('%Y-%m-%d %H:%M:%S')
        timeLabel = time.strftime('%Y-%m-%d-%H-%M-%S')

        self.SaveFileName = timeLabel + ".txt"

        Msg = timeInfo + " " \
              + ChessGame.Game_Mode_Info[self.GameMode] + " " \
              + ChessGame.Distribution_Info[self.distribution] + "\n"
        Msg_AI = ""
        if self.GameMode == 1:
            Msg_AI += str(self.ai_0) + "\n"
        elif self.GameMode == 2:
            Msg_AI += str(self.ai_0) + "\n"
            Msg_AI += str(self.ai_1) + "\n"

        print Msg + Msg_AI,
        if self.SaveInfo:
            self.SaveData(Msg + Msg_AI)

        self.board.Board_Initialization(self.distribution)

        if self.GameMode == 2:
            if not self.ShowGraphUI:
                self.Game_AIvAI_Auto(self.ai_0, self.ai_1)

        self.view.showMsg("Chess")
        self.view.draw_board(self.board)
        self.view.start()

    def callback(self, event):
        rx, ry = real_coord(event.x), real_coord(800 - event.y)
        self.Game(rx, ry, self.GameMode)

    def Move_Info(self, move_info):
        game_info = {0:"", 1:" #", 2:" #", 3:" Stalemate", 4:" Draw", 5:" Perpetual check"}
        return "(" + str(self.board.Round) + "):" + move_info \
        + game_info[self.board.Status] \
        + ("; " if self.Player_Side else ";\n")

    def SaveData(self, info):
        fileName = self.SavePath + r'\chess-' + self.SaveFileName
        with open(fileName, 'a') as data:
            data.write(info)

    def Game(self, x, y, mode = 0):
        if mode == 0:
            self.Game_PvP(x, y)
        elif mode == 1:
            self.Game_PvAI(x, y)
        elif mode == 2:
            self.Game_AIvAI(self.ai_0, self.ai_1)
        else:
            raise Exception("Invalid game mode: " + str(mode))

    def Game_PvP(self, rx, ry):
        if self.board.Status != 0:
            return
        move_info = self.board.select(rx, ry, self.Player_Side)
        if move_info != "":
            self.view.showMsg("White turn" if self.Player_Side else "Black turn")
            self.Player_Side = not self.Player_Side
            self.board.Round += 1
            self.board.UpdateStatu()
            if self.ShowMoveInfo:
                print self.Move_Info(move_info),
                if self.SaveInfo:
                    self.SaveData(self.Move_Info(move_info))
        self.view.draw_board(self.board)

    def Game_PvAI(self, rx, ry):
        if self.board.Status != 0:
            return
        move_info = self.board.select(rx, ry, self.Player_Side)
        self.view.draw_board(self.board)
        if move_info != "":
            self.view.showMsg("White turn" if self.Player_Side else "Black turn")
            self.Player_Side = not self.Player_Side
            self.board.Round += 1
            self.board.UpdateStatu()
            if self.ShowMoveInfo:
                print self.Move_Info(move_info),
                if self.SaveInfo:
                    self.SaveData(self.Move_Info(move_info))
            self.view.draw_board(self.board)

            if self.board.Status != 0:
                return

            move, msg = self.ai_0.Play(self.board, self.Player_Side)
            self.board.select(move[0][0], move[0][1], self.Player_Side)
            move_info = self.board.select(move[1][0], move[1][1], self.Player_Side)
            self.view.showMsg("White turn" if self.Player_Side else "Black turn")
            self.Player_Side = not self.Player_Side
            self.board.Round += 1
            self.board.UpdateStatu()
            if self.ShowSearchInfo:
                print msg,
                if self.SaveInfo:
                    self.SaveData(msg + " ")
            if self.ShowMoveInfo:
                print self.Move_Info(move_info),
                if self.SaveInfo:
                    self.SaveData(self.Move_Info(move_info))
            self.view.draw_board(self.board)

    def Game_AIvAI(self, ai_0, ai_1):
        if self.board.Status != 0:
            return
        if self.Player_Side == False:
            ai_0.Clear()
            move, msg = ai_0.Play(self.board, self.Player_Side)
        else:
            ai_1.Clear()
            move, msg = ai_1.Play(self.board, self.Player_Side)
        self.board.select(move[0][0], move[0][1], self.Player_Side)
        move_info = self.board.select(move[1][0], move[1][1], self.Player_Side)
        self.view.showMsg("White turn" if self.Player_Side else "Black turn")
        self.Player_Side = not self.Player_Side
        self.board.Round += 1
        self.board.UpdateStatu()
        if self.ShowSearchInfo:
            print msg,
            if self.SaveInfo:
                self.SaveData(msg + " ")
        if self.ShowMoveInfo:
            print self.Move_Info(move_info),
            if self.SaveInfo:
                self.SaveData(self.Move_Info(move_info))
        self.view.draw_board(self.board)

    def Game_AIvAI_Auto(self, ai_0, ai_1):
        while self.board.Status == 0:
            ai_0.Clear()
            move, msg = ai_0.Play(self.board, self.Player_Side)
            self.board.select(move[0][0], move[0][1], self.Player_Side)
            move_info = self.board.select(move[1][0], move[1][1], self.Player_Side)
            self.view.showMsg("White turn" if self.Player_Side else "Black turn")
            self.Player_Side = not self.Player_Side
            self.board.Round += 1
            self.board.UpdateStatu()
            if self.ShowSearchInfo:
                print msg,
                if self.SaveInfo:
                    self.SaveData(msg + " "),
            if self.ShowMoveInfo:
                print self.Move_Info(move_info),
                if self.SaveInfo:
                    self.SaveData(self.Move_Info(move_info))

            if self.board.Status != 0:
                self.SaveData("\n")
                print ""
                break

            ai_1.Clear()
            move, msg = ai_1.Play(self.board, self.Player_Side)
            self.board.select(move[0][0], move[0][1], self.Player_Side)
            move_info = self.board.select(move[1][0], move[1][1], self.Player_Side)
            self.view.showMsg("White turn" if self.Player_Side else "Black turn")
            self.Player_Side = not self.Player_Side
            self.board.Round += 1
            self.board.UpdateStatu()
            if self.ShowSearchInfo:
                print msg,
                if self.SaveInfo:
                    self.SaveData(msg + " ")
            if self.ShowMoveInfo:
                print self.Move_Info(move_info),
                if self.SaveInfo:
                    self.SaveData(self.Move_Info(move_info))

        print self.board
        print self.board.Status
        if self.SaveInfo:
            self.SaveData(str(self.board)+"\n")
            self.SaveData(str(self.board.Status) + "\n")