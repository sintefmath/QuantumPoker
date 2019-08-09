# Copyright SINTEF 2019
# Authors: Franz G. Fuchs <franzgeorgfuchs@gmail.com>,
#          Christian Johnsen <christian.johnsen97@gmail.com>,
#          Vemund Falch <vemfal@gmail.com>

from numpy import empty


class InteractiveButtons:
    def __init__(self, board, interactiveContainer, checkPlayerBet, foldPlayer, playerGates, initialGates,
                 getPlayer):
        self.board = board
        self.interactiveContainer = interactiveContainer
        self.coords = empty(3)
        self.button = None
        self.nQBits = None
        self.coords = empty(3, dtype=int)
        self.nFilledQBits = 0
        self.buttonIsGate = False
        self.currentlyShowingPlayer = False
        self.playerGates = playerGates
        self.initialGates = initialGates
        self.qubitsShowing=0

        self.getPlayer = getPlayer

        self.basis = 0
        self.basisText = ["1,0", "+,-"]

        self.checkPlayerBet = checkPlayerBet
        self.foldPlayer = foldPlayer

    def getCurrentlyShowingPlayer(self):
        return self.currentlyShowingPlayer

    def changePlayer(self, newBoard):
        self.board = newBoard
        self.interactiveContainer.updateProbs(self.board.getProbs01()[0:self.qubitsShowing],
                                              self.board.getProbsPlusMinus()[0:self.qubitsShowing], self.basis,
                                              self.sortBellPairs(self.board.getBellPairs()))

    def updateQubitsShowing(self, additionalQubits):
        self.qubitsShowing += additionalQubits

        self.interactiveContainer.updateProbs(self.board.getProbs01()[0:self.qubitsShowing],
                                              self.board.getProbsPlusMinus()[0:self.qubitsShowing], self.basis,
                                              self.sortBellPairs(self.board.getBellPairs()))

    def changeCurrentButton(self, newButton, updateColor=True):
        if self.button is not None:
            self.interactiveContainer.setGateColor(self.button, self.interactiveContainer.getNormalColors()[0])
        if newButton is not None:
            self.interactiveContainer.setGateColor(newButton, self.interactiveContainer.getNormalColors()[1])
        if updateColor:
            self.interactiveContainer.updateBoard()
        if newButton is None:
            self.buttonIsGate = False
        self.nFilledQBits = 0
        self.button = newButton

    def H(self, event):
        self.changeCurrentButton('H')
        self.nQBits = 1
        self.buttonIsGate = True

    def X(self, event):
        self.changeCurrentButton('X')
        self.nQBits = 1
        self.buttonIsGate = True

    def Z(self, event):
        self.changeCurrentButton('Z')
        self.nQBits = 1
        self.buttonIsGate = True

    def ID(self, event):
        self.changeCurrentButton('ID')
        self.nQBits = 1
        self.buttonIsGate = True

    def CX(self, event):
        self.changeCurrentButton('CX')
        self.nQBits = 2
        self.buttonIsGate = True

    def CH(self, event):
        self.changeCurrentButton('CH')
        self.nQBits = 2
        self.buttonIsGate = True

    def SWAP(self, event):
        self.changeCurrentButton('SWAP')
        self.nQBits = 2
        self.buttonIsGate = True

    def CCX(self, event):
        self.changeCurrentButton('CCX')
        self.nQBits = 3
        self.buttonIsGate = True

    def ZH(self, event):
        self.changeCurrentButton('ZH')
        self.nQBits = 1
        self.buttonIsGate = True

    def SRX(self, event):
        self.changeCurrentButton('SRX')
        self.nQBits = 1
        self.buttonIsGate = True

    def SRZ(self, event):
        self.changeCurrentButton('SRZ')
        self.nQBits = 1
        self.buttonIsGate = True

    def changeBasis(self, event):
        self.basis = (self.basis+1)%2
        if self.basis == 0:
            self.interactiveContainer.setGateColor('Basis', self.interactiveContainer.getNormalColors()[0])
        else:
            self.interactiveContainer.setGateColor('Basis', self.interactiveContainer.getNormalColors()[1])
        self.interactiveContainer.updateProbs(self.board.getProbs01()[0:self.qubitsShowing],
                                              self.board.getProbsPlusMinus()[0:self.qubitsShowing], self.basis,
                                              self.sortBellPairs(self.board.getBellPairs()))
        self.interactiveContainer.setGateText('Basis', self.basisText[self.basis])
        self.interactiveContainer.updateBoard()

    def checkBellStates2(self, event):
        self.changeCurrentButton('Bell2')
        self.nQBits = 2
        self.nFilledQBits = 0
        self.buttonIsGate = False

    def checkBellStates3(self, event):
        self.changeCurrentButton('Bell3')
        self.nQBits = 3
        self.nFilledQBits = 0
        self.buttonIsGate=False

    def showHand(self, event, updateBoard=True):
        if self.currentlyShowingPlayer:
            self.interactiveContainer.setShowHandButtonColor(self.interactiveContainer.getNormalColors()[0],)
            self.interactiveContainer.updatePlayerGate({})
            self.currentlyShowingPlayer = False
        else:
            self.interactiveContainer.setShowHandButtonColor(self.interactiveContainer.getNormalColors()[1])
            self.interactiveContainer.updatePlayerGate(self.playerGates[self.getPlayer()], showZero=True)
            self.currentlyShowingPlayer = True
        if updateBoard:
            self.interactiveContainer.updateBoard()

    def foldButton(self, event):
        self.foldPlayer()

    def checkButton(self, event):
        self.checkPlayerBet()

    def mouseClick(self, qubit):
        """
        Called when the user has clicked a qubit on the board.
        :param qubit: number of qubit in row
        :return: buttonPress(Bool): Whether button press has gone through
                 isGate(Bool) Whether button is gate
                 button(Str): The button
        """
        if self.button is None:
            return False, ""
        isGate, button = False, ""
        if qubit not in self.coords[0:self.nFilledQBits] and self.nFilledQBits < self.nQBits and qubit<self.qubitsShowing:
            self.coords[self.nFilledQBits] = qubit
            self.nFilledQBits += 1
        if self.nFilledQBits == self.nQBits:
            if self.buttonIsGate:
                self.board.playerMoveInteractive(self.button, self.coords)
                self.interactiveContainer.updateProbs(self.board.getProbs01(), self.board.getProbsPlusMinus(),
                                                      self.basis, self.board.findBellPairs())
                self.interactiveContainer.unshowBellProbs()
                isGate = True
            if self.button == "Bell2":
                bellProbs = self.board.getBellStateProbs(self.coords[0:2], self.board.getPsi())
                self.interactiveContainer.updateBellProbs2(bellProbs)
            if self.button == "Bell3":
                bellProbs = self.board.getBellStateProbs3(self.coords, self.board.getPsi())
                self.interactiveContainer.updateBellProbs3(bellProbs)
            button = self.button
            self.changeCurrentButton(None, updateColor=False)
            self.interactiveContainer.updateBoard()
        return isGate, button

    def sortBellPairs(self, bellPairs):
        showingBellPairs = []
        for i in range(len(bellPairs)):
            if bellPairs[i][0] < self.qubitsShowing and bellPairs[i][1] < self.qubitsShowing:
                showingBellPairs.append(bellPairs[i])
        return showingBellPairs
