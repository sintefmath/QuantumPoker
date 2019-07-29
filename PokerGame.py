# Copyright SINTEF 2019
# Authors: Franz G. Fuchs <franzgeorgfuchs@gmail.com>,
#          Christian Johnsen <christian.johnsen97@gmail.com>,
#          Vemund Falch <vemfal@gmail.com>

from os.path import dirname, abspath
import sys
sys.path.append(dirname(abspath(__file__)))
from interactive import InteractiveContainer
from Board import Board
from Buttons import InteractiveButtons
from helpFiles import distributeGates
from numpy import amax, array, sum, empty, append, argwhere, copy, any, in1d, argsort, zeros
from qiskit import execute, Aer
from time import time


class PokerGame:
    def __init__(self, deckOfGates, nPlayers, money, names = None, smallBlind=5, smallBlindPlayer=0,
                 enableEntanglement=False, seed=None):
        if seed == None:
            seed = int(time())
        self.boards = [Board(boardSeed=seed, enableEntanglement=enableEntanglement) for i in range(nPlayers)]

        self.playerGates = distributeGates(deckOfGates, nPlayers)
        self.interactive = InteractiveContainer(nPlayers, self.boards[0].getSize(), deckOfGates,
                                                [str(i) for i in range(nPlayers)] if (names is None) else names)
        self.interactiveButtons = InteractiveButtons(self.boards[0], self.interactive, self.check, self.fold,
                                                     self.playerGates, deckOfGates, self.getPlayer)

        self.names = names
        self.nPlayers = nPlayers
        self.smallBlind = smallBlind
        self.allIn = empty(0, dtype=int)
        self.haveRaised = False

        self.playerMoney = money  # Number at index i is player i's money
        self.playerBets = array([0 for i in range(nPlayers)], dtype=int)  # Number at index i is player i's bet
        self.foldedPlayers = []

        self.smallBlindPlayer = smallBlindPlayer
        self.lastPlayerInRound = (smallBlindPlayer+2)%self.nPlayers
        self.player = (smallBlindPlayer+2)%self.nPlayers
        self.bettingRound = 0
        self.lastRaiser = (smallBlindPlayer+1)%self.nPlayers
        self.currentBet = self.smallBlind*2
        self.gameOver = False

        self.interactive.connectBets(self.interactiveButtons, self.convertRaiseToInt)
        self.interactive.connectMouseclick(self.mouseClick)
        self.interactive.connectShowHandButton(self.interactiveButtons)

        self.doBlindBets()

    def doBlindBets(self):
        self.playerBets[self.smallBlindPlayer] += self.smallBlind
        self.playerBets[(self.smallBlindPlayer+1) % self.nPlayers] += self.smallBlind*2
        self.playerMoney[self.smallBlindPlayer] -= self.smallBlind
        self.playerMoney[(self.smallBlindPlayer + 1) % self.nPlayers] -= self.smallBlind * 2
        self.interactive.updateNextBet(self.playerBets[self.player], amax(self.playerBets))
        self.interactive.updateCurrentBets(self.playerBets, self.playerMoney)
        self.interactive.setPlayerPatchColor(self.player, self.interactive.getCurrentPlayerColor()[0])

    def advanceGame(self):
        """
        Moves the game to the next player and round.
        :return: None
        """

        if len(self.foldedPlayers) >= self.nPlayers - 1:
            self.interactive.disconnectShowHandButton()
            self.interactive.disconnectBets()
            self.interactive.setPlayerPatchColor(self.player, self.interactive.getFoldedColor())
            self.endGame(allFolded=True)
            return

        if len(self.foldedPlayers) + self.allIn.shape[0] == self.nPlayers and self.bettingRound < 4:
            advanceRound = True

        else:
            advanceRound = False
            firstIter = True
            nextPlayer = self.player

            while firstIter or nextPlayer in self.foldedPlayers or (nextPlayer in self.allIn and self.bettingRound < 4):
                firstIter = False
                nextPlayer = (nextPlayer + 1) % self.nPlayers
                if nextPlayer == self.lastPlayerInRound:
                    advanceRound = True

        if len(self.foldedPlayers) + self.allIn.shape[0] >= self.nPlayers - 1 and self.bettingRound < 4 and advanceRound:
            self.forwardToRound4()
            nextPlayer = self.lastRaiser

        elif advanceRound:
            if self.bettingRound == 0:
                self.showCards(3)
                self.interactive.connectBellAndBasis(self.interactiveButtons)
                nextPlayer = self.findRoundStarter()
                self.lastPlayerInRound = nextPlayer
                if self.haveRaised:
                    self.interactive.setBetandCheck()
                    self.haveRaised = False
            elif self.bettingRound == 1:
                self.showCards(1)
                nextPlayer = self.findRoundStarter()
                self.lastPlayerInRound = nextPlayer
                if self.haveRaised:
                    self.interactive.setBetandCheck()
                    self.haveRaised = False
            elif self.bettingRound == 2:
                self.showCards(1)
                nextPlayer = self.findRoundStarter()
                self.lastPlayerInRound = nextPlayer
                if self.haveRaised:
                    self.interactive.setBetandCheck()
                    self.haveRaised = False
            elif self.bettingRound == 3:
                self.interactive.disconnectBets()
                self.interactive.disconnectShowHandButton()
                self.interactive.connectEnd(self.endGateTurn)
                nextPlayer = self.lastRaiser
                self.lastPlayerInRound = nextPlayer

            elif self.bettingRound == 4:  # "Round" in which gates were used
                self.endGame()
                self.interactive.setPlayerPatchColor(self.player, self.interactive.getDisconnectedColor())
                self.interactive.disconnectAllGates()
                self.interactive.disconnectEnd()
                return
            self.bettingRound += 1

        if self.bettingRound == 4:
            self.interactive.connectAllowedGates(self.interactiveButtons, self.playerGates[nextPlayer])
            self.interactiveButtons.changePlayer(self.boards[nextPlayer])

        if self.bettingRound == 4:
            self.inform("Apply the desired quantum gates\nthen click the end button.")
        elif self.bettingRound < 3:
            self.interactive.updateNextBet(self.playerBets[nextPlayer], amax(self.playerBets))
            self.inform("Place a bet or fold.")

        self.updateColor(nextPlayer, self.bettingRound<4)

        self.interactive.updateBoard()

        self.player = nextPlayer

    def findRoundStarter(self):
        nextPlayer = self.smallBlindPlayer
        while nextPlayer in self.allIn or nextPlayer in self.foldedPlayers:
            nextPlayer = (nextPlayer+1)%self.nPlayers
        return nextPlayer

    def updateColor(self, nextPlayer, active):
        if nextPlayer == self.player:
            return
        if self.player in self.allIn:
            self.interactive.setPlayerPatchColor(self.player, self.interactive.getAllInColor()[0])
        elif self.player in self.foldedPlayers:
            self.interactive.setPlayerPatchColor(self.player, self.interactive.foldedColor)
        else:
            self.interactive.setPlayerPatchColor(self.player, self.interactive.disconnectedColor)
        self.interactive.setPlayerPatchColor(nextPlayer, self.interactive.getCurrentPlayerColor()[0])

    def forwardToRound4(self):
        while self.bettingRound < 4:
            if self.bettingRound == 0:
                self.showCards(3)
                self.interactive.connectBellAndBasis(self.interactiveButtons)
            elif self.bettingRound == 1:
                self.showCards(1)
            elif self.bettingRound == 2:
                self.showCards(1)
            self.bettingRound += 1
        self.interactive.disconnectBets()
        self.interactive.disconnectShowHandButton()
        self.interactive.connectEnd(self.endGateTurn)

    def endGateTurn(self, event):
        """
        Called by the "end" button when a user has finished using their gates.
        :return: None
        """
        if self.gameOver:
            return

        self.interactive.disconnectAllGates()
        self.advanceGame()

    def endGame(self, allFolded=False):
        """
        Called when the game is supposed to end.
        :return: None
        """
        if allFolded:
            if len(self.foldedPlayers) == self.nPlayers:
                self.inform("Somehow you all folded! No winner.")
                self.inform("Exit to start a new game.")
                self.gameOver = True
                return

            for player in range(self.nPlayers):
                if player not in self.foldedPlayers:
                    self.inform(self.names[player] + " won " + str(sum(self.playerBets)) +
                                " because everyone else folded.")
                    self.inform("Game over. Exit to start a new game.")
                    self.gameOver = True
                    self.playerMoney[player] += sum(self.playerBets)

                    scoresDisplay = [-1 for i in range(self.nPlayers)]
                    winnings = [0 for i in range(self.nPlayers)]
                    winnings[player] = sum(self.playerBets)
                    scoresDisplay[player] = -2

                    self.interactive.displayEndResults(scoresDisplay, winnings)
                    return

        simulator = Aer.get_backend("qasm_simulator")
        scores = [0 for i in range(self.nPlayers)]
        for i in range(self.nPlayers):
            if i in self.foldedPlayers:
                scores[i] = -1
                continue

            board = self.boards[i]
            board.qc.measure(board.q, board.c)
            counts = execute(board.qc, simulator, shots=1).result().get_counts(board.qc)
            for bitStr in list(counts.keys())[0]:
                if bitStr == "1":
                    scores[i] += 1

        print("\n---- Final scores----")
        winners = []
        nWinners = 0
        maxScore = max(scores)

        for i in range(self.nPlayers):
            print("Player", i + 1, end=": ")
            if scores[i] == -1:
                print("Folded")
            else:
                print(scores[i])
                if scores[i] == maxScore:
                    winners.append(i)
                    nWinners += 1

        self.allIn = self.allIn[argsort(self.playerBets[self.allIn])]
        pot = zeros(self.allIn.shape[0]+1, dtype=int)

        for nPot in range(self.allIn.shape[0]):
            currentPotBet = self.playerBets[self.allIn[nPot]]
            for player in range(self.nPlayers):
                betToPot = min(self.playerBets[player], currentPotBet)
                pot[nPot] += betToPot
                self.playerBets[player] -= betToPot

        pot[-1] = sum(self.playerBets)
        winnings = [0 for i in range(self.nPlayers)]
        originalScore = copy(scores)

        if self.allIn.shape[0] == 0 or not(any(in1d(array(winners), self.allIn))):
            self.printWinners(winners, nWinners, scores, pot[0])
            for i in range(len(winners)):
                winnings[winners[i]] += pot[0]/nWinners

        else:
            for i in range(self.allIn.shape[0]):
                if pot[i] == 0 or self.allIn[i] not in winners:
                    pot[i+1] += pot[i]
                    continue
                self.printWinners(winners, nWinners, scores, pot[i])
                for j in range(len(winners)):
                    winnings[winners[j]] += pot[i]/nWinners

                scores[self.allIn[i]] = -1
                winners = argwhere(scores == amax(scores)).flatten()
                nWinners = winners.shape[0]
                if not(any(in1d(array(winners), self.allIn))):
                    pot[-1] = sum(pot[i+1:])
                    break
            if pot[-1] > 0:
                self.printWinners(winners, nWinners, scores, pot[-1])
                for j in range(len(winners)):
                    winnings[winners[j]] += pot[-1]/nWinners

        self.interactive.displayEndResults(originalScore, winnings)

        self.gameOver = True
        self.inform("Game over. Exit to start a new game.")

    def printWinners(self, winners, nWinners, scores, pot):
        if nWinners == 0:
            self.inform("No winners!")
        elif nWinners == 1:
            self.inform(self.names[winners[0]] + " won " + str(pot) + " with a score of " +
                        str(scores[winners[0]]) + ".")
            self.playerMoney[winners[0]] += pot
        else:
            text = ""
            pot /= nWinners
            for i in range(nWinners):
                self.playerMoney[winners[i]] += pot
                text += self.names[winners[i]]
                if i == nWinners - 2:
                    if nWinners != 2:
                        text += ","
                    text += " and "
                elif i < nWinners - 1:
                    text += ", "
            text += " each won " + str(round(pot, 2)) + " with a score of " + str(scores[winners[0]])
            self.inform(text)

    def fold(self):
        """
        Called by the "fold" button.
        :return: None
        """
        if self.bettingRound > 3 or self.gameOver:
            return

        self.interactive.updateCurrentBets(self.playerBets, self.playerMoney)
        self.foldedPlayers.append(self.player)
        if self.interactiveButtons.getCurrentlyShowingPlayer():
            self.interactiveButtons.showHand(None, updateBoard=False)
        self.advanceGame()

    def check(self):
        if self.bettingRound > 3 or self.gameOver:
            return
        """
        Called by the "check" button.
        :return: None
        """
        if (self.currentBet-self.playerBets[self.player] > self.playerMoney[self.player]):
            self.bet(self.playerMoney[self.player])
        else:
            self.bet(self.currentBet-self.playerBets[self.player])

    def convertRaiseToInt(self, amountStr, text_box):
        if text_box is not None:
            text_box.set_val("")
        try:
            amount = int(amountStr)
        except ValueError:
            self.inform("Enter a valid number.")
            return
        if amount < 0:
            self.inform("Enter a non-negative number.")
            return
        self.bet(amount + self.currentBet - self.playerBets[self.player])

    def bet(self, amount):
        """
        Called by the input text box when the user hits enter.
        :param amountStr: String that was in the text box, text_box: input box from text
        :return: None
        """

        if amount == self.playerMoney[self.player]:  # All In
            self.allIn = append(self.allIn, self.player)

        elif amount + self.playerBets[self.player] < self.currentBet:
            self.inform("To bet you must either raise or check. Enter a large enough number.")
            return

        elif amount > self.playerMoney[self.player]:
            self.inform("You cannot raise by more than " + str(self.playerMoney[self.player]+\
                                                               self.playerBets[self.player]-self.currentBet) + ".")
            return

        if self.interactiveButtons.getCurrentlyShowingPlayer():
            self.interactiveButtons.showHand(None, updateBoard=False)

        self.playerBets[self.player] += amount
        self.playerMoney[self.player] -= amount

        if self.playerBets[self.player] > self.currentBet:
            self.currentBet = self.playerBets[self.player]
            self.lastRaiser = self.player
            self.lastPlayerInRound = self.player
            if not (self.haveRaised):
                self.interactive.setRaiseandCall()
                self.haveRaised = True

        self.interactive.updateCurrentBets(self.playerBets, self.playerMoney)
        self.interactive.updateNextBet(self.playerBets[(self.player+1)%self.nPlayers], amax(self.playerBets))

        self.advanceGame()

    def showCards(self, nCards):
        """
        Makes nCards more qubits visible on the board.
        :param nCards: Number of additional cards to show.
        :return: None
        """
        self.interactiveButtons.updateQubitsShowing(nCards)

    def inform(self, text):
        self.interactive.updateInfoText(text)
        self.interactive.fig.canvas.draw()

    def mouseClick(self, qubit):
        """
        Logic for mouseclick
        :param qubit: the target qubit
        :return: Nothing
        """
        if self.gameOver:
            return

        isGate, button = self.interactiveButtons.mouseClick(qubit)
        if isGate:
            self.playerGates[self.player][button] -= 1
            if self.playerGates[self.player][button] == 0:
                del self.playerGates[self.player][button]
                self.interactive.disconnectGate(button)
            self.interactive.updatePlayerGate(self.playerGates[self.player], hover=True, showZero=True)
        self.interactive.updateBoard()

    def getPlayer(self):
        return self.player
