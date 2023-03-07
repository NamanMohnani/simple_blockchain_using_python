'''
This blockchain is created in a single file, main.py

Source code: https://github.com/dvf/blockchain/blob/master/blockchain.py

Blockchain is an immutable, sequential chain of records called blocks.
They can contain transactions, files or any data you like, really.
They're chained together using hashes.

the idea of a chain should be apparent—each new block contains within itself,
the hash of the previous Block. This is crucial because it’s what gives
blockchains immutability: If an attacker corrupted an earlier Block in the chain then all subsequent
blocks will contain incorrect hashes.

A Proof of Work algorithm (PoW) is how new Blocks are created or mined on the blockchain.
The goal of PoW is to discover a number which solves a problem. The number must be difficult to find but
easy to verify—computationally speaking—by anyone on the network. This is the core idea behind Proof of Work.

In Bitcoin, the Proof of Work algorithm is called Hashcash. And it’s not too different from our basic example
above. It’s the algorithm that miners race to solve in order to create a new block.
In general, the difficulty is determined by the number of characters searched for in a string.
The miners are then rewarded for their solution by receiving a coin—in a transaction.

We’re going to use the Python Flask Framework. It’s a micro-framework and it makes it easy to map endpoints
to Python functions. This allows us talk to our blockchain over the web using HTTP requests.

But the whole point of Blockchains is that they should be decentralized. And if they’re decentralized,
how on earth do we ensure that they all reflect the same chain? This is called the problem of Consensus,
and we’ll have to implement a Consensus Algorithm if we want more than one node in our network.

The first method valid_chain() is responsible for checking if a chain is valid by looping through each block
and verifying both the hash and the proof.

resolve_conflicts() is a method which loops through all our neighbouring nodes, downloads their chains and
verifies them using the above method. If a valid chain is found, whose length is greater than ours,
we replace ours.



'''

