# Copyright SINTEF 2019
# Authors: Franz G. Fuchs <franzgeorgfuchs@gmail.com>,
#          Christian Johnsen <christian.johnsen97@gmail.com>,
#          Vemund Falch <vemfal@gmail.com>

from os.path import dirname, abspath
import sys
sys.path.append(dirname(abspath(__file__)))
from Python.PokerGame import PokerGame
import matplotlib.pyplot as plt
from Python.helpFiles import getIntInput
from numpy import array, count_nonzero, nonzero, delete, flip


if __name__ == "__main__":
    dealer = 0
    nPlayers = getIntInput("Enter the number of players (2 to 5): ", 2, 5)
    enableEntanglement = True
    deckOfGates = {"H": nPlayers, "X": nPlayers, "ZH": nPlayers, "CX": nPlayers}
    money = array([100 for i in range(nPlayers)])
    names = ["" for i in range(nPlayers)]
    for i in range(nPlayers):
        names[i] = input("Enter the initials of player {}: ".format(i+1))

    while not count_nonzero(money == 0) == (nPlayers-1):
        pokerGame = PokerGame(deckOfGates, nPlayers, money, names = names, smallBlind=5, smallBlindPlayer=dealer,
                              enableEntanglement = enableEntanglement)
        dealer = (dealer + 1) % nPlayers
        plt.show()
        if 0 in money:
            toDelete=nonzero(money==0)[0]
            for i in flip(toDelete):
                if i < dealer:
                    dealer -= 1
            names = delete(names, nonzero(money==0)[0])
            money = delete(money, nonzero(money==0)[0])
            nPlayers = money.shape[0]
