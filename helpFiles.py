# Copyright SINTEF 2019
# Authors: Franz G. Fuchs <franzgeorgfuchs@gmail.com>,
#          Christian Johnsen <christian.johnsen97@gmail.com>,
#          Vemund Falch <vemfal@gmail.com>

from numpy import inf
from numpy.random import randint
from tkinter import Tk, simpledialog
# ----Get Inputs--------------------------------------------------------------------------------------------------------


def getIntInput(inputString, numMin, numMax):
    num = inf
    while num<numMin or num>numMax or num==inf:
        try:
            num = int(input(inputString))
        except ValueError:
            print("Du må skrive inn et gyldig tall mellom {} og {}".format(numMin, numMax))
        if num<numMin or num>numMax:
            print("Du må skrive inn et tall mellom {} og {}".format(numMin, numMax))
    return num


def getFloatInput(inputString, numMin, numMax):
    num = inf
    while num<numMin or num>numMax or num==inf:
        try:
            num = float(input(inputString))
        except ValueError:
            print("Du må skrive inn et gyldig tall mellom {} og {}".format(numMin, numMax))
        if num<numMin or num>numMax:
            print("Du må skrive inn et tall mellom {} og {}".format(numMin, numMax))
    return num


def getUnentangledTag(i, bellPairs):
    tag = ""
    for j in range(len(bellPairs)):
        if i in bellPairs[j]:
            tag += "Pair " + chr(ord("A") + j) + "\n"

    return tag


#----Get Random Numbers-----------------

def get2DiffRandNum(size):
    qbit1 = randint(0, size)
    qbit2 = randint(0, size)
    while qbit2 == qbit1:
        qbit2 = randint(0, size)
    return qbit1, qbit2


def get3DiffRandNum(size):
    qbit1 = randint(0, size)
    qbit2 = randint(0, size)
    qbit3 = randint(0, size)
    while qbit2 == qbit1:
        qbit2 = randint(0, size)
    while qbit3 == qbit1 or qbit3 == qbit2:
        qbit3 = randint(0, size)
    return qbit1, qbit2, qbit3


# ----Poker related-----------------------------------------------------------------------------------------------------

def distributeGates(originalDeck: dict, nPlayers: int) -> dict:
    """
    :param originalDeck: dict containing e.g. {'H': 2, 'X': 1, ...}
    :param nPlayers: Number of players
    :return: dict containing players as keys and gate dicts as values {0: {'H': 2,...}, ...}
    """
    pool = originalDeck.copy()
    gates = list(pool.keys())
    n_gates = len(gates)
    playersGates = [dict() for i in range(nPlayers)]

    for i in range(3):
        for player in range(nPlayers):
            found = False
            while not found:
                gate = gates[randint(0, n_gates)]
                if pool[gate] > 0:
                    pool[gate] -= 1
                    if gate in playersGates[player].keys():
                        playersGates[player][gate] += 1
                    else:
                        playersGates[player][gate] = 1
                    found = True
    return playersGates
