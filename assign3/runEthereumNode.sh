# !/bin/bash
rm -rf $HOME/Projects/cs765-aut21/assign3/test-eth1/geth/chaindata/;
rm -rf $HOME/Projects/cs765-aut21/assign3/test-eth1/geth/lightchaindata/;
rm -rf $HOME/Projects/cs765-aut21/assign3/test-eth1/geth/nodes/;
rm -rf $HOME/Projects/cs765-aut21/assign3/test-eth1/geth/ethash/;
rm -f $HOME/Projects/cs765-aut21/assign3/test-eth1/geth/LOCK;
rm -f $HOME/Projects/cs765-aut21/assign3/test-eth1/geth/transactions.rlp;
geth --datadir $HOME/Projects/cs765-aut21/assign3/test-eth1 --rpc --rpcport=1558 --rpcapi "eth,net,web3,debug" --networkid=2310 --port=1547 --syncmode full --gcmode archive --nodiscover --nodekey=nk.txt init $HOME/Projects/cs765-aut21/assign3/genesis.json
gnome-terminal --geometry 90x25+1300+1550 -- bash startIpc.sh 1
geth --datadir $HOME/Projects/cs765-aut21/assign3/test-eth1 --rpc --rpcport=1558 --rpcapi "eth,net,web3,debug" --networkid=2310 --port=1547 --syncmode full --gcmode archive --nodiscover --nodekey=nk.txt --verbosity 5 --allow-insecure-unlock --unlock 0 --password password.txt
