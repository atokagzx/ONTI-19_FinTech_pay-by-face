#!/usr/bin/env python

from web3 import Web3, HTTPProvider
from sha3 import keccak_256
from json import load, loads
import sys
import cognitive_face as cf


web3 = Web3(HTTPProvider("https://sokol.poa.network"))

with open("network.json") as network:
	default_price = loads(network.read())["defaultGasPrice"]

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
	if balance == 0:
		return str(balance) + " poa"
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

def add(pin_code, phone_number):
	if phone_number[0] != "+" or len(phone_number) != 12 or phone_number.lower().islower():
		print("Incorrect phone number")
		return
	try:
		with open("person.json") as person:
			person_id = loads(person.read())["id"].split("-")
	except:
		print("ID is not found")
		return
	try:
		with open("registrar.json") as registrar:
			reg_address = loads(registrar.read())["registrar"]["address"]
	except:
		print("No contract address")
		return
	with open("registrar.abi") as abi_file:
		reg_abi = loads(abi_file.read())
	with open("network.json") as network:
		default_price = loads(network.read())["defaultGasPrice"]
	private_key = make_privet_key(person_id, pin_code)
	account = web3.eth.account.privateKeyToAccount(private_key)
	contract_reg = web3.eth.contract(address = reg_address, abi = reg_abi)
	try:
		contract_reg.functions.owner().call()
	except:
		print("Seems that the contract address is not registrar contract")
		return
	else:
		headers = {"accept": "application/json"}
		try:
			data = requests.get(gas_url, headers)
		except:
			gas_price = default_price
		else:
			gas_price = int(data.json()["fast"] * 10**9)
		if web3.eth.getBalance(account.address) < gas_price * 70000:
			print("No funds to send the request")
			return
		tx_add = contract_reg.functions.add_user(int(phone_number), account.address).buildTransaction({
			"from": account.address,
			"nonce": web3.eth.getTransactionCount(account.address),
			"gas": 100000,
			"gasPrice": gas_price
			})
		signed_tx_add = account.signTransaction(tx_add)
		try:
			tx_add_id = web3.eth.sendRawTransaction(signed_tx_add.rawTransaction)
		except:
			print("Registration request already sent")
			return
		tx_add_rec = web3.eth.waitForTransactionReceipt(tx_add_id)
		print("Registration request sent by", tx_add_rec["transactionHash"].hex())

def delete(pin_code):
	with open("person.json") as person:
		person_id = loads(person.read())["personId"].split("-")
	with open("registrar.json") as registrar:
		reg_address = load(registrar.read())["registrar"]["address"]
	with open("registrar.abi") as abi_file:
		reg_abi = loads(abi_file.read())
	private_key = make_privet_key(person_id, pin_code)
	account = web3.eth.account.privateKeyToAccount(private_key)
	contract_reg = web3.eth.contract(address = reg_address, abi = reg_abi)
	try:
		contract_reg.functions.users_by_address(account.address).call()
	except:
		print("Account does not exsist")
	else:
		tx_del = contract_reg.functions.delete_user(account.address).buildTransaction({
			"from": account.address,
			"nonce": web3.eth.getTransactionCount(account.address),
			"gas": 100000,
			"gasPrice": gas_price
			})
		signed_tx_del = account.signTransaction(tx_del)
		tx_del_id = web3.eth.sendRawTransaction(signed_tx_del.rawTransaction)
		tx_del_rec = web3.eth.waitForTransactionReceipt(tx_del_id)
		print("Succesfully deleted by", tx_del_rec["transactionHash"].hex())

def send_coins(pin_code, phone_number, value):
	with open("person.json") as person:
		person_id = loads(person.read())["personId"]
	with open("registrar.json") as registrar:
		reg_address = loads(registrar.read())["registrar"]["address"]
	with open("registrar.abi") as abi_file:
		reg_abi = loads(abi_file.read())
	private_key = make_privet_key(pin_code, person_id)
	account = web3.eth.account.privateKeyToAccount(private_key)
	if phone_number[0] != "+" or len(phone_number) != 12 or phone_number.lower().islower():
		print("Incorrect phone number")
		return
	elif web3.eth.getBalance(account.address) < int(value):
		print("No funds to send the payment")
		return
	else:
		contract_reg = web3.eth.contract(address = reg_address, abi = reg_abi)
		try:
			contract_reg.functions.users_by_number(int(phone_number[1:])).call()
		except:
			print("No account with the phone number", phone_number)
		else:
			receiver = contract_reg.functions.users_by_number(int(phone_number[1:])).call()
			gas = web3.eth.estimateGas({"to" : receiver, "value" : int(value)})
			nonce = web3.eth.getTransactionCount(account.address)
			headers = {"accept": "application/json"}
			try:
				data = requests.get(gas_url, headers)
			except:
				gas_price = default_price
			else:
				gas_price = int(data.json()["fast"] * 10**9)
			tx_s = {"to" : receiver, "value" : int(value), "gas" : gas, "gasPrice" : gas_price, "nonce" : nonce}
			signed = web3.eth.account.signTransaction(tx_s, sender)
			tx_r = web3.eth.sendRawTransaction(signed.rawTransaction)
			print("""Payment of {} to {} scheduled""".format(convert(int(value)), phone_number))
			print("Transaction Hash: {}".format(tx_r.hex()))



if sys.argv[1] == "--balance":
	try:
		with open("person.json") as person:
			data = load(person)
			ID = data["id"].split("-")
	except:
		print("ID is not found")
	else:
		pin_code = sys.argv[2]
		private_key = make_privet_key(ID, pin_code)
		get_user_balance(private_key)
elif sys.argv[1] == "--add":
	pin_code = sys.argv[2]
	phone_number = sys.argv[3]
	add(pin_code, phone_number)