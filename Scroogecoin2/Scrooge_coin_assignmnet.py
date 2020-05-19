import hashlib
import json
import pprint
from fastecdsa import ecdsa, keys, curve, point
import logging

class ScroogeCoin(object):
    def __init__(self):
        # MUST USE secp256k1 curve from fastecdsa
        self.private_key, self.public_key = keys.gen_keypair(curve.secp256k1)
        
        # create the address using public key, and bitwise operation, may need hex(value).hexdigest()
        self.address = hashlib.sha256(hex(self.public_key.x << 256 | self.public_key.y).encode()).hexdigest()
        
        # list of all the blocks
        self.chain = []
        
        # list of all the current transactions
        self.current_transactions = []

    def create_coins(self, receivers: dict):
        """
        Scrooge adds value to some coins
        :param receivers: {account:amount, account:amount, ...}
        """
        tx = {
            "sender": self.address,
            # coins that are created do not come from anywhere
            "location": {"block": -1, "tx": -1},
            "receivers": receivers,
        }
        tx["hash"] = self.hash(tx)
        tx["signature"] = self.sign(tx["hash"])
        self.current_transactions.append(tx)

    def hash(self, blob):
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        # use json.dumps().encode() and specify the corrent parameters=
        # use hashlib to hash the output of json.dumps()
        hash_object = hashlib.sha256(json.dumps(blob, sort_keys=True).encode())
        return hash_object.hexdigest()

    def sign(self, hash_):
        # use fastecdsa library
        r, s = ecdsa.sign(hash_, self.private_key, curve=curve.secp256k1)
        return (r,s)

    def get_user_tx_positions(self, address):
        """
        Scrooge adds value to some coins
        :param address: User.address
        :return: list of all transactions where address is funded
        [{"block":block_num, "tx":tx_num, "amount":amount}, ...]
        """
        funded_transactions = []

        for block in self.chain:
            tx_index = 0
            for old_tx in block["transactions"]:
                for funded, amount in old_tx["receivers"].items():
                    if(address == funded):
                        funded_transactions.append({"block": block["index"], "tx": tx_index, "amount": amount})
                tx_index += 1
        return funded_transactions

    def validate_tx(self, tx, public_key):
        """
        validates a single transaction

        :param tx = {
            "sender" : User.address,
                ## a list of locations of previous transactions
                ## look at
            "locations" : [{"block":block_num, "tx":tx_num, "amount":amount}, ...],
            "receivers" : {account:amount, account:amount, ...}
        }

        :param public_key: User.public_key

        :return: if tx is valid return tx
        """
        is_correct_hash = False
        base_tx = {
            "sender": tx["sender"],
            "location": tx["location"],
            "receivers": tx["receivers"],
        }
        if self.hash(base_tx) == tx["hash"]:
            is_correct_hash = True

        is_signed = ecdsa.verify(tx["signature"], tx["hash"], public_key, curve=curve.secp256k1)

        blockIndex = tx["location"]["block"]
        txIndex = tx["location"]["tx"]

        # what is the meaning of isFunded?
        is_funded = False
        list_of_transactions = self.chain[blockIndex]["transactions"]
        amount = 0
        if tx["sender"] in list_of_transactions[txIndex]["receivers"]:
            amount = list_of_transactions[txIndex]["receivers"][tx["sender"]]
            if amount >= 0:
                is_funded = True

        is_all_spent = False
        totalAmountSpent = 0
        for rec in tx["receivers"].keys():
            totalAmountSpent += tx["receivers"][rec]
        is_all_spent = True if totalAmountSpent == amount else False

        consumed_previous = False
        # for each block after blockIndex , need to verify if blockIndex and tx is not used as location
        for block in self.chain[blockIndex:]:
            for transaction in block["transactions"]:
                if transaction["sender"] == tx["sender"]:
                    if transaction["location"]["block"] == blockIndex and transaction["location"]["tx"] == txIndex:
                        consumed_previous = True


        if (is_correct_hash and is_signed and is_funded and is_all_spent and not consumed_previous):
            return tx
        else:
            return None

    def mine(self):
        """
        mines a new block onto the chain
        """
        previous_hash = None
        if len(self.chain) != 0:
            previous_hash = self.chain[len(self.chain) - 1]

        block = {
            'previous_hash': previous_hash,
            'index': len(self.chain),
            'transactions': self.current_transactions,
        }

        block["hash"] = self.hash(block)   # hash and sign the block
        block["signature"] = self.sign(block["hash"]) # signed hash of block
        self.chain.append(block)
        self.current_transactions = []
        return block

    def add_tx(self, tx, public_key):
        """
        checks that tx is valid
        adds tx to current_transactions

        :param tx = {
            "sender" : User.address,
                ## a list of locations of previous transactions
                ## look at
            "locations" : [{"block":block_num, "tx":tx_num, "amount":amount}, ...],
            "receivers" : {account:amount, account:amount, ...},
            "hash": "1233245353543",
            "signature": "ABCDEFHGISMSLDDJSKWOSMSSKSJDKFLMD"
        }

        :param public_key: User.public_key

        :return: True if the tx is added to current_transactions
        """
        tx = self.validate_tx(tx, public_key)
        if tx != None:
            self.current_transactions.append(tx)
            return True
        else:
            return False

    def show_user_balance(self, address):
        """
        prints balance of address
        :param address: User.address
        """
        totalBalance = 0
        for block in self.chain:
            for transaction in block["transactions"]:
                if transaction["sender"] == address:
                    for reciever, amount in transaction["receivers"].items():
                        if reciever != address:
                            totalBalance -= amount
                else:
                    for reciever, amount in transaction["receivers"].items():
                        if reciever == address:
                            totalBalance += amount
        print(totalBalance)
        return totalBalance


    def show_block(self, block_num):
        """
        prints out a single formated block
        :param block_num: index of the block to be printed
        """
        print(self.chain[block_num])

class User(object):
    def __init__(self, Scrooge):
        # MUST USE secp256k1 curve from fastecdsa
        self.private_key, self.public_key = keys.gen_keypair(curve.secp256k1)
        
        # create the address using public key, and bitwise operation, may need hex(value).hexdigest()
        self.address = hashlib.sha256(hex(self.public_key.x << 256 | self.public_key.y).encode()).hexdigest()
        

    def hash(self, blob):
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        :return: the hash of the blob
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        # use json.dumps().encode() and specify the corrent parameters
        # use hashlib to hash the output of json.dumps()
        hash_object = hashlib.sha256(json.dumps(blob, sort_keys=True).encode())
        value = hash_object.hexdigest()
        return value

    def sign(self, hash_):

        r, s = ecdsa.sign(hash_, self.private_key, curve=curve.secp256k1)
        return (r,s) # use fastecdsa library

    def send_tx(self, receivers, previous_tx_locations):
        """
        creates a TX to be sent
        :param receivers: {account:amount, account:amount, ...}
        :param previous_tx_locations
        """

        tx = {
                "sender": self.address,
                "location": previous_tx_locations[0],
                "receivers": receivers,
            }
        base_tx = tx
        # hash_value = self.hash(base_tx),
        # print(hash_value)
        hash_object = hashlib.sha256(json.dumps(base_tx, sort_keys=True).encode())
        hash_value = hash_object.hexdigest()
        signature = self.sign(hash_value)
        tx["hash"] = hash_value  # hash of TX
        tx["signature"] = signature  # signed hash of TX
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
    print("##### Executing Main #####")
    Scrooge = ScroogeCoin()
    users = [User(Scrooge) for i in range(10)]
    Scrooge.create_coins({users[0].address: 10, users[1].address: 20, users[3].address: 50})
    Scrooge.mine()

    user_0_tx_locations = Scrooge.get_user_tx_positions(users[0].address)
    first_tx = users[0].send_tx({users[1].address: 2, users[0].address:8}, user_0_tx_locations)
    print(Scrooge.add_tx(first_tx, users[0].public_key))
    Scrooge.mine()

    second_tx = users[1].send_tx({users[0].address:20}, Scrooge.get_user_tx_positions(users[1].address))
    print(Scrooge.add_tx(second_tx, users[1].public_key))
    Scrooge.mine()

    Scrooge.get_user_tx_positions(users[1].address)
    Scrooge.get_user_tx_positions(users[0].address)

    Scrooge.show_user_balance(users[0].address)
    Scrooge.show_user_balance(users[1].address)
    Scrooge.show_user_balance(users[3].address)

    test_1()
    test_2()
    test_3()
    test_4()


def test_1():

    print("TestCase 1: #### Mine a valid transaction that consumes coins from a previous block")
    log = logging.getLogger('test_1')
    log.info("hello")
    Scrooge = ScroogeCoin()
    users = [User(Scrooge) for i in range(10)]
    Scrooge.create_coins({users[0].address: 10, users[1].address: 10, users[2].address: 10})
    Scrooge.mine()

    Scrooge.create_coins({users[3].address: 10, users[4].address: 10, users[5].address: 10})
    Scrooge.mine()
    user_5_tx_locations = Scrooge.get_user_tx_positions(users[5].address)
    first_tx = users[5].send_tx({users[6].address: 10}, user_5_tx_locations)
    Scrooge.add_tx(first_tx, users[5].public_key)
    Scrooge.mine()
    assert Scrooge.show_user_balance(users[5].address) == 0
    assert Scrooge.show_user_balance(users[6].address) == 10
    print("#### Passed TestCase_1 #### \n\n")


def test_2():

    print("TestCase 2:#### Create all invalid scenarios and show the error message.")
    # Invalid scenario 1 - is_correct_hash = false
    Scrooge = ScroogeCoin()
    users = [User(Scrooge) for i in range(10)]
    Scrooge.create_coins({users[0].address: 10, users[1].address: 10, users[2].address: 10})
    Scrooge.mine()

    user_0_tx_locations = Scrooge.get_user_tx_positions(users[0].address)
    tx = users[0].send_tx({users[1].address: 10}, user_0_tx_locations)
    hash = tx["hash"]
    tx["hash"] = "1234"
    assert Scrooge.add_tx(tx, users[0].public_key) == False

    # Invalid Scenario 2 - isSigned = false
    tx["hash"] = hash
    signature = tx["signature"]
    tx["signature"] = (1234, 12345)

    assert Scrooge.add_tx(tx, users[0].public_key) == False
    tx["signature"] = signature

    # Invalid Scenario 3 - isAllSpent
    tx = users[0].send_tx({users[1].address: 5}, user_0_tx_locations)
    assert Scrooge.add_tx(tx, users[0].public_key) == False

    # Invalid scenario 4 - consumed previous
    tx = users[0].send_tx({users[1].address: 10}, user_0_tx_locations)
    Scrooge.add_tx(tx, users[0].public_key)
    Scrooge.mine()
    tx = users[0].send_tx({users[2].address: 10}, user_0_tx_locations)
    assert Scrooge.add_tx(tx, users[0].public_key) == False
    print("#### Passed TestCase_2 #### \n\n")


def test_3():

    print("TestCase 3: #### Print a couple users balance before and after a transaction occurs between them.")
    Scrooge = ScroogeCoin()
    users = [User(Scrooge) for i in range(10)]
    Scrooge.create_coins({users[0].address: 10, users[1].address: 10, users[2].address: 10})
    Scrooge.mine()

    Scrooge.show_user_balance(users[0].address)
    Scrooge.show_user_balance(users[1].address)
    Scrooge.show_user_balance(users[2].address)

    # Transferring 10 coins from Users[0] to Users[1]
    user_0_tx_locations = Scrooge.get_user_tx_positions(users[0].address)
    tx = users[0].send_tx({users[1].address: 10}, user_0_tx_locations)
    Scrooge.add_tx(tx, users[0].public_key)
    Scrooge.mine()

    assert Scrooge.show_user_balance(users[0].address) == 0
    assert Scrooge.show_user_balance(users[1].address) == 20
    assert Scrooge.show_user_balance(users[2].address) == 10
    print("#### Passed TestCase_3 #### \n\n")


def test_4():

    print("TestCase 4: #### # print a block ")
    Scrooge = ScroogeCoin()
    users = [User(Scrooge) for i in range(10)]
    Scrooge.create_coins({users[0].address: 10, users[1].address: 10, users[2].address: 10})
    Scrooge.mine()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(Scrooge.chain)
    print("#### Passed TestCase_4 ####\n\n")




if __name__ == '__main__':
   main()

