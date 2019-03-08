pragma solidity ^0.5.4;

contract payments {
	address public owner;

	constructor() public {
		owner = msg.sender;
	}

	function print_owner() public view returns(address) {
		return owner;
	}
	
	function change_con_owner(address new_owner) public {
		require(msg.sender == owner);
		owner = new_owner;
	}
}
