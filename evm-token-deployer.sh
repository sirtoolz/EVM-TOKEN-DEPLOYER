const { ethers } = require("ethers");
const readline = require("readline");
require("dotenv").config();

const chalk = require("chalk");

console.log(chalk.blue.bold("=============================="));
console.log(chalk.magenta.bold("✨ Made With Love By SIRTOOLZ ✨"));
console.log(chalk.blue.bold("=============================="));

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

async function askQuestion(query) {
    return new Promise(resolve => rl.question(query, resolve));
}

async function deployContract() {
    console.log(chalk.green.bold("🚀 Deploying Your Token - Made With Love By SIRTOOLZ 🚀"));
    
    const networkType = await askQuestion("Do you want to deploy on mainnet or testnet? (mainnet/testnet): ");
    const rpcUrl = await askQuestion("Enter RPC URL for your chosen network: ");
    const privateKey = await askQuestion("Enter your wallet private key: ");
    const tokenName = await askQuestion("Enter token name: ");
    const tokenSymbol = await askQuestion("Enter token symbol: ");
    const tokenSupply = await askQuestion("Enter token supply (in whole tokens, not wei): ");
    rl.close();
    
    const provider = new ethers.JsonRpcProvider(rpcUrl);
    const wallet = new ethers.Wallet(privateKey, provider);
    
    const erc20ABI = [
        "constructor(string memory name, string memory symbol, uint256 initialSupply)",
    ];
    
    const erc20Bytecode = "0x..."; // Replace with actual compiled ERC-20 bytecode
    
    const factory = new ethers.ContractFactory(erc20ABI, erc20Bytecode, wallet);
    const contract = await factory.deploy(tokenName, tokenSymbol, ethers.parseUnits(tokenSupply, 18));
    
    console.log(chalk.yellow("Deploying contract..."));
    await contract.waitForDeployment();
    console.log(chalk.cyan.bold(`🎉 Token deployed at: ${await contract.getAddress()} 🎉`));
}

deployContract().catch(error => {
    console.error(chalk.red("Error deploying contract:"), error);
    process.exit(1);
});
