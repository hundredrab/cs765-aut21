pragma solidity ^0.8.10;

contract SimpleStorage {
    struct User {
        uint id;
        string username;
    }

    User[] public users;

    mapping(uint => User) public id2user;
    mapping(uint => uint[]) public partners;
    mapping(uint => uint[]) public balances;


    function registerUser(uint userid, string memory username) public {
        User memory user = User(userid, username);
        users.push(user);
        id2user[userid] = user;
        // partners[userid] = uint[] memory;
        // balances[userid] = uint[] memory;
    }

    function createAcc(uint uid1, uint uid2, uint contri) public {
        partners[uid1].push(uid2);
        partners[uid2].push(uid1);
        balances[uid1].push(contri);
        balances[uid2].push(contri);
        assert(partners[uid1].length == balances[uid1].length);
    }

    struct Set {
        uint[] values;
        mapping (uint => bool) is_in;
    }

    uint[] path;
    mapping (uint => bool) visit;


    function sendAmount(uint source, uint target) public returns (uint[] memory) {
        // Set memory visited;
        delete path;
        path.push(source);
        for (uint i=0; i< users.length; i++) {
            visit[users[i].id] = false;
        }
        visit[source] = true;
        bool flag = true;
        // uint counter = 0;
        while (path.length > 0 && path[path.length-1] != target){
            flag = true;
            uint node = path[path.length-1];
            for (uint i = 0; i< partners[node].length; i++) {
                if (visit[partners[node][i]] == false && balances[node][i] >= 1) {
                    visit[partners[node][i]] = true;
                    path.push(partners[node][i]);
                    flag = false;
                    break;
                }
            }
            // if (counter == 5)
            // break;else counter++;
            if (flag == true) path.pop();
        }

        assert(path.length > 0);

        for (uint i=0; i<path.length-1; i++) {
            uint j = i+1;
            uint ii = path[i];
            uint jj = path[j];
            for (uint k=0; k<partners[ii].length; k++) {
                if (partners[ii][k] == jj) {
                    // console.log(partners);
                    balances[ii][k] -= 1;
                    break;
                }
            }
            for (uint k=0; k<partners[jj].length; k++) {
                if (partners[jj][k] == ii) {
                    balances[jj][k] -= 1;
                    break;
                }
            }
        }

        return path;
    }


    function closeAccount(uint uid1, uint uid2) public {
        for (uint i = 0; i < partners[uid1].length; i++){
            if (partners[uid1][i] == uid2) {
                balances[uid1][i] = 0;
                break;
            }
        }
        for (uint i = 0; i < partners[uid2].length; i++){
            if (partners[uid2][i] == uid1) {
                balances[uid2][i] = 0;
                break;
            }
        }

    }

    function getPartners(uint userid) public view returns (uint[] memory) {
        return partners[userid];
    }

    function getBalances(uint userid) public view returns (uint[] memory) {
        return balances[userid];
    }

    // function sendAmount()
}
