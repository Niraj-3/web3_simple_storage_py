from dis import Bytecode
import json
from solcx import compile_standard,install_solc
from web3 import Web3
import os
from dotenv import load_dotenv;
load_dotenv()



with open("./SimpleStorage.sol","r") as file:
    simple_storage_file = file.read();


print("Installing...")#solcx is a compiler
install_solc("0.6.0")

compiled_sol = compile_standard(
    {
        "language":"Solidity",
        "sources":{"SimpleStorage.sol":{"content":simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        }
    }, 
    solc_version="0.6.0"
)

with open("compiled_code.json","w") as file:
    json.dump(compiled_sol,file);


bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]


#For connecting to ganache;
w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/5bf3d480c7f74e24959aa45709b5abc8"))

chain_id = 4
my_address = "0x67E60fcEEF117236b2419957445eCCDDf34569A2"
private_key = os.getenv("PRIVATE_KEY")

#Creating the contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

#Get the latest transaction;
nonce = w3.eth.getTransactionCount(my_address)

#build the transaction;
transaction = SimpleStorage.constructor().buildTransaction({
    "chainId": chain_id,
    "gasPrice": w3.eth.gas_price,
    "from": my_address,
    "nonce": nonce,
})


#sign the transaction;
signed_txn = w3.eth.account.sign_transaction(transaction,private_key=private_key)
print("Deploying Contract!")

#Send the transaction
txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# Wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
print(f"Done! Contract deployed to {txn_receipt.contractAddress}")




#Working with deployed contract.
simple_storage = w3.eth.contract(address=txn_receipt.contractAddress, abi=abi)
print(f"Initial Stored Value {simple_storage.functions.retrieve().call()}")
greeting_transaction = simple_storage.functions.store(25).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_greeting_txn = w3.eth.account.sign_transaction(
    greeting_transaction, private_key=private_key
)
txn_greeting_hash = w3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
print("Updating stored Value...")
tx_receipt = w3.eth.wait_for_transaction_receipt(txn_greeting_hash)

print(simple_storage.functions.retrieve().call())