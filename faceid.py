#!/usr/bin/env python

from web3 import Web3, HTTPProvider
from sha3 import keccak_256
from json import load
import sys

web3 = Web3(HTTPProvider("https://sokol.poa.network"))

with open("person.json") as person:
	data = load(person)
	ID = data["id"].split("-")

def make_ID(ID):
	sum = ""
	for i in range(5):
		sum += ID[i]
	return int(sum, 16).to_bytes(16, "big")

def num_pin(pin_code, num):
	return int(pin_code[num]).to_bytes(1, "big")

def make_privet_key(ID, pin_code):
	m = make_ID(ID)
	privet_key = keccak_256("".encode("utf-8")).digest()
	privet_key = keccak_256(privet_key + m + num_pin(pin_code, 0)).digest()
	privet_key = keccak_256(privet_key + m + num_pin(pin_code, 1)).digest()
	privet_key = keccak_256(privet_key + m + num_pin(pin_code, 2)).digest()
	privet_key = keccak_256(privet_key + m + num_pin(pin_code, 3)).digest()
	privet_key = hex(int.from_bytes(privet_key, "big"))[2:]
	return privet_key

def convert(balance):
    if balance < 10**3:
        return str(balance) + " wei"
    elif balance < 10**6:
        balance = balance / 10**3
        if len(str(balance)) > 8:
        	return "{0:.6f}".format(balance).rstrip('0').rstrip(".") + " kwei"
       	return str(balance) + " kwei"
    elif balance < 10**9:
    	balance = balance / 10**6
    	if len(str(balance)) > 8:
    		return "{0:.6f}".format(balance).rstrip('0').rstrip(".") + " mwei"
    	return str(balance) + " mwei"
    elif balance < 10**12:
    	balance = balance / 10**9
    	if len(str(balance)) > 8:
    		return "{0:.6f}".format(balance).rstrip('0').rstrip(".") + " gwei"
    	return str(balance) + " gwei"
    elif balance < 10**15:
    	balance = balance / 10**12
    	if len(str(balance)) > 8:
    		return "{0:.6f}".format(balance).rstrip('0').rstrip(".") + " szabo"
    	return str(balance) + " szabo"
    elif balance < 10**18:
    	balance = balance / 10**15
    	if len(str(balance)) > 8:
    		return "{0:.6f}".format(balance).rstrip('0').rstrip(".") + " finney"
    	return str(balance) + " finney"
    else:
    	balance = balance / 10**18
    	if len(str(balance)) > 8:
    		return "{0:.6f}".format(balance).rstrip('0').rstrip(".") + " poa"
    	return str(balance) + " poa"

def get_user_balance(private_key):
	account = web3.eth.account.privateKeyToAccount(private_key)
	balance = web3.eth.getBalance(account.address)
	print("Your balance is", convert(balance))

if sys.argv[1] == "--balance":
	pin_code = sys.argv[2]
	private_key = make_privet_key(ID, pin_code)
	get_user_balance(private_key)