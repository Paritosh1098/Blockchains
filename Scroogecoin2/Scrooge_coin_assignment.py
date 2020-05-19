import hashlib
import json
from fastecdsa import ecdsa, keys, curve, point

class ScroogeCoin(object):
    def __init__(self):
        self.private_key, self.public_key = # MUST USE secp256k1 curve from fastecdsa
        self.address = # create the address using public key, and bitwise operation, may need hex(value).hexdigest()
        self.chain = [] # list of all the blocks
        self.current_transactions = [] # list of all the current transactions

    


    """
    The function takes a list of input addresses and amount of coins. 
    It will create a transaction that creates coins and adds it to the transaction list which will be later mined. 
    The transaction should be hashed and signed by Scrooge.
    """
    def create_coins(self, receivers: dict):
        """
        Scrooge adds value to some coins
        :param receivers: {account:amount, account:amount, ...}
        """

        tx = {
            "sender" : # address,
            # coins that are created do not come from anywhere
            "locations": {"block": -1, "tx": -1, "amount":-1},
            "receivers" : receivers,
        }
        tx["hash"] = # hash of tx
        tx["signature"] = # signed hash of tx

        self.current_transactions.append(tx)

    



    def hash(self, blob):
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        # use json.dumps().encode() and specify the corrent parameters
        # use hashlib to hash the output of json.dumps()
        return # hash_of_blob

    

    """
        Sign function that signs the input which is usually hash of a block or transaction.
    """
    def sign(self, hash_):
        return # use fastecdsa library

    




    """
    Add the submitted transaction by a user to your transaction list if the transaction is valid.
    """
    def add_tx(self, tx, public_key):
         """
        checks that tx is valid
        adds tx to current_transactions

        :param tx = {
            "sender" : User.address,
                ## a list of locations of previous transactions
                ## look at 
            "locations" : [{"block":block_num, "tx":tx_num, "amount":amount}, ...], 
            "receivers" : {account:amount, account:amount, ...}
        }

        :param public_key: User.public_key

        :return: True if the tx is added to current_transactions
        """


class User(object):
    def __init__(self):
        self.private_key, self.public_key = # MUST USE secp256k1 curve from fastecdsa
        self.address = # create the address using public key, and bitwise operation, may need hex(value).hexdigest()

    def hash(self, blob):
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        :return: the hash of the blob
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        # use json.dumps().encode() and specify the corrent parameters
        # use hashlib to hash the output of json.dumps()
        return # hash_of_blob

    def sign(self, hash_):
        return # use fastecdsa library

    def send_tx(self, receivers, previous_tx_locations):
        """
        creates a TX to be sent
        :param receivers: {account:amount, account:amount, ...}
        :param previous_tx_locations 
        """

        tx = {
                "sender" : # address,
                "locations" : previous_tx_locations,
                "receivers" : receivers 
            }

        tx["hash"] = # hash of TX
        tx["signature"] = # signed hash of TX

        return tx



def main():

    # dict - defined using {key:value, key:value, ...} or dict[key] = value
        # they are used in this code for blocks, transactions, and receivers
        # can be interated through using dict.items()
        # https://docs.python.org/3/tutorial/datastructures.html#dictionaries

    # lists -defined using [item, item, item] or list.append(item) as well as other ways
        # used to hold lists of blocks aka the blockchain
        # https://docs.python.org/3/tutorial/datastructures.html#more-on-lists

    # fastecdsa - https://pypi.org/project/fastecdsa/
    # hashlib - https://docs.python.org/3/library/hashlib.html
    # json - https://docs.python.org/3/library/json.html

    # Example of how the code will be run
    Scrooge = ScroogeCoin()
    users = [User() for i in range(10)]
    Scrooge.create_coins({users[0].address:10, users[1].address:20, users[3].address:50})

    

if __name__ == '__main__':
   main()
    