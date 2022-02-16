import argparse
import logging
import random
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from heapq import heapify, heappop, heappush
from pathlib import Path

import numpy as np
from tqdm import tqdm

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.WARN)
logger = logging.getLogger(__name__)
random.seed(42)
np.random.seed(42)
sys.setrecursionlimit(50000)


parser = argparse.ArgumentParser()
parser.add_argument("-n", "--num_honest", type=int,
                    help="Number of peers")
parser.add_argument("-t", "--num_transactions", type=int,
                    help="Number of transactions generated by each peer")
parser.add_argument("-i", "--interarrival", type=float,
                    help="Mean of interarrivals between transactions")
parser.add_argument("-m", "--mining_time", type=float,
                    help="Average time to mine")
parser.add_argument("-z", "--num_adversary_connected_nodes", type=float,
                    help="Percent of honest nodes connected to adversary")
args = parser.parse_args(sys.argv[1:])

NUM_HONEST = args.num_honest
NUM_PEERS = NUM_HONEST + 1
ZETA = args.num_adversary_connected_nodes
Z = .5
NUM_TRANS = args.num_transactions
INTERARRIVAL_MEAN = args.interarrival
AVG_MINING_TIME = args.mining_time

if ZETA >= 1:
    ZETA = ZETA / 100


DATA_FOLDER = "data"
LOG_FILE = f"{DATA_FOLDER}/{NUM_HONEST}_{NUM_TRANS}_{INTERARRIVAL_MEAN}_{AVG_MINING_TIME}_{Z}.csv"
Path(DATA_FOLDER).mkdir(parents=True, exist_ok=True)
file_logs = list()


q = list()


# Create link speed matrix c
is_fast = np.random.choice([True, False], NUM_HONEST, p=[1 - Z, Z])
is_fast = np.append(is_fast, True)
c = np.empty((NUM_PEERS, NUM_PEERS))
for i in range(NUM_PEERS):
    for j in range(NUM_PEERS):
        c[i][j] = 5 + (is_fast[i] and is_fast[j]) * 95


# Create propagation delay matrix p; values in ms
p = np.random.uniform(10, 500, (NUM_PEERS, NUM_PEERS))
p = (p + p.T) / 2

##
peers = list(range(NUM_PEERS))
chains = defaultdict(list)
seen_transactions = defaultdict(set)
pool = defaultdict(list)


def generate_random_transaction(source):
    """Returns source, dest, amt after generating a random transaction."""
    # source = random.randrange(NUM_PEERS)
    while (creditor := random.randrange(NUM_PEERS)) == source:
        pass
    amt = abs(10 * np.random.normal())
    return source, creditor, amt


def execute(time, func, *args):
    """Executes the event function func.

    An event function is of the format _funcname,
    and these events are contained in the event queue.
    """
    func(time, *args)


class Transaction:
    """Transaction"""

    def __init__(self, tid, payer, payee, amt):
        self.id = tid
        self.payer = payer
        self.payee = payee
        self.amt = amt

    def __str__(self):
        return f"{self.id}: {self.payer} paid {self.payee} ${self.amt} coins."

    def __repr__(self):
        return f"{self.id}: {self.payer} =={self.amt}=> {self.payee}."


class Block:
    """Block"""

    def __init__(self, generator, prev_block, trxs):
        self.prev = prev_block
        self.trxs = trxs
        self.generator = generator

    @lru_cache(maxsize=3200)
    def block_balance(self):
        """Net output of trxs ONLY in the current block."""
        ledger = defaultdict(int)
        ledger[self.generator] = 50
        for trx in self.trxs:
            ledger[trx.payer] -= trx.amt
            ledger[trx.payee] += trx.amt
        return Counter(ledger)

    @lru_cache(maxsize=3200)
    def overall_balance(self):
        """Net output of all the trxs upto this block."""
        ledger = Counter()
        node = self
        while node is not None:
            ledger.update(node.block_balance())
            node = node.prev
        return ledger

    @lru_cache(maxsize=3200)
    def is_valid(self):
        """Determines if the current block has valid trxs only.

        The balance of any payer may not go below zero at any point.
        """
        ledger = self.prev.overall_balance()
        for trx in self.trxs:
            ledger[trx.payer] -= trx.amt
            if ledger[trx.payer] < 0:
                return False
        return True

    def id(self):
        return hash(self)

    @lru_cache(maxsize=3200)
    def height(self):
        """Height/depth of this block; height(GENESIS) = 0."""
        if self.prev is None:
            return 0
        return self.prev.height() + 1

    @lru_cache(maxsize=3200)
    def get_transaction_set(self):
        """Returns the set of all transaction ids since genesis."""
        block_trxs = set(map(lambda x: x.id, self.trxs))
        if self.prev is None:
            return block_trxs
        prev_trxs = self.prev.get_transaction_set()
        return prev_trxs.union(block_trxs)

    @lru_cache(maxsize=3200)
    def size(self):
        """Returns size in terms of number of transactions inside."""
        return 1 + len(self.trxs)

    def __repr__(self):
        return f"[Ht: {self.height()}; Gen: {self.generator}; #Trx: {len(self.trxs)}]"

    def _writeable(self, timestamp, node):
        return f"{node},{is_fast[node]},{timestamp},{self.id()},{self.height()},{self.prev.id()}\n"


class Message:
    """Message containing a transaction."""

    def __init__(self, txn, source, dest):
        self.trx = txn
        self.source, self.dest = source, dest

    def __str__(self):
        return f"{self.source} -> {self.dest}: \t{self.trx}"

    def __gt__(self, m2):
        return self.source > m2.source


class BlockMessage:
    """Message containing a block."""

    def __init__(self, block: Block, source, dest):
        self.block = block
        self.source, self.dest = source, dest

    def __str__(self):
        return f"{self.source} -> {self.dest}: \t{self.block}"

    def __gt__(self, m2):
        return self.source > m2.source


GENESIS_BLOCK = Block(-1, None, list())
##
# ##### Block testing and debugging ####
"""
GENESIS_BLOCK = Block(-1, None, list())
b1 = Block(1, GENESIS_BLOCK, [Transaction(0, 2, 3, 5), Transaction(1, 3, 2, 10)])
b2 = Block(1, GENESIS_BLOCK, [])
b3 = Block(2, b2, [Transaction(2, 1, 5, 20), Transaction(3, 1, 7, 15)])
b4 = Block(2, b3, [Transaction(5, 2, 5, 50), Transaction(4, 1, 7, 25)])
print(b4.is_valid())
"""
##


def generate_valid_graph(num=NUM_HONEST, zeta=ZETA):
    """
    Keeps generating random graph until a valid graph is generated.

    Valid => One single component; all nodes reachable.

    The adversarial node is connected to `zeta` percent of honest nodes.
    """

    logger.info("Attempting to create a valid graph...")

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

    def generate_random_graph(num=num, zeta=zeta):
        """
        Generates a random graph.

        Also adds edges to the adversary.
        """
        logger.debug("Generating candidate graph")
        gen = dict(enumerate(barabasi_albert(num, 2)))
        connect = np.random.choice(num, round(zeta * num), replace=False)
        gen[num] = set(connect)
        for i in connect:
            gen[i].add(num)
        return gen



    def check_validity(potential_graph):
        if len(potential_graph) < num + 1:
            return False
        visited = {0}
        stack = [0]
        while stack:
            node = stack.pop()
            for neigh in potential_graph[node]:
                if neigh not in visited:
                    stack.append(neigh)
                    visited.add(neigh)
        return len(visited) == num + 1

    while not check_validity((potential_graph := generate_random_graph())):
        logger.debug("Invalid Graph: %s", potential_graph)
    logger.info("Generated graph")
    logger.debug("Valid Graph: %s", potential_graph)
    return potential_graph


graph = generate_valid_graph()


def _transact(time, trx: Transaction):
    """Initiate a transaction on the source node.

    Create events of sending transaction info to itself for simplification."""
    logger.info(f"{time}s:\tCreated transaction: {trx}")
    heappush(q, (time, _receive_transaction, Message(trx, trx.payer, trx.payer)))


def _receive_transaction(time, message: Message):
    """Execute a message receive, by scheduling for forwarding messages."""
    if message.trx.id in seen_transactions[message.dest]:
        return
    logger.debug(f"{time}s:\tMessage recvd: {message}")
    seen_transactions[message.dest].add(message.trx.id)
    pool[message.dest].append(message.trx)
    for neigh in graph[message.dest]:
        if message.source != neigh:
            cij = c[message.dest][neigh]  # kb/ms
            m_c = 8 / cij  # ms
            dij = np.random.exponential(96 / cij)  # ms
            latency = (p[message.dest][neigh] + m_c + dij) / 1000  # s
            rec_time = time + latency
            heappush(
                q,
                (
                    rec_time,
                    _receive_transaction,
                    Message(message.trx, message.dest, neigh),
                ),
            )


block_book = defaultdict(list)
deepest_node = dict((k, GENESIS_BLOCK) for k in range(NUM_PEERS))
pvt = [GENESIS_BLOCK, 0]  # Contains (LATEST_PVT_BLOCK, LEN_OF_PVT_CHAIN)


def _receive_block(time, msg: BlockMessage):
    """Receive a block and propagate it to peers.

    Check if this is the longest chain, and if so,
    immediately start mining a new block.
    """
    if msg.block in block_book[msg.dest]:
        return
    logger.debug(f"{time}s:\tBlock received: {msg}")
    file_logs.append(msg.block._writeable(time, msg.dest))
    block_book[msg.dest].append(msg.block)
    if msg.dest == ADV:
        diff = pvt[0].depth - deepest_node[ADV].depth
        assert diff >= 0
        if msg.block.generator == ADV:
            pvt[0] = msg.block
            if diff == 0 :

        else:
            if msg.block.height() > deepest_node[msg.dest].height():
                deepest_node[msg.dest] = msg.block
            # release 1


    else:
        if msg.block.height() > deepest_node[msg.dest].height():
            heappush(q, (time, _start_mining, msg.dest))
        for neigh in graph[msg.dest]:
            if msg.source != neigh:
                cij = c[msg.dest][neigh]  # kb/ms
                m_c = msg.block.size() * 8 / cij  # ms
                dij = np.random.exponential(96 / cij)  # ms
                latency = (p[msg.dest][neigh] + m_c + dij) / 1000  # s
                rec_time = time + latency
                heappush(
                    q, (rec_time, _receive_block, BlockMessage(msg.block, msg.dest, neigh))
                )


def _start_mining(time, generator):
    """Aggregate trxs and schedule a _mine event for the generated block."""
    logger.debug(f"{time}s:\tMining started by {generator}")
    deepest = GENESIS_BLOCK
    depth = deepest.height()
    for block in block_book[generator]:
        if (b_ht := block.height()) > depth:
            depth = b_ht
            deepest = block
    deepest_node[generator] = deepest
    done = deepest.get_transaction_set()
    ledger = deepest.overall_balance()
    new_block_trxs = list()
    for trx in pool[generator]:
        if len(new_block_trxs) >= 999:  # Max blocksize minus coinbase
            break
        if trx.id in done or ledger[trx.payer] < trx.amt:
            continue
        ledger[trx.payer] -= trx.amt
        new_block_trxs.append(trx)
    new_block = Block(generator, deepest, new_block_trxs)
    mine_time = time + np.random.exponential(AVG_MINING_TIME)
    heappush(q, (mine_time, _mine, new_block))


def _mine(time, block: Block):
    """Mine a block after checking if the longest node is still the same as it
    was when the mining was scheduled.
    Also schedule reception of block-message on neighbours."""
    curr_deep = deepest_node[block.generator]
    if block.prev == curr_deep:  # Update longest chain
        logger.info(f"{time}s:\tMined block: {block}")
        deepest_node[block.generator] = block
        block_msg = BlockMessage(block, block.generator, block.generator)
        heappush(q, (time, _receive_block, block_msg))
    else:
        logger.debug(f"{time}s:\tDiscarded unmined old block: {block}")
    heappush(q, (time + 0.000000001, _start_mining, block.generator))


def populate_transaction_events():
    """Populates initial transaction queue with transaction events."""
    interarrivals = np.random.exponential(INTERARRIVAL_MEAN, (NUM_PEERS, NUM_TRANS))
    tid = 0
    for peer, peer_times in enumerate(interarrivals):
        curr_time = 0
        for time in peer_times:
            curr_time += time
            tid += 1
            q.append(
                (
                    time,
                    _transact,
                    Transaction(tid, *generate_random_transaction(peer)),
                )
            )
    logger.info("Generating transactions spread across time for each node.")
    assert (
        len(q) == NUM_TRANS * NUM_PEERS
    ), "Initial #transactions should be NUM_PEERS X NUM_TRANS"
    heapify(q)
    return interarrivals.max()


def populate_init_mining_events():
    """Each node schedules a mining event at the start of the sim."""
    sched_minings = np.random.exponential(AVG_MINING_TIME, (NUM_PEERS,))
    for peer, mine_time in enumerate(sched_minings):
        block = Block(peer, GENESIS_BLOCK, list())
        heappush(q, (mine_time, _mine, block))
    return sched_minings.mean()


def main():
    trans_max = populate_transaction_events()
    mine_mean = populate_init_mining_events()
    end_time = trans_max + (2 * mine_mean)
    print(f"END_TIME is {end_time}; last trx at {trans_max}")
    with tqdm(total=end_time) as pbar:
        while q and (item:=heappop(q))[0] < end_time:
            execute(*item)
            #execute(*heappop(q))
            pbar.update(q[0][0]-item[0])
    for n in range(NUM_PEERS):
        NODE_FILE = f"{DATA_FOLDER}/{n}.csv"
        with open(NODE_FILE, 'w') as nodefile:
            nodefile.write("peer,is_fast,timestamp,hash,number,parent_hash\n")
            nodefile.writelines(filter(lambda x: x.split(',')[0].strip() == str(n), file_logs))
    with open(LOG_FILE, 'w') as infofile:
        infofile.write("peer,is_fast,timestamp,hash,number,parent_hash\n")
        infofile.writelines(file_logs)


##
if __name__ == "__main__":
    main()


# Genesis, 0001
# Genesis, 0002
# 0001, 0005
# 0001, 0006
# Genesis, 0003
# 0003, 0007
# 0002, 0008
# 0005, 0009


# genesis
# 0001                                00002                                0003
# 00005   0006                          0008                              0007
# 0009