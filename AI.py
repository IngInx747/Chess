import random, Queue, threading

class Node:

    def __init__(self, v = 0, father = None):
        self.value = v
        self.depth = 0
        self.father = father
        self.children = []

    def IsLeaf(self):
        if self is not None and len(self.children) == 0:
            return True
        else:
            return False

    def GetDepth(self):
        if self is not None:
            return self.depth
        else:
            return -1

    def Add_Child(self, node):
        if self is not None:
            if node is not None:
                node.Update_Depth()
                self.children.append(node)
                return True
            else:
                return False
        else:
            raise Exception("Node: Add_Child(..): null reference")

    def Del_Children(self):
        if self is not None:
            if self.IsLeaf() == False:
                for node in self.children:
                    node.Del_Children()
                self.children = []
                return True
            else:
                return False
        else:
            raise Exception("Node: Add_Child(..): null reference")

    def Count_Nodes(self):
        if self is not None:
            if self.IsLeaf() == True:
                return 0
            else:
                count = len(self.children)
                for node in self.children:
                    count += node.Count_Nodes()
                return count
        else:
            return -1

    def Set_Father(self, node):
        if self is not None:
            self.father = node
            self.Update_Depth()
            return True
        else:
            raise Exception("Node: Add_Child(..): null reference")

    def Update_Depth(self):
        self.depth = self.father.GetDepth() + 1
        if self.IsLeaf() is False:
            for node in self.children:
                node.Update_Depth()

class MinMaxNode(Node):

    def __init__(self, v = 0, type = True, info = None, father = None):
        Node.__init__(self, v, father)
        self.type = type
        self.info = info

    def GetValue(self, a, b):
        if self.IsLeaf() == True:
            return self.value
        elif self.type == True:
            return self.GetMax(a, b)
        else:
            return self.GetMin(a, b)

    def GetMax(self, a, b):
        v = -999999
        for node in self.children:
            v = max(v, node.GetValue(a, b))
            if v >= b:
                self.value = v
                return v
            a = max(a, v)
        self.value = v
        return v

    def GetMin(self, a, b):
        v = 999999
        for node in self.children:
            v = min(v, node.GetValue(a, b))
            if v <= a:
                self.value = v
                return v
            b = min(b, v)
        self.value = v
        return v

class AI:

    def __str__(self):
        raise Exception("AI::__str__() : Virtual method is called.")

    def Clear(self):
        raise Exception("AI::Clear() : Virtual method is called.")

    def Play(self, board, camp):
        raise Exception("AI::Play(..) : Virtual method is called.")

class RandomMoveAI(AI):

    def __str__(self):
        return "RandomMove"

    def Clear(self):
        pass

    def Play(self, board, camp):
        move = []
        pieces = [piece for piece in board.Pieces.values()]
        random.shuffle(pieces)
        for piece in pieces:
            if piece.BlackOrWhite == camp:
                succ = piece.Get_Move_Locs(board)
                if len(succ) != 0:
                    move.append((piece.x, piece.y))
                    move.append(random.choice(succ))
                    break
        return move

class MinMaxSearchAI(AI):

    Infinity = 999999

    def __init__(self, limit, use_material = True, use_position = True):
        self.Root = MinMaxNode()
        self.DepthLimit = limit
        self.Camp = True
        self.Use_Material_Balance = use_material
        self.Use_Position_Evaluation = use_position
        self.Thread_Result = Queue.Queue()

    def __str__(self):
        msg = "MinMaxSearch"
        msg += " - " + "Max Search Depth: " + str(self.DepthLimit)
        msg += " - " + "Use Position Evaluation: " + str(self.Use_Position_Evaluation)
        return msg

    def Clear(self):
        self.Root.Del_Children()

    def Play_Thread(self, board, camp):
        eva = self.Expand(self.Root, board, camp, 0, -self.Infinity, self.Infinity)
        self.Thread_Result.put(eva)

    def Play(self, board, camp):
        self.Camp = camp
        self.Root.type = True
        self.Root.Del_Children()
        choice = ((-1, -1), (-1, -1))
        choices = []

        thr = threading.Thread(target=self.Play_Thread, name='thread_ai', args=(board, camp))
        thr.setDaemon(True)
        thr.start()
        thr.join()

        eva = self.Thread_Result.get()
        count = self.Root.Count_Nodes()
        Msg = "Nodes: " + str(count) + " Eva: " + str(eva)

        for child in self.Root.children:
            if child.value == eva:
                choices.append(child.info)
        random.shuffle(choices)
        if len(choices) != 0:
            choice = choices[0]

        return choice, Msg

    def Expand(self, node, board, camp, depth, a, b):
        if depth >= self.DepthLimit:
            return node.value
        elif node.type: # MAX
            return self.Expand_Max(node, board, camp, depth, a, b)
        else:
            return self.Expand_Min(node, board, camp, depth, a, b)

    def Expand_Max(self, node, board, camp, depth, a, b):
        v = -self.Infinity
        position_move = []
        for position in board.Pieces.keys():
            if board.Pieces[position].BlackOrWhite == camp:
                moves = board.Pieces[position].Get_Move_Locs(board)
                for move in moves:
                    position_move.append((position, move))
        random.shuffle(position_move)
        for move in position_move:
            board_future = board.__deepcopy__()
            board_future.Select_For_AI(move[0], move[1])
            eva = 0
            if depth + 1 >= self.DepthLimit:
                if self.Use_Material_Balance:
                    eva += board_future.Evaluation_Material(self.Camp)
                if self.Use_Position_Evaluation:
                    eva += board_future.Evaluation_Position(self.Camp)
            newNode = MinMaxNode(eva, not node.type, move, node)
            v = max(v, self.Expand(newNode, board_future, not camp, depth + 1, a, b))

            # Value must be higher than upper bound or some critical cases will be pruned
            if v > b:
                node.value = v
                node.Add_Child(newNode)
                return v
            a = max(a, v)
            # ----------
            node.Add_Child(newNode)
        if node.IsLeaf():
            if not board.KingUnderAttack(camp):
                v = 0
        node.value = v
        return v

    def Expand_Min(self, node, board, camp, depth, a, b):
        v = self.Infinity
        position_move = []
        for position in board.Pieces.keys():
            if board.Pieces[position].BlackOrWhite == camp:
                moves = board.Pieces[position].Get_Move_Locs(board)
                for move in moves:
                    position_move.append((position, move))
        random.shuffle(position_move)
        for move in position_move:
            board_future = board.__deepcopy__()
            board_future.Select_For_AI(move[0], move[1])
            eva = 0
            if depth + 1 >= self.DepthLimit:
                if self.Use_Material_Balance:
                    eva += board_future.Evaluation_Material(self.Camp)
                if self.Use_Position_Evaluation:
                    eva += board_future.Evaluation_Position(self.Camp)
            newNode = MinMaxNode(eva, not node.type, move, node)
            v = min(v, self.Expand(newNode, board_future, not camp, depth + 1, a, b))

            # Value must be higher than upper bound or some critical cases will be pruned
            if v < a:
                node.value = v
                node.Add_Child(newNode)
                return v
            b = min(b, v)
            # ----------
            node.Add_Child(newNode)
        if node.IsLeaf():
            if not board.KingUnderAttack(camp):
                v = 0
        node.value = v
        return v
