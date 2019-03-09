#!/usr/bin/env python

from web3 import Web3, HTTPProvider
from json import loads
import sys
import requests


web3 = Web3(HTTPProvider("https://sokol.poa.network"))

def get_list(key):
	try:
		with open("registrar.json") as registrar:
			reg_address = loads(registrar.read())["registrar"]["address"]
	except:
		print("No contract address")
		return
	with open("registrar.abi") as abi_file:
		reg_abi = loads(abi_file.read())
	contract_reg = web3.eth.contract(address = reg_address, abi = reg_abi)
	try:
		contract_reg.functions.owner().call()
	except:
		print("Seems that the contract address is not the registrar contract")
		return
	if key == "add":
		add_list = contract_reg.functions.get_list_add().call()
		if len(add_list) == 0 or len(add_list) == add_list.count("0x0000000000000000000000000000000000000000"):
			print("No KYC registration requests found")
			return
		for address in add_list:
			if address == "0x0000000000000000000000000000000000000000":
				continue
			print("{}: {}".format(address, contract_reg.functions.pending_add(address).call()))
	else:
		del_list = contract_reg.functions.get_list_del().call()
		if len(del_list) == 0 or len(del_list) == del_list.count("0x0000000000000000000000000000000000000000"):
			print("No KYC unregistration requests found")
			return
		for address in del_list:
			if address == "0x0000000000000000000000000000000000000000":
				continue
			print("{}: {}".format(address, contract_reg.functions.pending_del(address).call()))

def confirm_ac(user_address):
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
		data = loads(network.read())
		default_price = data["defaultGasPrice"]
		gas_url = data["gasPriceUrl"]
		try:
			private_key = data["privKey"]
		except:
			print("No admin account found")
			return
	headers = {"accept": "application/json"}
	data = requests.get(gas_url, headers)
	if data.status_code != 200:
		gas_price = default_price
	else:
		gas_price = int(data.json()["fast"] * 10**9)
	account = web3.eth.account.privateKeyToAccount(private_key)
	if web3.eth.getBalance(account.address) < gas_price:
		print("No funds to send the request")
		return
	contract_reg = web3.eth.contract(address = reg_address, abi = reg_abi)
	try:
		contract_reg.functions.owner().call()
	except:
		print("Seems that the contract address is not the registrar contract")
		return
	if contract_reg.functions.confirmed_users(user_address).call() != "" and contract_reg.functions.pending_del(user_address).call() == "":
		print(contract_reg.functions.confirmed_users(user_address).call(), contract_reg.functions.pending_del(user_address).call())
		print("Such phone number already registered")
		return
	tx_conf = contract_reg.functions.confirm_act(user_address, account.address).buildTransaction({
		"from": account.address,
		"nonce": web3.eth.getTransactionCount(account.address),
		"gas": 100000,
		"gasPrice": gas_price
		})
	signed_conf = account.signTransaction(tx_conf)
	tx_conf_id = web3.eth.sendRawTransaction(signed_conf.rawTransaction)
	tx_conf_rec = web3.eth.waitForTransactionReceipt(tx_conf_id)
	if contract_reg.functions.pending_add(user_address) == "" or contract_reg.functions.pending_del(user_address) == "":
		print("Failed but included in", tx_conf_rec["transactionHash"].hex())
	else:
		print("Confirmed by", tx_conf_rec["transactionHash"].hex())

def get_account(phone_number):
	try:
		with open("registrar.json") as registrar:
			reg_address = loads(registrar.read())["registrar"]["address"]
	except:
		print("No contract address")
	with open("registrar.abi") as abi_file:
		reg_abi = loads(abi_file.read())
	contract_reg = web3.eth.contract(address = reg_address, abi = reg_abi)
	try:
		contract_reg.functions.owner().call()
	except:
		print("Seems that the contract address is not the registrar contract")
		return
	if contract_reg.functions.confirmed_users_by_number(phone_number).call() == "0x0000000000000000000000000000000000000000":
		print("Corresponde not found")
		return
	print("Registered corresponde: ", contract_reg.functions.confirmed_users_by_number(phone_number).call())



if sys.argv[1] == "--list":
	key = sys.argv[2]
	get_list(key)
elif sys.argv[1] == "--confirm":
	user_address = sys.argv[2]
	confirm_ac(user_address)
elif sys.argv[1] == "--get":
	phone_number = sys.argv[2]
	get_account(phone_number)