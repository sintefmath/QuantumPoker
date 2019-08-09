# Copyright SINTEF 2019
# Authors: Franz G. Fuchs <franzgeorgfuchs@gmail.com>,
#          Christian Johnsen <christian.johnsen97@gmail.com>,
#          Vemund Falch <vemfal@gmail.com>

from os.path import dirname, abspath
import sys
sys.path.append(dirname(abspath(__file__)))
from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit, execute
from Python.helpFiles import get2DiffRandNum, get3DiffRandNum
from qiskit import BasicAer
from numpy import power, abs, where, array, zeros, empty, absolute, sort
from numpy.random import randint, seed
from scipy.constants import pi


class Board:
    def __init__(self, boardSeed=43, enableEntanglement=False, nRandOneQGates=5, nRandTwoQGates=5):
        """
        Initializes a board with a QuantumCircuit containing a QuantumRegister adn QuantumCircuit, and randomizes the
        initial state. The variable PreviousBellPairs minimizes the number of times one need to search for the BellPairs.
        :param boardSeed: the seed which is used to create the random boardstate
        :param enableEntanglement: Whether to use randomized CX-gates
        :param nRandOneQGates: Number of one qubit-gates to apply in randomizing the initial state
        :param nRandTwoQGates: Number of two qubit-gates to apply in randomizing the initial state
        """
        self.size = 5

        self.doubleGates = ["CH", "CX", "SWAP"]
        self.tripleGates = ["CCX"]

        self.q = QuantumRegister(self.size)
        self.c = ClassicalRegister(self.size)
        self.qc = QuantumCircuit(self.q, self.c)

        self.previousBellPairs = []
        self._createInitState(boardSeed, enableEntanglement, nRandOneQGates, nRandTwoQGates)

    def _createInitState(self, boardSeed, enableEntanglement, nRandOneQGates, nRandTwoQGates):
        """
        Randomizes the initial state
        :param all: see definition of __init__
        """
        gates = ("H", "HZ", "X", "Id")
        seed(boardSeed)
        for i in range(nRandOneQGates):
            gate = randint(0, len(gates))
            if gates[gate] == "H":
                self.qc.h(self.q[i])
            elif gates[gate] == "HZ":
                self.qc.h(self.q[i])
                self.qc.z(self.q[i])
            elif gates[gate] == "X":
                self.qc.x(self.q[i])
            else:
                pass
        if enableEntanglement:
            gates = ("CX", )
            for i in range(nRandTwoQGates):
                gate = randint(0, len(gates))
                self._doRandGate(gates[gate])
        self.findBellPairs()

    def getSize(self):
        return self.size

    def getBellPairs(self):
        return self.previousBellPairs

    def playerMoveInteractive(self, gate, gateCoords):
        """
        Applies a set playermove by applying gate to qubits at gatecoord.
        :param gate: The gate to be applied
        :param gateCoords: The coordinate at which the gate is to be applied. Contains up to 3 coordinates.
        :return: None
        """
        if gate == "H":
            self.qc.h(self.q[int(gateCoords[0])])

        elif gate == "X":
            self.qc.x(self.q[int(gateCoords[0])])

        elif gate == "Z":
            self.qc.z(self.q[int(gateCoords[0])])

        elif gate == "ID":
            pass

        elif gate == "SRX":
            self.qc.u3(pi/2, pi/2, -pi/2, self.q[int(gateCoords[0])])

        elif gate == "CX":
            qubit1 = int(gateCoords[0])
            qubit2 = int(gateCoords[1])
            self.qc.cx(self.q[qubit1],
                       self.q[qubit2])

        elif gate == "CH":
            qubit1 = int(gateCoords[0])
            qubit2 = int(gateCoords[1])
            self.qc.ch(self.q[qubit1],
                       self.q[qubit2])

        elif gate == "SWAP":
            qubit1 = int(gateCoords[0])
            qubit2 = int(gateCoords[1])
            self.qc.swap(self.q[qubit1],
                         self.q[qubit2])

        elif gate == "CCX":
            qubit1 = int(gateCoords[0])
            qubit2 = int(gateCoords[1])
            qubit3 = int(gateCoords[2])
            self.qc.ccx(self.q[qubit1],
                        self.q[qubit2],
                        self.q[qubit3])

        elif gate == "ZH":
            self.qc.z(self.q[int(gateCoords[0])])
            self.qc.h(self.q[int(gateCoords[0])])

        elif gate == "SRZ":
            self.qc.s(self.q[int(gateCoords[0])])

    def getProbsPlusMinus(self):
        """
        Finds the probabilities that the qubits give - upon being measured in the +,- basis
        :return: the probabilities
        """
        probs = zeros(self.size)
        psi = self.getPsi()
        for qbit in range(self.size):
            dist = 2**qbit
            gaps = 2**(qbit+1)
            for j in range(2**(self.size-qbit-1)):
                for i in range(0, 2**qbit):  # i -> j*dist[1]+i
                    probs[qbit] += power(absolute(psi[i + j * gaps] - psi[i + j * gaps + dist]), 2)
        return probs / 2

    def getProbs01(self):
        """
        Finds the probabilities that the qubits give 1 upon being measured in the 1,0 basis
        :return: the probabilities
        """
        probabilities = empty(self.size)
        psi = self.getPsi()
        for i in range(self.size):
            probabilities[i] = (self.readProbability(i, psi))
        return probabilities

    def readProbability(self, i, psi):
        # Sum absolute squares of amplitudes in psi corresponding to qubit #i being 1.
        probability = 0
        # Size of cluster of 1's in ith pos. when
        # looking at list of basis vectors |0...00>, |0...01>, ...
        groupSize = 2 ** i
        # Takes out every other cluster of length groupSize
        for startIndex in range(groupSize, 2 ** self.size, 2*groupSize):
            for index in range(startIndex, startIndex + groupSize):
                probability += abs(psi[index]) ** 2
        return probability

    def getBellStateProbs(self, coords, psi):
        """
        A two-qubit state can use the four 2-qubit bell-states as a basis. Finds the probabilities that the system will
        be measured to be in each of the four bell-states.
        :param coords: The coordinates of the two qubits
        :param psi: The wavevector of the system.
        :return: The probabilities
        """
        order = array([where(coords==i)[0][0] for i in sort(coords)])
        probs = zeros(4)
        dist = array([0, 2**(coords[0]), 2**(coords[1]),  2**(coords[0])+2**(coords[1])])
        gaps = array([2**(coords[order[0]]+1), 2**(coords[order[1]]+1)])
        for k in range(2**(self.size-coords[order[1]]-1)):
            for j in range(2**(coords[order[1]]-coords[order[0]]-1)):
                for i in range(0, 2**coords[order[0]]): # i -> j*dist[1]+i
                    probs[0] += power(absolute(psi[i + j*gaps[0]+k*gaps[1]] +
                                               psi[i + j*gaps[0]+k*gaps[1] + dist[3]]), 2)
                    probs[1] += power(absolute(psi[i + j*gaps[0]+k*gaps[1]] -
                                               psi[i + j*gaps[0]+k*gaps[1] + dist[3]]), 2)
                    probs[2] += power(absolute(psi[i + j*gaps[0]+k*gaps[1] + dist[1]] +
                                               psi[i + j*gaps[0]+k*gaps[1] + dist[2]]), 2)
                    probs[3] += power(absolute(psi[i + j*gaps[0]+k*gaps[1] + dist[1]] -
                                               psi[i + j*gaps[0]+k*gaps[1] + dist[2]]), 2)
        return probs/2

    def getBellStateProbs3(self, coords, psi):
        """
        A three-qubit state can use the eight 3-qubit bell-states as a basis. Finds the probabilities that the system will
        be measured to be in each of the eight bell-states.
        :param coords: The coordinates of the two qubits
        :param psi: The wavevector of the system.
        :return: The probabilities
        """
        order = array([where(coords==i)[0][0] for i in sort(coords)])
        probs = zeros(8)
        dist = array([0, 2**coords[2], 2**coords[1], 2**coords[0], 2**coords[1]+2**coords[2], 2**coords[0]+2**coords[2],
                      2**coords[0]+2**coords[1], 2**coords[0]+2**coords[1]+2**coords[2]])
        gaps = array([2**(coords[order[0]]+1), 2**(coords[order[1]]+1), 2**(coords[order[2]]+1)])
        for l in range (2**(self.size-coords[order[2]]-1)):
            for k in range(2**(coords[order[2]]-coords[order[1]]-1)):
                for j in range(2**(coords[order[1]]-coords[order[0]]-1)):
                    for i in range(0, 2**coords[order[0]]):
                        for index in range(0, 4):
                            probs[2*index]+= power(absolute(psi[i + j*gaps[0] + k*gaps[1] + l*gaps[2] + dist[index]] +
                                                   psi[i + j*gaps[0] + k*gaps[1]  + l*gaps[2] + dist[7-index]]), 2)
                            probs[2*index+1] += power(
                                absolute(psi[i + j * gaps[0] + k * gaps[1] + l * gaps[2] + dist[index]] -
                                         psi[i + j * gaps[0] + k * gaps[1] + l * gaps[2] + dist[7 - index]]), 2)
        return probs/2

    def getPsi(self):
        """
        Finds the wavevector of the system
        :return: The wavevector of the system
        """
        return execute(self.qc, BasicAer.get_backend("statevector_simulator"), shots=1).result()\
                          .get_statevector(self.qc)

    def findBellPairs(self):
        """
        Searches the system for qubits in a two-qubit Bell-state
        :return: List[tuple[int1, int2], ], where each tuple corresponds to one Bell pair
        """
        pairs = []
        psi = self.getPsi()
        for i in range(self.size - 1):
            for j in range(i + 1, self.size):
                bellStateProbs = list(self.getBellStateProbs((i, j), psi))
                bellStateProbs.sort(reverse=True)
                if abs(bellStateProbs[0]-1) < 1e-4:
                    pairs.append((i, j))

        self.previousBellPairs = pairs
        return pairs

    def _doRandGate(self, gate):
        """
        Applies a random gate at a random qubit(s)
        :param gate: the gate to be applied
        :return: None
        """
        if gate == "H":
            self.qc.h(self.q[randint(0, self.size)])
        elif gate == "CH":
            qbit1, qbit2 = get2DiffRandNum(self.size)
            self.qc.ch(self.q[qbit1], self.q[qbit2])
        elif gate == "X":
            self.qc.x(self.q[randint(0, self.size)])
        elif gate == "Z":
            self.qc.z(self.q[randint(0, self.size)])
        elif gate=="CCX":
            qbit1, qbit2, qbit3 = get3DiffRandNum(self.size)
            self.qc.ccx(self.q[qbit1], self.q[qbit2], self.q[qbit3])
        elif gate=="CX":
            qbit1, qbit2 = get2DiffRandNum(self.size)
            self.qc.cx(self.q[qbit1], self.q[qbit2])
        elif gate=="SRX":
            self.qc.u3(pi/2, pi/2, -pi/2, self.q[randint(0, self.size)])
        elif gate=="SRZ":
            self.qc.s(self.q[randint(0, self.size)])
        elif gate == "U":
            self.qc.u3(randint(0, 360)*pi/360, randint(0, 4)*pi/4, randint(0, 4)*pi/4, self.q[randint(0, self.size)])
