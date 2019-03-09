pragma solidity ^0.5.4;

contract registrar {
	address public owner;
	mapping(uint => address) public users_by_number;
	mapping (address => uint) public users_by_address;
	

	constructor () public {
		owner = msg.sender;
	}

	event RegistrationRequest(address indexed sender);
	event UnregistrationRequest(address indexed sender);

	function add_user(uint phone_number, address user_address) public {
		if (user_address == users_by_number[phone_number]) {
			revert();
		}
		users_by_number[phone_number] = user_address;
		users_by_address[user_address] = phone_number;
		emit RegistrationRequest(user_address);
	}

	function delete_user(address user_address) public {
		require(users_by_address[user_address] != 0);
		delete users_by_number[users_by_address[user_address]];
		delete users_by_address[user_address];
		emit UnregistrationRequest(user_address);
	}

	function change_con_owner(address new_owner) public {
		require(msg.sender == owner);
		owner = new_owner;
	}
}