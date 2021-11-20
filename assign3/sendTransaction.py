import sys
import time
from pprint import pprint
import random
import numpy as np
from math import ceil


from web3 import *
from solcx import compile_source, compile_files
import os


random.seed(42)


def compile_source_file(file_path):
    return compile_files(
        [file_path],
        output_values=['bin', 'abi', 'bin-runtime'],
        solc_version='0.8.10'
    )



def sendEmptyLoopTransaction(address):
    contract_source_path = 'emptyLoop.sol'
    compiled_sol = compile_source_file(contract_source_path)

    contract_id, contract_interface = compiled_sol.popitem()

    sort_contract = w3.eth.contract(
        address=address,
        abi=contract_interface['abi']
    )
    from pprint import pprint
    pprint(contract_interface['abi'])
    tx_hash = sort_contract.functions.runLoop().transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638})
    return tx_hash


print("Starting Transaction Submission")
w3 = Web3(IPCProvider('/home/sourab/Projects/cs765-aut21/assign3/test-eth1/geth.ipc', timeout=100000))

contract_source_path = 'emptyLoop.sol'
compiled_sol = compile_source_file(contract_source_path)

contract_id, contract_interface = compiled_sol.popitem()

with open('contractAddressList') as fp:
    for line in fp:
        #print(line)
        _, address = line.rstrip().split(':', 1)

print(address)
sort_contract = w3.eth.contract(
    address=address,
    abi=contract_interface['abi']
)


def registerUser(userid, username):
    tx_hash = sort_contract.functions.registerUser(userid, username).transact(
        {'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638}
    )
    return tx_hash

def createAcc(id1, id2, amt):
    tx_hash = sort_contract.functions.createAcc(id1, id2, amt).transact(
        {'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638}
    )
    return tx_hash

def sendAmount(id1, id2):
    tx_hash = sort_contract.functions.sendAmount(id1, id2).transact(
        {'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638}
    )
    return tx_hash

def closeAccount(id1, id2):
    tx_hash = sort_contract.functions.closeAccount(id1, id2).transact(
        {'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638}
    )
    return tx_hash

def getBalances(id1):
    tx_hash = sort_contract.functions.closeAccount(id1, id2).transact(
        {'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638}
    )
    return tx_hash



def generate_valid_graph(num=100):
    """Keeps generating random graph until a valid graph is generated.
    Valid => One single component; all nodes reachable.
    """


    def barabasi_albert(n, m):
        """
        Generate a graph with power-law degree distribution.
        Uses the Preferential Attachment algo (Albert & Barabasi, 1999)
        Code modified from SO:
        https://stackoverflow.com/a/59055822/6352364
        """

        def random_subset_with_weights(weights, m):
            mapped_weights = [(random.expovariate(w), i) for i, w in enumerate(weights)]
            return {i for _, i in sorted(mapped_weights)[:m]}

        # Initialise with a complete graph on m vertices.
        neighbours = [set(range(m)) - {i} for i in range(m)]
        degrees = [m - 1 for i in range(m)]

        for i in range(m, n):
            n_neighbours = random_subset_with_weights(degrees, m)

            # add node with back-edges
            neighbours.append(n_neighbours)
            degrees.append(m)

            # add forward-edges
            for j in n_neighbours:
                neighbours[j].add(i)
                degrees[j] += 1

        return neighbours

    def generate_random_graph(num=num):
        """Generates a random graph."""
        return dict(enumerate(barabasi_albert(num, 2)))

    return generate_random_graph(num)

NUM_PEERS = 100
NUM_TRX = 1000

w3.miner.start(1)

g = generate_valid_graph(NUM_PEERS)

for i in range(NUM_PEERS):
    tx = registerUser(i, str(i))
    receipt = None
    while receipt is None:
        receipt = w3.eth.getTransactionReceipt(tx)
        time.sleep(1)
    print("Registered", i, receipt)

pprint(g)

for i, neighs in g.items():
    for j in neighs:
        contri = np.random.exponential(10)
        tx = createAcc(i, j, ceil(ceil(contri)/2))
        receipt = None
        while receipt is None:
            receipt = w3.eth.getTransactionReceipt(tx)
            time.sleep(1)
        print("Account Created", i, j, ceil(ceil(contri)/2), receipt)

for i in range(NUM_TRX):
    source, dest = None, None
    while source == dest:
        source = random.randint(0, NUM_PEERS - 1)
        dest = random.randint(0, NUM_PEERS - 1)
    tx = sendAmount(source, dest)
    receipt = None
    while receipt is None:
        receipt = w3.eth.getTransactionReceipt(tx)
        time.sleep(1)
    print("Amt sending attempted", source, dest, receipt)

w3.miner.stop()
