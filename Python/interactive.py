# Copyright SINTEF 2019
# Authors: Franz G. Fuchs <franzgeorgfuchs@gmail.com>,
#          Christian Johnsen <christian.johnsen97@gmail.com>,
#          Vemund Falch <vemfal@gmail.com>

from os.path import dirname, abspath
import sys
sys.path.append(dirname(abspath(__file__)))
import matplotlib.pyplot as plt
from Python.helpFiles import getUnentangledTag
from Python.CustomButton import Button
from Python.CustomTextBox import TextBox
from numpy import array, concatenate, flip


class InteractiveContainer:
    def __init__(self, nPlayers, dims, initialGates, names):
        self.nPlayers = nPlayers
        self.fig, self.ax, self.probsnum, self.probsStr = makeFigure(dims)
        self.bellProbsInt, self.bellProbsStr, self.bellProbs_ax = createBellWindow(self.fig)
        self.buttonsDict, self.gates, self.notGates, self.patchDict = createButtonsInfig(self.fig)
        self.text_box, self.betText, self.buttonsDict['checkButton'], self.buttonsDict['foldButton'], \
            self.showPlayerHandButton, self.infoText = createBets(self.fig, self.ax)

        self.infoTextLine0, self.infoTextLine1 = "Place a bet or fold.", "                 "

        self.playerButtons, self.playerBet, self.playerMoney\
            = createPlayerPatches(self.fig, self.ax, nPlayers, names)
        self.connects, self.playerConnects = {}, []

        self.normalColors = ["darkgrey", "dimgray", "lightgray"]
        self.currentPlayerColors = ['lime', 'green', 'springgreen']
        self.disconnectedColor = 'whitesmoke'
        self.foldedColor = 'darkred'
        self.allInColor = ['#ffff00', '#ebe60b', '#f9f960']
        #Inactive, Active, HoverColor
        self.setInitialColors()
        self.updatePlayerPatches(initialGates)

        self.currentAxes = None
        self.motionCID = self.fig.canvas.mpl_connect('motion_notify_event', self._motion)

    def setInitialColors(self):
        self.buttonsDict['End'].ax.set_facecolor(self.disconnectedColor)  # ax.set_facecolor updates color immediately
        self.buttonsDict['End'].color = self.disconnectedColor  # .color = ... updates color after next mouse movement
        self.buttonsDict['End'].hovercolor = self.disconnectedColor
        self.buttonsDict['Basis'].ax.set_facecolor(self.disconnectedColor)
        self.buttonsDict['Basis'].color = self.disconnectedColor
        self.buttonsDict['Basis'].hovercolor = self.disconnectedColor
        self.buttonsDict['Bell2'].ax.set_facecolor(self.disconnectedColor)
        self.buttonsDict['Bell2'].color = self.disconnectedColor
        self.buttonsDict['Bell2'].hovercolor = self.disconnectedColor
        self.buttonsDict['Bell3'].ax.set_facecolor(self.disconnectedColor)
        self.buttonsDict['Bell3'].color = self.disconnectedColor
        self.buttonsDict['Bell3'].hovercolor = self.disconnectedColor
        for player in range(self.nPlayers):
            self.playerButtons[player].set_facecolor(self.disconnectedColor)
        for gate in self.gates:
            self.buttonsDict[gate].ax.set_facecolor(self.disconnectedColor)
            self.buttonsDict[gate].color = self.disconnectedColor
            self.buttonsDict[gate].hovercolor=self.disconnectedColor

    def setGateColor(self, button, color):
        self.buttonsDict[button].ax.set_facecolor(color)
        self.buttonsDict[button].color = color

    def setGateHoverColor(self, button, color):
        self.buttonsDict[button].hovercolor = color

    def setShowHandButtonColor(self, color):
        self.showPlayerHandButton.ax.set_facecolor(color)
        self.showPlayerHandButton.color = color

    def setShowHandHoverColor(self, color):
        self.showPlayerHandButton.hovercolor = color

    def setPlayerPatchColor(self, player, color):
        self.playerButtons[player].set_facecolor(color)

    def setGateText(self, button, text):
        self.buttonsDict[button].label.set_text(text)

    def setBetandCheck(self):
        self.text_box.label.set_text("Place bet:")
        self.buttonsDict['checkButton'].label.set_text("Check")

    def setRaiseandCall(self):
        self.text_box.label.set_text("Raise:")
        self.buttonsDict['checkButton'].label.set_text("Call")

    def getDisconnectedColor(self):
        return self.disconnectedColor

    def getFoldedColor(self):
        return self.foldedColor

    def getCurrentPlayerColor(self):
        return self.currentPlayerColors

    def getNormalColors(self):
        return self.normalColors

    def getAllInColor(self):
        return self.allInColor

    def connectMouseclick(self, mouseClickFunc):
        self.cidMC = self.fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, mouseClickFunc,
                                                                                             self.ax))

    def connectEnd(self, endFunc):
        self.connects['End'] = self.buttonsDict['End'].on_clicked(endFunc)
        self.setGateColor('End', self.normalColors[0])
        self.setGateHoverColor('End', self.normalColors[2])

    def disconnectEnd(self):
        if self.buttonsDict['End'] is not None:
            self.buttonsDict['End'].disconnect(self.connects['End'])
            self.setGateColor('End', self.disconnectedColor)
            self.setGateHoverColor('End', self.disconnectedColor)

    def connectShowHandButton(self, interactiveButtons):
        self.connects['showHand'] = self.showPlayerHandButton.on_clicked(interactiveButtons.showHand)
        self.showPlayerHandButton.ax.set_facecolor(self.normalColors[0])
        self.showPlayerHandButton.color = self.normalColors[0]
        self.showPlayerHandButton.hovercolor = self.normalColors[2]

    def disconnectShowHandButton(self):
        self.showPlayerHandButton.disconnect(self.connects['showHand'])
        self.showPlayerHandButton.ax.set_facecolor(self.disconnectedColor)
        self.showPlayerHandButton.color = self.disconnectedColor
        self.showPlayerHandButton.hovercolor = self.disconnectedColor

    def connectBellAndBasis(self, interactiveButtons):
        self.buttonsDict['Basis'].on_clicked(interactiveButtons.changeBasis)
        self.setGateColor('Basis', self.normalColors[0])
        self.setGateHoverColor('Basis', self.normalColors[2])
        self.buttonsDict['Bell2'].on_clicked(interactiveButtons.checkBellStates2)
        self.setGateColor('Bell2', self.normalColors[0])
        self.setGateHoverColor('Bell2', self.normalColors[2])
        self.buttonsDict['Bell3'].on_clicked(interactiveButtons.checkBellStates3)
        self.setGateColor('Bell3', self.normalColors[0])
        self.setGateHoverColor('Bell3', self.normalColors[2])

    def connectAllowedGates(self, interactiveButtons, allowedButtons):
        allowedButtonsKeys = allowedButtons.keys()
        for i in range(len(self.gates)):
            if self.gates[i] == 'H' and 'H' in allowedButtonsKeys:
                self.connectGate('H', interactiveButtons.H)
            if self.gates[i] == 'X' and 'X' in allowedButtonsKeys:
                self.connectGate('X', interactiveButtons.X)
            if self.gates[i] == 'Z' and 'Z' in allowedButtonsKeys:
                self.connectGate('Z', interactiveButtons.Z)
            if self.gates[i] == 'SRX' and 'SRX' in allowedButtonsKeys:
                self.connectGate('SRX', interactiveButtons.SRX)
            if self.gates[i] == 'CX' and 'CX' in allowedButtonsKeys:
                self.connectGate('CX', interactiveButtons.CX)
            if self.gates[i] == 'CH' and 'CH' in allowedButtonsKeys:
                self.connectGate('CH', interactiveButtons.CH)
            if self.gates[i] == 'SWAP' and 'SWAP' in allowedButtonsKeys:
                self.connectGate('SWAP', interactiveButtons.SWAP)
            if self.gates[i] == 'CCX' and 'CCX' in allowedButtonsKeys:
                self.connectGate('CCX', interactiveButtons.CCX)
            if self.gates[i] == 'ZH' and 'ZH' in allowedButtonsKeys:
                self.connectGate('ZH', interactiveButtons.ZH)
            if self.gates[i] == 'SRZ' and 'SRZ' in allowedButtonsKeys:
                self.connectGate('SRZ', interactiveButtons.SRZ)
        self.updatePlayerGate(allowedButtons, hover = True, showZero=True)

    def disconnectAllGates(self):
        connectedGates = array(list(self.connects.keys()))
        for i in range(len(self.gates)):
            if self.gates[i] == 'H' and 'H' in connectedGates:
                self.disconnectGate('H')
            if self.gates[i] == 'X' and 'X' in connectedGates:
                self.disconnectGate('X')
            if self.gates[i] == 'Z' and 'Z' in connectedGates:
                self.disconnectGate('Z')
            if self.gates[i] == 'SRX' and 'SRX' in connectedGates:
                self.disconnectGate('SRX')
            if self.gates[i] == 'CX' and 'CX' in connectedGates:
                self.disconnectGate('CX')
            if self.gates[i] == 'CH' and 'CH' in connectedGates:
                self.disconnectGate('CH')
            if self.gates[i] == 'SWAP' and 'SWAP' in connectedGates:
                self.disconnectGate('SWAP')
            if self.gates[i] == 'CCX' and 'CCX' in connectedGates:
                self.disconnectGate('CCX')
            if self.gates[i] == 'ZH' and 'ZH' in connectedGates:
                self.disconnectGate('ZH')
            if self.gates[i] == 'SRZ' and 'SRZ' in connectedGates:
                self.disconnectGate('SRZ')

    def connectGate(self, gate, func):
        self.connects[gate] = self.buttonsDict[gate].on_clicked(func)

    def disconnectGate(self, gate):
        self.buttonsDict[gate].disconnect(self.connects[gate])

    def connectBets(self, interactiveButtons, betFunc):
        pass
        self.connects['checkButton'] = self.buttonsDict['checkButton'].on_clicked(interactiveButtons.checkButton)
        self.buttonsDict['checkButton'].ax.set_facecolor(self.normalColors[0])
        self.buttonsDict['checkButton'].color = self.normalColors[0]
        self.buttonsDict['checkButton'].hovercolor = self.normalColors[2]
        self.connects['foldButton'] = self.buttonsDict['foldButton'].on_clicked(interactiveButtons.foldButton)
        self.buttonsDict['foldButton'].ax.set_facecolor(self.normalColors[0])
        self.buttonsDict['foldButton'].color = self.normalColors[0]
        self.buttonsDict['foldButton'].hovercolor = self.normalColors[2]
        self.connects['Bet'] = self.text_box.on_submit(lambda text: betFunc(text, self.text_box))
        self.text_box.ax.set_facecolor(self.normalColors[0])
        self.text_box.color = self.normalColors[0]
        self.text_box.hovercolor = self.normalColors[2]

    def disconnectBets(self):
        self.buttonsDict['checkButton'].ax.set_facecolor(self.disconnectedColor)
        self.buttonsDict['checkButton'].color = self.disconnectedColor
        self.buttonsDict['checkButton'].hovercolor = self.disconnectedColor
        self.buttonsDict['foldButton'].ax.set_facecolor(self.disconnectedColor)
        self.buttonsDict['foldButton'].color = self.disconnectedColor
        self.buttonsDict['foldButton'].hovercolor = self.disconnectedColor
        self.text_box.ax.set_facecolor(self.disconnectedColor)
        self.text_box.color = self.disconnectedColor
        self.text_box.hovercolor = self.disconnectedColor
        self.betText.set_text("")
        self.buttonsDict['foldButton'].disconnect(self.connects['foldButton'])
        del self.connects['foldButton']
        self.text_box.disconnect(self.connects['Bet'])
        del self.connects['Bet']
        self.buttonsDict['checkButton'].disconnect(self.connects['checkButton'])
        del self.connects['checkButton']

    def updatePlayerGate(self, gates, hover=False, showZero=False):
        for gate in self.gates:
            if showZero:
                end = "0"
            else:
                end = "  "
            self.buttonsDict[gate].label.set_text("{}: ".format(gate) + str(gates[gate] if gate in gates else end))
            self.setGateColor(gate, (self.normalColors[0] if gate in gates else self.disconnectedColor))
            if hover:
                self.buttonsDict[gate].hovercolor = (self.normalColors[2] if gate in gates else self.disconnectedColor)
            else:
                self.buttonsDict[gate].hovercolor = (self.normalColors[0] if gate in gates else self.disconnectedColor)

    def updatePlayerPatches(self, gates):
        for gate in self.gates:
            self.patchDict[gate+"_text"].set_text("{}: ".format(gate) + str(gates[gate] if gate in gates else 0))
            self.patchDict[gate+"_patch"].set_facecolor(self.normalColors[0] if gate in gates else self.disconnectedColor)

    def updateCurrentBets(self, bets, money):
        for i in range(len(self.playerBet[:-1])):
            if bets[i] == -2:  # The first 2 cases only occur when showing scores and winnings
                self.playerBet[i].set_text("")
            elif bets[i] == -1:
                self.playerBet[i].set_text("Folded")
            else:
                self.playerBet[i].set_text(bets[i])
            self.playerMoney[i].set_text(round(money[i],2))

    def displayEndResults(self, scores, winnings):
        self.playerBet[-1].set_text("Score:")
        self.playerMoney[-1].set_text("Winnings:")
        self.updateCurrentBets(scores, winnings)

    def updateNextBet(self, playerCurrentBet, maxBet, show=True):
        if show:
            self.betText.set_text("{}/{}".format(playerCurrentBet, maxBet))
        else:
            self.betText.set_text("")

    def updateInfoText(self, newText):
        if not(newText == self.infoTextLine0):
            self.infoTextLine1 = self.infoTextLine0
            self.infoTextLine0 = newText
            self.infoText.set_text("  " + self.infoTextLine1 + "\n> " + self.infoTextLine0)

    def updateProbs(self, probs01, probsPlusMinus, basis, bellPairs):
        if basis == 0:
            probs = probs01
            prefix01, suffix01 = r"$\mathbf{", "}$"
            prefixPM, suffixPM = "$", "$"
        elif basis == 1:
            probs = probsPlusMinus
            prefix01, suffix01 = "$", "$"
            prefixPM, suffixPM = r"$\mathbf{", "}$"
        if probs.shape[0] < 5:
            self.probsnum.set_data([concatenate((probs, array([0.5 for i in range(5-probs.shape[0])])))])
        else:
            self.probsnum.set_data([probs])
        for i in range(probs.shape[0]):
            if abs(probs01[i]) < 1E-4:
                probsStr = r"$|0\rangle$"
            elif abs(probs01[i] - 1) < 1E-4:
                probsStr = r"$|1\rangle$"
            elif abs(probsPlusMinus[i]) < 1E-4:
                probsStr = r"$|+\rangle$"
            elif abs(probsPlusMinus[i] - 1) < 1E-4:
                probsStr = r"$|-\rangle$"
            else:
                extraInfoStr0 = getUnentangledTag(i, bellPairs)
                probsStr = extraInfoStr0 + prefix01 + r"P(1) = " + format(probs01[i], ".3f") + suffix01
                probsStr += "\n" + prefixPM + r"P(-) = " + format(probsPlusMinus[i], ".3f") + suffixPM

            self.probsStr[i].set_text(probsStr)

    def updateBellProbs2(self, bellProbs):
        self.bellProbsInt.set_data(concatenate((array([0.5 for i in range(4)]).reshape((2, 2)),
                                                flip(bellProbs.reshape((2, 2)), axis=0)), axis=0))

        for i in range(4):
            self.bellProbsStr[i].set_text(str(format(bellProbs[i], ".2f")))
            self.bellProbsStr[4 + i].set_text("")
        self.bellProbs_ax.set_yticklabels(["", "", r"$|01\rangle \pm |10\rangle$", r"$|00\rangle \pm |11\rangle$"],
                                          fontsize=12)
        self.bellProbs_ax.set_xticklabels(["+", "-"], fontsize=12)

    def updateBellProbs3(self, bellProbs):
        self.bellProbsInt.set_data(flip(bellProbs.reshape((4, 2)), axis=0))
        for i in range(8):
            self.bellProbsStr[i].set_text(str(format(bellProbs[i], ".2f")))
        self.bellProbs_ax.set_yticklabels([r"$|100\rangle \pm |011\rangle$", r"$|010\rangle \pm |101\rangle$",
                                           r"$|001\rangle \pm |110\rangle$", r"$|000\rangle \pm |111\rangle$"],
                                          fontsize=12)
        self.bellProbs_ax.set_xticklabels(["+", "-"], fontsize=12)

    def unshowBellProbs(self):
        self.bellProbsInt.set_data(array(array([0.50 for i in range(8)]).reshape((4, 2))))  # Update Bell States
        self.bellProbs_ax.set_yticklabels(["", "", "", ""], fontsize=12)
        self.bellProbs_ax.set_xticklabels(["", ""], fontsize=12)

        for i in range(8):
            self.bellProbsStr[i].set_text("")

    def updateBoard(self):
        self.fig.canvas.draw()

    def _motion(self, event):
        if self.currentAxes == event.inaxes:
            return

        if self.currentAxes is not None:
            if self.currentAxes == self.buttonsDict['H'].ax:
                if not self.buttonsDict['H'].ignore(event):
                    self.currentAxes.set_facecolor(self.buttonsDict['H'].color)
            elif self.currentAxes == self.buttonsDict['X'].ax:
                if not self.buttonsDict['X'].ignore(event):
                    self.currentAxes.set_facecolor(self.buttonsDict['X'].color)
            elif self.currentAxes == self.buttonsDict['CX'].ax:
                if not self.buttonsDict['CX'].ignore(event):
                    self.currentAxes.set_facecolor(self.buttonsDict['CX'].color)
            elif self.currentAxes == self.buttonsDict['ZH'].ax:
                if not self.buttonsDict['ZH'].ignore(event):
                    self.currentAxes.set_facecolor(self.buttonsDict['ZH'].color)
            elif self.currentAxes == self.buttonsDict['CH'].ax:
                if not self.buttonsDict['CH'].ignore(event):
                    self.currentAxes.set_facecolor(self.buttonsDict['CH'].color)

            elif self.currentAxes == self.buttonsDict['End'].ax:
                if not self.buttonsDict['End'].ignore(event):
                    self.currentAxes.set_facecolor(self.buttonsDict['End'].color)
            elif self.currentAxes == self.buttonsDict['Basis'].ax:
                if not self.buttonsDict['Basis'].ignore(event):
                    self.currentAxes.set_facecolor(self.buttonsDict['Basis'].color)
            elif self.currentAxes == self.buttonsDict['Bell2'].ax:
                if not self.buttonsDict['Bell2'].ignore(event):
                    self.currentAxes.set_facecolor(self.buttonsDict['Bell2'].color)
            elif self.currentAxes == self.buttonsDict['Bell3'].ax:
                if not self.buttonsDict['Bell3'].ignore(event):
                    self.currentAxes.set_facecolor(self.buttonsDict['Bell3'].color)

            elif self.currentAxes == self.buttonsDict['checkButton'].ax:
                if not self.buttonsDict['checkButton'].ignore(event):
                    self.currentAxes.set_facecolor(self.buttonsDict['checkButton'].color)
            elif self.currentAxes == self.buttonsDict['foldButton'].ax:
                if not self.buttonsDict['foldButton'].ignore(event):
                    self.currentAxes.set_facecolor(self.buttonsDict['foldButton'].color)

            elif self.currentAxes == self.showPlayerHandButton.ax:
                if not self.showPlayerHandButton.ignore(event):
                    self.currentAxes.set_facecolor(self.showPlayerHandButton.color)

            elif self.currentAxes == self.text_box.ax:
                if not self.text_box.ignore(event):
                    self.currentAxes.set_facecolor(self.text_box.color)

        if event.inaxes is not None:
            if event.inaxes == self.buttonsDict['H'].ax:
                if not self.buttonsDict['H'].ignore(event):
                    event.inaxes.set_facecolor(self.buttonsDict['H'].hovercolor)
            elif event.inaxes == self.buttonsDict['X'].ax:
                if not self.buttonsDict['X'].ignore(event):
                    event.inaxes.set_facecolor(self.buttonsDict['X'].hovercolor)
            elif event.inaxes == self.buttonsDict['CX'].ax:
                if not self.buttonsDict['CX'].ignore(event):
                    event.inaxes.set_facecolor(self.buttonsDict['CX'].hovercolor)
            elif event.inaxes == self.buttonsDict['ZH'].ax:
                if not self.buttonsDict['ZH'].ignore(event):
                    event.inaxes.set_facecolor(self.buttonsDict['ZH'].hovercolor)
            elif event.inaxes == self.buttonsDict['CH'].ax:
                if not self.buttonsDict['CH'].ignore(event):
                    event.inaxes.set_facecolor(self.buttonsDict['CH'].hovercolor)

            elif event.inaxes == self.buttonsDict['End'].ax:
                if not self.buttonsDict['End'].ignore(event):
                    event.inaxes.set_facecolor(self.buttonsDict['End'].hovercolor)
            elif event.inaxes == self.buttonsDict['Basis'].ax:
                if not self.buttonsDict['Basis'].ignore(event):
                    event.inaxes.set_facecolor(self.buttonsDict['Basis'].hovercolor)
            elif event.inaxes == self.buttonsDict['Bell2'].ax:
                if not self.buttonsDict['Bell2'].ignore(event):
                    event.inaxes.set_facecolor(self.buttonsDict['Bell2'].hovercolor)
            elif event.inaxes == self.buttonsDict['Bell3'].ax:
                if not self.buttonsDict['Bell3'].ignore(event):
                    event.inaxes.set_facecolor(self.buttonsDict['Bell3'].hovercolor)

            elif event.inaxes == self.buttonsDict['checkButton'].ax:
                if not self.buttonsDict['checkButton'].ignore(event):
                    event.inaxes.set_facecolor(self.buttonsDict['checkButton'].hovercolor)
            elif event.inaxes == self.buttonsDict['foldButton'].ax:
                if not self.buttonsDict['foldButton'].ignore(event):
                    event.inaxes.set_facecolor(self.buttonsDict['foldButton'].hovercolor)

            elif event.inaxes == self.showPlayerHandButton.ax:
                if not self.showPlayerHandButton.ignore(event):
                    event.inaxes.set_facecolor(self.showPlayerHandButton.hovercolor)

            elif event.inaxes == self.text_box.ax:
                if not self.text_box.ignore(event):
                    event.inaxes.set_facecolor(self.text_box.hovercolor)
        self.currentAxes = event.inaxes
        self.fig.canvas.draw()


def makeFigure(size):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.tick_params(axis='both', which='both', bottom=False, left=False, labelleft = False, labelsize=12)
    ax.set_xticks(array([i for i in range(size)]))
    ax.set_xticklabels(array([str(i+1) for i in range(size)]))
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    ax.set_aspect('equal')
    plt.subplots_adjust(right=0.77)

    for i in range(size + 1):
        ax.axvline(i - 0.5, c='k')
    ax.axhline(0.5, c="k")
    ax.axhline(-0.5, c="k")
    probs = array([0.5 for i in range(size)])
    probsNum = ax.imshow(probs.reshape(1, size), cmap=plt.get_cmap('cool'), vmin=0, vmax=1)
    probsStr = ["" for i in range(size)]

    for i in range(size):
        probsStr[i] = ax.text(i % size, i // size, "", fontsize=12,
                              horizontalalignment='center', verticalalignment='center')
    return fig, ax, probsNum, probsStr


def createBellWindow(fig):
    bellProbs_ax = fig.add_subplot(position=(0.78, 0.050, 0.10, 0.3), anchor = "NW")
    bellProbs_ax.tick_params(
        axis='both', which='both', bottom=False, left=False, labelleft=False, labelright=True)
    bellProbsNum = bellProbs_ax.imshow(array([[0.5 for i in range(2)] for j in range(4)]), cmap=plt.get_cmap('cool'), vmin=0 ,vmax=1)
    bellProbsStr = ["" for i in range(8)]
    for i in range(0, 4):
        bellProbsStr[2*i] = bellProbs_ax.text(0, 3-i, "", horizontalalignment='center', verticalalignment='center')
        bellProbsStr[2*i+1] = bellProbs_ax.text(1, 3-i, "", horizontalalignment='center', verticalalignment='center')
    bellProbs_ax.axvline(0.5, c='k')
    for i in range(3):
        bellProbs_ax.axhline(i+0.5, c='k')

    bellProbs_ax.set_xlim(-0.5, 1.5)
    bellProbs_ax.set_ylim(-0.5, 3.5)

    bellProbs_ax.set_xticks(array([i for i in range(2)]))
    bellProbs_ax.set_xticklabels(["", ""], fontsize = 12)
    bellProbs_ax.set_yticks(array([i for i in range(4)]))
    bellProbs_ax.set_yticklabels(["", "", "", ""], fontsize=12)
    return bellProbsNum, bellProbsStr, bellProbs_ax


def createButtonsInfig(fig):
    basis_ax = plt.axes([0.88, 0.44, 0.1, 0.075])
    end_ax = plt.axes([0.78, 0.44, 0.1, 0.075])
    bell2_ax = plt.axes([0.78, 0.365, 0.1, 0.075])
    bell3_ax = plt.axes([0.88, 0.365, 0.1, 0.075])

    h_ax_p = plt.axes([0.78, 0.83, 0.1, 0.075])
    x_ax_p = plt.axes([0.78, 0.755, 0.1, 0.075])
    cx_ax_p = plt.axes([0.78, 0.68, 0.1, 0.075])
    zh_ax_p = plt.axes([0.78, 0.605, 0.1, 0.075])
    ch_ax_p = plt.axes([0.78, 0.53, 0.1, 0.075])
    h_button_p = Button(h_ax_p, 'H:  ')
    x_button_p = Button(x_ax_p, 'X:   ')
    cx_button_p = Button(cx_ax_p, 'CX:   ')
    ch_button_p = Button(ch_ax_p, 'CH:   ')
    zh_button_p = Button(zh_ax_p, 'ZH:   ')
    basis_button = Button(basis_ax, "0,1")
    bell2_button = Button(bell2_ax, "Bell2")
    bell3_button = Button(bell3_ax, "Bell3")
    end_button = Button(end_ax, 'End')

    buttonsDict = {'H': h_button_p, 'X': x_button_p, 'CX': cx_button_p, 'ZH': zh_button_p,
                   'CH': ch_button_p, "Basis": basis_button, "End": end_button, "Bell2": bell2_button,
                   "Bell3": bell3_button}

    h_patch = plt.Rectangle((0.88, 0.83), lw=0.75,
                  width=0.1, height=0.075, edgecolor='black', linewidth=0.75, facecolor='White',
                  transform=fig.transFigure)
    x_patch = plt.Rectangle((0.88, 0.755), lw=0.75,
                            width=0.1, height=0.075, edgecolor='black', linewidth=0.75, facecolor='White',
                            transform=fig.transFigure)
    cx_patch = plt.Rectangle((0.88, 0.68), lw=0.75,
                            width=0.1, height=0.075, edgecolor='black', linewidth=0.75, facecolor='White',
                            transform=fig.transFigure)
    zh_patch = plt.Rectangle((0.88, 0.605), lw=0.75,
                            width=0.1, height=0.075, edgecolor='black', linewidth=0.75, facecolor='White',
                            transform=fig.transFigure)
    ch_patch = plt.Rectangle((0.88, 0.53), lw=0.75,
                            width=0.1, height=0.075, edgecolor='black', linewidth=0.75, facecolor='White',
                            transform=fig.transFigure)
    fig.patches.extend([h_patch])
    fig.patches.extend([x_patch])
    fig.patches.extend([cx_patch])
    fig.patches.extend([zh_patch])
    fig.patches.extend([ch_patch])

    h_text = fig.text(0.88+0.05, 0.83+0.07/2, 'H: ',
             horizontalalignment='center', verticalalignment='center', fontsize=12)
    x_text = fig.text(0.88+0.05, 0.755+0.07/2, 'X: ',
                      horizontalalignment='center', verticalalignment='center', fontsize=12)
    cx_text = fig.text(0.88+0.05, 0.68+0.07/2, 'CX: ',
                      horizontalalignment='center', verticalalignment='center', fontsize=12)
    zh_text = fig.text(0.88+0.05, 0.605+0.07/2, 'ZH: ',
                      horizontalalignment='center', verticalalignment='center', fontsize=12)
    ch_text = fig.text(0.88+0.05, 0.53+0.07/2, 'CH: ',
                      horizontalalignment='center', verticalalignment='center', fontsize=12)

    patchDict = {'H_patch': h_patch, 'X_patch': x_patch, 'CX_patch': cx_patch, 'ZH_patch': zh_patch,
                   'CH_patch': ch_patch, 'H_text': h_text, 'X_text': x_text, 'CX_text': cx_text, 'ZH_text': zh_text,
                   'CH_text': ch_text}

    fig.text(0.78 + 0.05, 0.93, 'Your Hand:',
             horizontalalignment='center', verticalalignment='center', fontsize=14)
    fig.text(0.88 + 0.05, 0.93, 'Deck:',
             horizontalalignment='center', verticalalignment='center', fontsize=14)




    gates = ["H", 'X', 'CX', 'CH', 'ZH']
    notGates = ["Basis", 'End', "Bell2", "Bell3"]

    return buttonsDict, gates, notGates, patchDict


def createPlayerPatches(fig, ax, nPlayers, names):
    mid = ax.transData.transform((2, 2))[0] / (fig.get_size_inches() * fig.dpi)[0]

    playerbuttons = []
    playerbet = []
    playerMoney = []
    for i in range(nPlayers):
        playerbuttons.append(plt.Rectangle((mid-(nPlayers*0.1+(nPlayers-1)*0.03)/2+0.13*i, 0.85),
                             width=0.1, height=0.075, edgecolor='black', linewidth=0.75, facecolor='White',
                             transform=fig.transFigure))
        fig.patches.extend([playerbuttons[i]])
        fig.text(mid-(nPlayers*0.1+(nPlayers-1)*0.03)/2+0.13*i+0.05, 0.85+0.07/2, names[i],
                 horizontalalignment='center', verticalalignment='center', fontsize=15)
        playerbet.append(fig.text(mid-(nPlayers*0.1+(nPlayers-1)*0.03)/2+0.13*i+0.05, 0.80, "0",
                              horizontalalignment='center', verticalalignment='center', fontsize = 15))
        playerMoney.append(fig.text(mid - (nPlayers * 0.1 + (nPlayers - 1) * 0.03) / 2 + 0.13 * i + 0.05, 0.70, "0",
                                  horizontalalignment='center', verticalalignment='center', fontsize=15))
    playerbet.append(fig.text(mid-(nPlayers*0.1+(nPlayers-1)*0.03)/2+0.05-0.12, 0.80, "Bets:",
                              horizontalalignment='center', verticalalignment='center', fontsize = 15))
    playerMoney.append(fig.text(mid - (nPlayers * 0.1 + (nPlayers - 1) * 0.03) / 2 + 0.05 - 0.12, 0.70, "Money left:",
                              horizontalalignment='center', verticalalignment='center', fontsize=15))

    return playerbuttons, playerbet, playerMoney


def createBets(fig, ax):
    mid = ax.transData.transform((2, 2))[0]/(fig.get_size_inches()*fig.dpi)[0]
    text_box = TextBox(plt.axes([mid-0.3, 0.15, 0.3, 0.1]), 'Place bet:', initial="")
    betText = fig.text(mid+0.075, 0.2, "0/0",
                              horizontalalignment='center', verticalalignment='center', fontsize=15)
    checkButton = Button(plt.axes([mid+0.15, 0.23, 0.1, 0.075]), "Check")
    foldButton = Button(plt.axes([mid+0.15, 0.15, 0.1, 0.075]), "Fold")
    showPlayerHandButton = Button(plt.axes([mid+0.15, 0.07, 0.1, 0.075]), "Show Hand")
    infoText = fig.text(mid-0.3+0.005, 0.12, "" + "          " + "\n> " + "Place a bet or fold.",
                        horizontalalignment='left', verticalalignment='top', fontsize=12, backgroundcolor="lightgray",
                        wrap=True)
    return text_box, betText, checkButton, foldButton, showPlayerHandButton, infoText


def onclick(event, mouseClick, ax):
    if not(event.xdata is None and event.ydata is None and event.inaxes is None):
        if event.inaxes == ax:
            mouseClick(int(event.xdata+0.5))