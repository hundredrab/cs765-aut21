Note that we assume the version of go-ethereum is 1.9.3, solidity 0.8.10

We're also using py-solc-x instead of py-solc in order to interact with the latest versions of solc compiler.

The solidity file is `emptyLoop.sol`, and the python code for interacting with the contract is in `sendTransaction.py`.

1. Install py-solc-x and web3:
`pip3 install py-solc-x web3==4.9.0`

Also install the latest version of solc:
`sudo apt install solc`

2. Run the following command and copy the address to the genesis.json in the alloc section that adds the balance to the geth account.

    `geth --datadir test-eth1/ --password password.txt account new`


3. Run the following command to set up the Ethereum node.

    `sh runEthereumNode.sh`


4. Run the following command, which will deploy the smart contract and copy the smart contract address to contractAddressList

    `python3 deployContract.py > contractAddressList`


5. Run the following command to send the transaction

    `python3 sendTransaction.py`
