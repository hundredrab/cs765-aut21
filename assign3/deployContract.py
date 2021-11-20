import sys
import time
import pprint

from solcx import compile_source, compile_files
from web3 import *
import os



k = 10
def compile_source_file(file_path):
    return compile_files(
        ['emptyLoop.sol'],
        output_values=['bin', 'abi', 'bin-runtime'],
        solc_version='0.8.10'
    )

def read_address_file(file_path):
    file = open(file_path, 'r')
    addresses = file.read().splitlines()
    return addresses


def connectWeb3():
    return Web3(IPCProvider(
        '/home/sourab/Projects/cs765-aut21/assign3/test-eth1/geth.ipc',
        timeout=100000
    ))


def deployEmptyContract(contract_source_path, w3, account):
    compiled_sol = compile_source_file(contract_source_path)
    contract_id, contract_interface3 = compiled_sol.popitem()
    curBlock = w3.eth.getBlock('latest')
    #import pdb; pdb.set_trace()
    tx_hash = w3.eth.contract(
            abi=contract_interface3['abi'],
            bytecode=contract_interface3['bin']).constructor(4).transact({'txType':"0x0", 'from':account, 'gas':'FFFFFF'})
    return tx_hash

def deployContracts(w3, account):
    tx_hash3 = deployEmptyContract(empty_source_path, w3, account)

    receipt3 = w3.eth.getTransactionReceipt(tx_hash3)

    while ((receipt3 is None)) :
        time.sleep(1)
        receipt3 = w3.eth.getTransactionReceipt(tx_hash3)

    w3.miner.stop()

    if receipt3 is not None:
        print("empty:{0}".format(receipt3['contractAddress']))


empty_source_path = '/home/sourab/Projects/cs765-aut21/assign3/emptyLoop.sol'


w3 = connectWeb3()
w3.miner.start(1)
time.sleep(4)
deployContracts(w3, w3.eth.accounts[0])
