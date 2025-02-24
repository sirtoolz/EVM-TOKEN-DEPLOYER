import os
import sys
import getpass
from colorama import init, Fore, Style
from web3 import Web3
from solcx import compile_standard, install_solc

# Initialize colorama for cross-platform colored output
init()

# Colorful branding
BRANDING = f"""
{Fore.RED}╔════════════════════════════════════╗{Style.RESET_ALL}
{Fore.YELLOW}║   Made with {Fore.RED}♥{Fore.YELLOW} by SIRTOOLZ   ║{Style.RESET_ALL}
{Fore.GREEN}╚════════════════════════════════════╝{Style.RESET_ALL}
"""

# Simple ERC20 contract source code
CONTRACT_SOURCE = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract ERC20 {
    string public name;
    string public symbol;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    constructor(string memory _name, string memory _symbol, uint256 _supply) {
        name = _name;
        symbol = _symbol;
        totalSupply = _supply * 10**18;
        balanceOf[msg.sender] = totalSupply;
    }
}
"""

def setup_dependencies():
    """Install necessary Python packages and Solidity compiler."""
    try:
        print(f"{Fore.CYAN}Installing dependencies...{Style.RESET_ALL}")
        os.system("pip install web3 py-solc-x colorama")
        install_solc("0.8.0")
        print(f"{Fore.GREEN}Dependencies installed successfully!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error installing dependencies: {e}{Style.RESET_ALL}")
        sys.exit(1)

def get_user_inputs():
    """Collect user inputs for deployment, masking the private key."""
    print(BRANDING)
    try:
        # Mask private key input using getpass
        private_key = getpass.getpass(f"{Fore.YELLOW}Enter your private key (input will be hidden): {Style.RESET_ALL}")
        token_name = input(f"{Fore.YELLOW}Token name: {Style.RESET_ALL}")
        token_symbol = input(f"{Fore.YELLOW}Token symbol: {Style.RESET_ALL}")
        token_supply = int(input(f"{Fore.YELLOW}Token supply: {Style.RESET_ALL}"))
        network = input(f"{Fore.YELLOW}Mainnet or Testnet? (m/t): {Style.RESET_ALL}").lower()
        rpc_url = input(f"{Fore.YELLOW}Chain RPC URL: {Style.RESET_ALL}")
        return private_key, token_name, token_symbol, token_supply, network, rpc_url
    except ValueError:
        print(f"{Fore.RED}Invalid input for token supply. Please enter a number.{Style.RESET_ALL}")
        sys.exit(1)

def deploy_contract(private_key, token_name, token_symbol, token_supply, network, rpc_url):
    """Deploy the ERC20 contract to the specified network."""
    # Connect to the blockchain
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"{Fore.RED}Failed to connect to RPC: {rpc_url}{Style.RESET_ALL}")
        sys.exit(1)

    # Enable unaudited features and get account
    w3.eth.account.enable_unaudited_hdwallet_features()
    try:
        account = w3.eth.account.from_key(private_key)
    except Exception as e:
        print(f"{Fore.RED}Invalid private key: {e}{Style.RESET_ALL}")
        sys.exit(1)

    # Compile the contract
    compiled = compile_standard({
        "language": "Solidity",
        "sources": {"ERC20.sol": {"content": CONTRACT_SOURCE}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
    })
    bytecode = compiled["contracts"]["ERC20.sol"]["ERC20"]["evm"]["bytecode"]["object"]
    abi = compiled["contracts"]["ERC20.sol"]["ERC20"]["abi"]

    # Create contract instance
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(account.address)

    # Set gas price based on network
    gas_price = w3.to_wei("50", "gwei") if network == "m" else w3.to_wei("1", "gwei")
    if network not in ["m", "t"]:
        print(f"{Fore.RED}Invalid network choice. Use 'm' for mainnet or 't' for testnet.{Style.RESET_ALL}")
        sys.exit(1)

    # Build transaction
    tx = contract.constructor(token_name, token_symbol, token_supply).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 2000000,
        "gasPrice": gas_price
    })

    # Sign and send transaction
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"{Fore.GREEN}Token deployed successfully! Transaction hash: {tx_hash.hex()}{Style.RESET_ALL}")

def main():
    """Main function to run the deployer."""
    setup_dependencies()
    private_key, token_name, token_symbol, token_supply, network, rpc_url = get_user_inputs()
    deploy_contract(private_key, token_name, token_symbol, token_supply, network, rpc_url)

if __name__ == "__main__":
    main()
