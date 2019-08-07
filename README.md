# Quantum Poker
This repository contains all the necessary components to learn and play quantum poker. The game works in the same way as Texas hold 'em poker with the main difference being that the community cards are replaced by qubits and the player cards are replaced by quantum logic gates.
This implementation is a proof-of-concept, but it is fully possible to create apps for mobile phones or tablets.
We hope you enjoy playing the game!

![Quantum Poker](quantumpoker.jpg)

## Basic Rules to get started
In order to play the basic version of this game, one does not have to learn or understand any quantum physics, or have a rigorous understanding of poker rules.  Even if this game involves only rudimentary essentials of quantum computing, people that are new to the field will find that it takes some time to get used to the rule set. This is why we have created a game in the first place, because learning should be fun!

At the start of the game, each player start with a pre-set amount of money. A game is then divided into many rounds with identical rules, which is described below.

At the start a round each player is given a randomized set of "quantum gates" from a preset "deck of gates". These quantum gates need not be the same for each player. The quantum gates can be viewed by pressing the button marked with "View Hand", and is shown in the leftmost coloumn. The rightmost coloumn shows all the gates in the deck of gates. These gates is not to be used until later in the game, and will be explained shortly. 

Before any more information is revealed to the players, a round of betting takes place. To not lose in the current round, each player need to at least match the current highest bet on the table. If a player instead chooses to fold by pressing the "Fold"-button, the player looses all the money ihe or she has placed on the table in the current round and is not able to play for the remainder of the round. The player will still be able to play in later rounds. To match the currently highest bet one presses the "Check"/"Call"-button. If a player wants to increase the highest bet by a set amount, he or she can enter the amount to increase the highest bet with into to "Bet:"-box, and hit enter. Note that two of the players automatically start with some money on the table.

Three "cards" are then revealed on the table. These cards are in a state marked that can be marked by |0>, |1>, |-> or |+> as well as some probabilities. The P(1)-probability determine the chance that the card gets the value 1 at the end of the round. _Later_ in the game the players will be able to apply their gates to these cards to change them. The gates changes the cards on the table in a given way. For example the X-gate changes |0> to |1>, and H changes |-> to |1>. For a full list of transformations, see the table at the end of this file. If two qubits are both marked with "Pair A", they are in an entangled state, and can be unentangled by applying a CX-gate. 

After the first three cards have been revealed, a second round of betting takes place, before another card is revealed. Then a third round of betting takes place, before the fifth and final card is revealed. Finally a last round of betting takes place. After all players have finished betting, the players takes turns apllying their gates to the cards, by first clicking on the gate and the on the desired card. To apply the CX gate the player needs to click on 2 qubits. Note that each player have their own cards, but that their initial values are shared by all players. After a player has used all the gates he wants to, he presses the "End" button to end his turn. Once all players are finished, each players cards are giving either the value 0 or the value 1 based on the P(1)-probability shown on the card. The player(s) whose cards gives the most ones then wins the round, and takes all the money on the table. 

If a player has no money left on the table, he is out of the game, and the winner is the last person to have any money left.

## How to get started
The game requires the Qiskit package for Python to be able to run. For help installing Qiskit please see [qiskit.org](https://qiskit.org/documentation/install.html). In the Jupyter Notebok file [runPokerJN.ipynb](runPokerJN.ipynb) an example game along with instructions on how to play the game is included. To play the game, either open the file [runInteractivePokerJN.ipynb](runInteractivePokerJN.ipynb) through Jupyter Notebook (in a Qiskit environment) or run the file [runPoker.py](runPoker.py) locally. Running the game in Jupyter Notebook is notably slower than running the proper Python file.

You can also find more info here [https://arxiv.org/abs/1908.00044](https://arxiv.org/abs/1908.00044).

## Detailed description the game
Note that this section assumes rudementary knowledge of how to play the game. We advise trying a couple of rounds before reading this section.

The basic entity of a quantum computer is called a quantum bit or qubit. While a classical bit can be either 0 or 1, a qubit can also exist in a combination of both 0 and 1. This is called a "superposition". The "value" of a qubit is called a qubit state, and qubit states are often written in bra-ket notation, i.e. a qubit which has the value 1 would be written as being in the state |1>. An example of states that are in a superposition is the states denoted by |+> = |0> + |1> and |-> = |0> - |1>.

In order to obtain information on the state of qubits, they have to be measured. A measurement will collapse the state to a classical bit and return either 0 or 1.

When measuring a qubit in state |0> one will get the classical state 0 with 100% probability, and for |1> one will get 1 with 100% probability. When one measures a qubit in state |+> or |-> however, one will either get the classical value 0 or the value 1 with equal probability for each, i.e. 50% each.

At the start of the game, a set of 5 qubits is created, where each qubit is in a randomized state. Each player is then given a copy of this set, so that all players have an identical set of 5 qubits. The goal of the game is then to change the state of your own qubits, so that as many as possible of the qubits collapse to 1 upon being measured. Remember that a qubit in state |1> has a 100% chance to collapse to 1, while a qubit in state |0> has a 0% to collapse to 1. Note that the states of the qubits in the set are gradually revealed to the players between each round of betting.

This brings us to next important topic, how to change the state of the qubits. This can be achieved by applying a "gate" to one or more qubits. In this game there a total of 4 gates. 

The first gate is the X-gate which changes |1> to |0> and |0> to |1>, but does nothing to |+> and |-> (The interested reader can check this against the definition of |+> and |->. Note that the phase is of no interested, i.e. -|->=|->). We write this as X|0>=|1> and X|1>=|0>.

We also have the Z-gate which does nothing to the states |0> and |1>, but interchanges |+> and |->, i.e. Z|+>=|-> and Z|->=|+>, and the H gate which interchanges |0> and |+>, and |1> and |->. For a full breakdown see the table below.

Each player is dealt three random gates at the start of the game, which need not be the same as for any other player. When betting ends, each player uses his/her gates to change their qubits, to maximize the chance of measuring 1 for each qubit. The winner of the round is then the player with the most measured 1 between the 5 qubits. 

Another important effect in quantum computing is called entanglement. By this is meant that the measured value of two or more qubits is dependent on one another. For example both qubits might have 50% chance to be measured to either 1 or to 0, but they will always be measured to the same value. However, there is no way to know which value they will collapse to until one actually performs a measurment on at least one of the qubits. 

Two qubit states is written as |q<sub>1</sub>q<sub>2</sub>>, where |q<sub>1</sub>> is the state of the first qubit, and |q<sub>2</sub>> is the state of the second. For example the state |00> means both the first and second qubit is in the state |0>. The entangled state described in the previous paragraph could be written as |00> + |11> or |00> - |11>. Both states looks identical if you try to measure them directly, but will behave differently when you start applying gates. One could also have the entangled states |01> + |10> or |01> - |10>, in this case the two qubits will always be measured to different values, but again there is an equal probability for the two possibilities.

The last gate implemented in this game is the controlled not (CX) gate. This applies an X-gate to the second qubit if the first qubit is in the state |1>, and does nothing when the first qubit is in the state |0>. For example the state |00> is unchanged upon apllying a CX-gate as the first qubit is int the state |0>, but the state |10> changes to the state |11>. See the table below for a full overview of different possibilities when applying a CX gate.

The last thing is to note that all gates used here are their own inverse, i.e. applying a gate twice to a state will give the initial state again. However this is not the case for all possible gates.

## Table for effects of the different gates

#### Not gate X <br />
X|0> = |1> <br />
X|1> = |0> <br />
X|+> = |+> <br />
X|-> = |-> <br />

#### Hadamard gate H <br />
H|0> = |+> <br />
H|1> = |-> <br />
H|+> = |0> <br />
H|-> = |1> <br />

#### Phase flip gate Z <br />
Z|0> = |0> <br />
Z|1> = |1> <br />
Z|+> = |-> <br />
Z|-> = |+> <br />

#### Controlled Not gate CX<br />
CX|00> = |00> <br />
CX|01> = |01> <br />
CX|10> = |11> <br />
CX|11> = |10> <br />

CX|+0> = |00> + |11> <br />
CX|+1> = |01> + |10> <br />
CX|-0> = |00> - |11> <br />
CX|-1> = |01> - |10> <br />

CX|++> = |++> <br />
CX|+-> = |--> <br />
CX|-+> = |-+> <br />
CX|--> = |+-> <br />

CX|0+> = |0+> <br />
CX|0-> = |0-> <br />
CX|1+> = |1+> <br />
CX|1-> = |1-> <br />
