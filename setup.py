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
		abi = loads(abi_file.read())
	with open("registrar.bin") as bin_file:
		bytecode = bin_file.read()
	contract = web3.eth.contract(abi = abi, bytecode = bytecode)
	headers = {"accept": "application/json"}
	try:
		data = requests.get(gas_url, headers)
	except:
		gas_price = defaul_price
	else:
		gas_price = int(data.json()["fast"] * 10**9)
	if balance < gas_price * 70000:
		print("No enough funds to send transaction")
		return
	tx_con = contract.constructor().buildTransaction({
			"from": account.address,
			 "nonce": web3.eth.getTransactionCount(account.address),
			 "gas": 300000,
			 "gasPrice": gas_price 
			 })
	signed = account.signTransaction(tx_con)
	tx_hash = web3.eth.sendRawTransaction(signed.rawTransaction)
	tx = web3.eth.waitForTransactionReceipt(tx_hash)
	if tx["blockNumber"] is None:
		print("Transaction is not validated too long")
		return
	with open("registrar.json", "w") as registrar:
		dump({"registrar": {"address": tx["contractAddress"], "startBlock": tx["blockNumber"]}}, registrar)
	print("KYC Resistrar:", account.address)
	print("Payment Handler:", tx["contractAddress"])


if sys.argv[1] == "--deploy":
	deploy(private_key)