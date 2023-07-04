from web3 import Web3
import json

ganache_url = "http://127.0.0.1:7545"
registeredInstitutes = {"MIT": 1, "VJTI": 2, "IITB": 3}

class Blockchain:
    def __init__(self, institute):
        self.web3 = Web3(Web3.HTTPProvider(ganache_url))
        self.institute = institute

        with open('contractDetails.json') as f:
            contractDetails = json.load(f)
            contractAddress = self.web3.toChecksumAddress(contractDetails["address"])
            abi = contractDetails["abi"]
        
        self.contract = self.web3.eth.contract(address=contractAddress, abi=abi)

        if institute in registeredInstitutes.keys():
            self.web3.eth.defaultAccount = self.web3.eth.accounts[registeredInstitutes[institute]]
            print("Connected to blockchain with account: ", institute)
        else:
            self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
            print("Connected to blockchain with default account")
    
    def addBatchMerkleRoot(self, batch, batchMerkleRoot):
        self.contract.functions.addBatchMerkleRoot(self.institute, batch, batchMerkleRoot).transact()
    
    def verifyBatchMerkleRoot(self, institute, batch, batchMerkleRoot):
        return self.contract.functions.verifyBatchMerkleRoot(institute, batch, batchMerkleRoot).call()

if __name__ == "__main__":
    bc = Blockchain("MIT")
    res = bc.verifyBatchMerkleRoot("MIT", "2019", "0x05D979462b2158Ad5506B39a2Dc4f0954612d167")
    print(res)
