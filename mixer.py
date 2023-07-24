import os
from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware
from solcx import compile_source
from solcx import install_solc

install_solc('0.8.0')

INFURA_API_KEY = os.getenv('INFURA_API_KEY')  # Use environment variables for sensitive information
MIXER_ACCOUNTS = os.getenv('MIXER_ACCOUNTS').split(',')  # Assuming the accounts are stored as a comma separated string in an environment variable
MIXER_PRIVATE_KEYS = os.getenv('MIXER_PRIVATE_KEYS').split(',')  # Same for the private keys

# Connect to the Ethereum node
w3 = Web3(Web3.HTTPProvider(f'https://rinkeby.infura.io/v3/{INFURA_API_KEY}'))

# Final recipient
FINAL_RECIPIENT = '0xFinalRecipientAddress'  # Should be a real address

# Number of intermediate wallets and transactions
NUM_INTERMEDIATE_WALLETS = 15
NUM_TRANSACTIONS = 7

# Contract compilation
CONTRACT_SOURCE_CODE = '''
pragma solidity ^0.8.0;

contract Mixer {
    event Deposit(address indexed from, uint256 amount);
    event Withdrawal(address indexed to, uint256 amount);

    mapping(address => uint256) public balances;
    address[] public mixerAccounts;

    constructor(address[] memory _mixerAccounts) {
        mixerAccounts = _mixerAccounts;
        for (uint256 i = 0; i < mixerAccounts.length; i++) {
            balances[mixerAccounts[i]] = 0;
        }
    }

    function deposit() external payable {
        require(msg.value > 0, "Invalid amount");
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    function withdraw(address payable recipient, uint256 amount) external {
        require(amount > 0 && amount <= balances[msg.sender], "Insufficient balance");
        balances[msg.sender] -= amount;
        recipient.transfer(amount);
        emit Withdrawal(recipient, amount);
    }
}
'''

def compile_contract():
    compiled_contract = compile_source(CONTRACT_SOURCE_CODE)
    contract_interface = compiled_contract['<stdin>:Mixer']
    return contract_interface

def deploy_contract(contract_interface):
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    transaction = {
        'from': MIXER_ACCOUNTS[0],
        'nonce': w3.eth.get_transaction_count(MIXER_ACCOUNTS[0]),
        'gasPrice': w3.toWei('10', 'gwei'),
        'gas': 2000000,
        'data': contract.constructor(MIXER_ACCOUNTS).data_in_transaction
    }
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=MIXER_PRIVATE_KEYS[0])
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt['contractAddress']
    return contract_address


def mix_funds(contract_address, contract_interface):
    contract = w3.eth.contract(address=contract_address, abi=contract_interface['abi'])
    total_amount = 1_000_000_000  # 1 ETH (10^18 wei)
    amount_per_transaction = total_amount // (NUM_INTERMEDIATE_WALLETS * NUM_TRANSACTIONS)

    for _ in range(NUM_TRANSACTIONS):
        for i in range(NUM_INTERMEDIATE_WALLETS):
            sender_index = i % len(MIXER_ACCOUNTS)
            receiver_index = (i + 1) % len(MIXER_ACCOUNTS)

            sender_account = MIXER_ACCOUNTS[sender_index]
            sender_private_key = MIXER_PRIVATE_KEYS[sender_index]
            receiver_account = MIXER_ACCOUNTS[receiver_index]

            nonce = w3.eth.get_transaction_count(sender_account)
            gas_price = w3.toWei('10', 'gwei')
            gas_limit = 21000

            amount_to_send = amount_per_transaction

            deposit_tx = contract.functions.deposit().buildTransaction({
                'from': sender_account,
                'value': amount_to_send,
                'nonce': nonce,
                'gasPrice': gas_price,
                'gas': gas_limit
            })
            signed_deposit_tx = w3.eth.account.sign_transaction(deposit_tx, private_key=sender_private_key)
            w3.eth.send_raw_transaction(signed_deposit_tx.rawTransaction)

            withdraw_tx = contract.functions.withdraw(MIXER_ACCOUNTS[receiver_index], amount_to_send).buildTransaction({
                'from': sender_account,
                'nonce': nonce + 1,
                'gasPrice': gas_price,
                'gas': gas_limit
            })
            signed_withdraw_tx = w3.eth.account.sign_transaction(withdraw_tx, private_key=sender_private_key)
            w3.eth.send_raw_transaction(signed_withdraw_tx.rawTransaction)

    final_recipient_nonce = w3.eth.get_transaction_count(FINAL_RECIPIENT)
    withdraw_tx = contract.functions.withdraw(FINAL_RECIPIENT, total_amount).buildTransaction({
        'from': MIXER_ACCOUNTS[0],
        'nonce': final_recipient_nonce,
        'gasPrice': gas_price,
        'gas': gas_limit
    })
    signed_withdraw_tx = w3.eth.account.sign_transaction(withdraw_tx, private_key=MIXER_PRIVATE_KEYS[0])
    w3.eth.send_raw_transaction(signed_withdraw_tx.rawTransaction)

def main():
    # Use middleware for Rinkeby network
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Compile the contract
    contract_interface = compile_contract()

    # Deploy the contract
    try:
        contract_address = deploy_contract(contract_interface)
        print("Contract deployed at address:", contract_address)

        # Mix the funds
        mix_funds(contract_address, contract_interface)
    except Exception as e:
        print("An error occurred during the mixing process:", str(e))

if __name__ == "__main__":
    main()
