#!/usr/bin/env python

from web3 import Web3, HTTPProvider
from json import dump, loads, load
import requests
import sys

with open("network.json") as network:
	data = load(network)
	url = data["rpcUrl"]
	gas_url = data["gasPriceUrl"]
	private_key = data["privKey"]
	defaul_price = data["defaultGasPrice"]

web3 = Web3(HTTPProvider(url))

account = web3.eth.account.privateKeyToAccount(private_key)


def deploy(private_key):
	balance = web3.eth.getBalance(account.address)
	with open("registrar.abi") as abi_file:
		reg_abi = loads(abi_file.read())
	with open("registrar.bin") as bin_file:
		reg_bytecode = bin_file.read()
	with open("payments.abi") as abi_file:
		pay_abi = loads(abi_file.read())
	with open("payments.bin") as bin_file:
		pay_bytecode = bin_file.read()
	contract_reg = web3.eth.contract(abi = reg_abi, bytecode = reg_bytecode)
	contract_pay = web3.eth.contract(abi = pay_abi, bytecode = pay_bytecode)
	headers = {"accept": "application/json"}
	try:
		data = requests.get(gas_url, headers)
	except:
		gas_price = defaul_price
	else:
		gas_price = int(data.json()["fast"] * 10**9)
	if balance < gas_price * 4000000:
		print("No enough funds to send transaction")
		return
	tx_reg = contract_reg.constructor().buildTransaction({
			"from": account.address,
			 "nonce": web3.eth.getTransactionCount(account.address),
			 "gas": 4000000,
			 "gasPrice": gas_price 
			 })
	signed = account.signTransaction(tx_reg)
	tx_hash_reg = web3.eth.sendRawTransaction(signed.rawTransaction)
	tx_r = web3.eth.waitForTransactionReceipt(tx_hash_reg)
	if tx_r["blockNumber"] is None:
		print("Transaction is not validated too long")
		return
	if balance < gas_price * 400000:
		print("No enough funds to send transaction")
		return
	tx_pay = contract_reg.constructor().buildTransaction({
			"from": account.address,
			 "nonce": web3.eth.getTransactionCount(account.address),
			 "gas": 4000000,
			 "gasPrice": gas_price 
			 })
	signed = account.signTransaction(tx_pay)
	tx_hash_pay = web3.eth.sendRawTransaction(signed.rawTransaction)
	tx_p = web3.eth.waitForTransactionReceipt(tx_hash_pay)
	if tx_p["blockNumber"] is None:
		print("Transaction is not validated too long")
		return
	with open("registrar.json", "w") as registrar:
		dump({"registrar": {"address": tx_r["contractAddress"], "startBlock": tx_r["blockNumber"]}, "payments": {"address": tx_p["contractAddress"], "startBlock": tx_p["blockNumber"]}}, registrar)
	print("KYC Resistrar:", tx_r["contractAddress"])
	print("Payment Handler:", tx_p["contractAddress"])

def contract_owner(contract_name):
	if contract_name == "registrar":
		with open("registrar.abi") as abi_file:
			reg_abi = loads(abi_file.read())
		with open("registrar.bin") as bin_file:
			reg_bytecode = bin_file.read()
		with open("registrar.json") as registrar:
			data = loads(registrar.read())
			reg_address = data["registrar"]["address"]
		contract_reg = web3.eth.contract(address = reg_address, abi = reg_abi)
		owner = contract_reg.functions.owner().call()
		print("Admin account:", owner)

def change_owner(contract_name, address):
	if contract_name == "registrar":
		with open("registrar.abi") as abi_file:
			reg_abi = loads(abi_file.read())
		with open("registrar.bin") as bin_file:
			reg_bytecode = bin_file.read()
		with open("registrar.json") as registrar:
			data = loads(registrar.read())
			reg_address = data["registrar"]["address"]
		contract_reg = web3.eth.contract(address = reg_address, abi = reg_abi)
		headers = {"accept": "application/json"}
		try:
			data = requests.get(gas_url, headers)
		except:
			gas_price = defaul_price
		else:
			gas_price = int(data.json()["fast"] * 10**9)
			if web3.eth.getBalance(account.address) < gas_price * 70000:
				print("No enough funds to send transaction")
				return
			elif contract_reg.functions.owner().call() != account.address:
				print("Request cannot be executed")
				return
		tx_chan = contract_reg.functions.change_con_owner(address).buildTransaction({
			"from": account.address,
			"nonce": web3.eth.getTransactionCount(account.address),
			"gas": 100000,
			"gasPrice": gas_price
			})
		signed_tx_chan = account.signTransaction(tx_chan)
		tx_chan_id = web3.eth.sendRawTransaction(signed_tx_chan.rawTransaction)
		tx_chan_receipt = web3.eth.waitForTransactionReceipt(tx_chan_id) 
		print("New admin account:", address)


if sys.argv[1] == "--deploy":
	deploy(private_key)
elif sys.argv[1] == "--owner":
	contract_name = sys.argv[2]
	contract_owner(contract_name)
elif sys.argv[1] == "--chown":
	contract_name = sys.argv[2]
	new_owner = sys.argv[3]
	change_owner(contract_name, new_owner)