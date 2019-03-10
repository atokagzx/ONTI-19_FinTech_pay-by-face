pragma solidity ^0.5.4;

contract registrar {
	address public owner;
	mapping(address => string) public pending_add;
	mapping(address => string) public pending_del;
	mapping(address => string) public confirmed_users;
	mapping(string => address) public confirmed_users_by_number;
	address[] public addresses_add;
	address[] public addresses_del;
	
	
	constructor () public {
		owner = msg.sender;
	}

	event RegistrationRequest(address indexed sender);
	event UnregistrationRequest(address indexed sender);
	event RegistrationCanceled(address indexed sender);
	event UnregistrationCanceled(address indexed sender);
	event RegistrationConfirmed(address indexed sender);

	function add_user_pend(string memory phone_number, address user_address) public {
	    bytes memory num = bytes(pending_add[user_address]);
		require(num.length == 0);
		pending_add[user_address] = phone_number;
		addresses_add.push(user_address);
		for (uint i = 0; i < addresses_del.length; ++i) {
		    if (user_address == addresses_del[i]) {
		        delete addresses_del[i];
		        break;
		    }
		}
		emit RegistrationRequest(user_address);
	}
	
	function delete_user_pend(address user_address) public returns(uint){
	    bytes memory check = bytes(pending_del[user_address]);
	    if(check.length > 0) {
	    	revert();
	    }
	    addresses_del.push(user_address);
	    pending_del[user_address] = confirmed_users[user_address];
	    emit UnregistrationRequest(user_address);
	}
	
	function cancel(address user_address) public returns(uint){
	    bytes memory ad = bytes(pending_add[user_address]);
	    bytes memory dl = bytes(pending_del[user_address]);
	    if(ad.length != 0) {
	        delete pending_add[user_address];
	        emit RegistrationCanceled(user_address);
	    }
	    if(dl.length != 0) {
	        delete pending_del[user_address];
	        emit UnregistrationCanceled(user_address);
	    }
	    else {
	        revert();
	    }
	}

	function change_con_owner(address new_owner) public {
		require(msg.sender == owner);
		owner = new_owner;
	}

	function get_list_add() public view returns(address[] memory) {
		return addresses_add;
	}

	function get_list_del() public view returns(address[] memory) {
		return addresses_del;
	}

    function confirm_act(address user_address, address owner_address) public {
		if(owner_address != owner) {
			revert();
		}
		bytes memory add = bytes(pending_add[user_address]); 
		bytes memory del = bytes(pending_del[user_address]);
		if(add.length != 0) {
		    confirmed_users[user_address] = pending_add[user_address];
		    confirmed_users_by_number[confirmed_users[user_address]] = user_address; 
		    delete pending_add[user_address];
		     for (uint i = 0; i < addresses_add.length; ++i) {
		        if (user_address == addresses_add[i]) {
		            delete addresses_add[i];
		            break;
		        }
		    }
		}
		else if(del.length != 0) {
		    delete confirmed_users[user_address];
		    delete pending_del[user_address];
		    for (uint i = 0; i < addresses_del.length; ++i) {
		        if (user_address == addresses_del[i]) {
		            delete addresses_del[i];
		            break;
		        }
		    }
		}
		else {
		    revert();
		}
	}
}