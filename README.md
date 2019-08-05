# Quantum Poker
This repository contains all the necessary components to learn and play quantum poker. The game works in the same way as Texas hold 'em poker with the main difference being that the community cards are replaced by qubits and the player cards are replaced by quantum logic gates.
This implementation is a proof-of-concept, but it is fully possible to create apps for mobile phones or tablets.

You can also find more info here [https://arxiv.org/abs/1908.00044](https://arxiv.org/abs/1908.00044). We hope you enjoy playing the game!

![Quantum Poker](quantumpoker.jpg)

## Basic Rules to get started
We assume familiarity with the rules of Texas Hold 'em.
Just as with any other game, one needs to learn a set of rules.
In order to play the basic version of this game, one does not have to learn or understand any quantum physics.
It is enough to learn the transformation rules listed below.

Even if this game involves only rudimentary essentials of quantum computing, people that are new to the field will find that it takes some time to get used to the rule set. This is why we have created a game in the first place, because learning should be fun!

The basic entity of a quantum computer is called a quantum bit or qubit. While a classical bit can be either 0 or 1, a qubit can also exist in states that is a combination of both 0 and 1. This is called a "superposition". Qubit states are often written in bra-ket notation, i.e. a qubit which is in the state 1 would be written as |1>. An example of a state that is in superposition is the state  denoted by |+> = |0> + |1>.

In order to obtain information on the state of qubits, they have to be measured. A measurement will collapse the state to a classical bit and return either 0 or 1.

When one measures a qubit in state |+> one will get the classical state 0 or 1 with equal probability, i.e., 50% each.
When measuring a qubit in state |0> one will get the classical state 0 with 100% probability, and for |1> one will get 1 with 100% probability. There is also a state denoted by |-> = |0> - |1> which will get the classical state 0 or 1 with equal probability, i.e., 50% each.

The next important thing to know is that one can change the state of qubits. For instance one can apply what is known as the NOT gate X, which has the following effect <br />
X|0> = |1> <br />
X|1> = |0> <br />
X|+> = |+> <br />
X|-> = |-> <br />

Another important operation on qubits is the Hadamard gate H. It has the following effect <br />
H|0> = |+> <br />
H|1> = |-> <br />
H|+> = |0> <br />
H|-> = |1> <br />

The final important operation on one qubit is the Z gate, which has the following rules <br />
Z|0> = |0> <br />
Z|1> = |1> <br />
Z|+> = |-> <br />
Z|-> = |+> <br />

The final operation one needs to know is something called a controlled not gate CX. It acts on two bits and flips the second bit only if the first bit is 1: <br />
CX|00> = |00> <br />
CX|01> = |01> <br />
CX|10> = |11> <br />
CX|11> = |10> <br />

The action of the contolled NOT gate is <br />
CX|+0> = |00> + |11> <br />
CX|+1> = |01> + |10> <br />
CX|-0> = |00> - |11> <br />
CX|-1> = |01> - |10> <br />

CX|++> = |++> <br />
CX|+-> = |--> <br />
CX|-+> = |-+> <br />
CX|--> = |+-> <br />

## How to get started
The game requires the Qiskit package for Python to be able to run. For help installing Qiskit please see [qiskit.org](https://qiskit.org/documentation/install.html). In the Jupyter Notebok file [runPokerJN.ipynb](runPokerJN.ipynb) an example game along with instructions on how to play the game is included. To play the game, either open the file [runInteractivePokerJN.ipynb](runInteractivePokerJN.ipynb) through Jupyter Notebook (in a Qiskit environment) or run the file [runPoker.py](runPoker.py) locally. Running the game in Jupyter Notebook is notably slower than running the proper Python file.
