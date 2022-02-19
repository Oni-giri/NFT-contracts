from utils.sha_utils import sign_message
from web3 import Web3
import csv
import json

def main():
    
    def sign(_address, _amount, _price):
        message_hash = Web3.solidityKeccak(["address", "uint256", "uint256"],
                    [_address, _amount, _price])
        message_signed = sign_message(message_hash.hex(), signer[0])
        return message_signed.signature.hex()

    signer = ["0x9a68219f2043f84c6f53585a25ada91cbd5f24727912942a3a05a7981185a44c",
                "0x66666666f823add319d99db0deb95cbaf762b693"]

    max_amount = 5
    price = 10
    results = []

    with open('./scripts/whitelist_address.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for line in csv_reader:
            address =  line[0]
            signature = sign(address, max_amount, price)
            results.append({"address":address, "signature":signature})
        csv_file.close()
        results = json.dumps(results)

    with open("./scripts/whitelisted_signatures", "w") as signatures_file:
        signatures_file.write(results)
