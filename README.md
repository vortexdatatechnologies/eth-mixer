<h1>ETH Mixer</h1>
It interacts with the Ethereum network to implement a cryptocurrency mixer.
A mixer is a service that "mixes" funds from multiple accounts to preserve your privacy.

<h2>How to use?</h2>
To configure the parameters and make it work correctly, in your CMD or Terminal you must enter the following:
<h3>Linux and macOS</h3>

***export INFURA_API_KEY=your_infura_api_key***

***export MIXER_ACCOUNTS='0xMixerAccount1,0xMixerAccount2,0xMixerAccount3,0xMixerAccount4,0xMixerAccount5'***

***export MIXER_PRIVATE_KEYS='0xMixerPrivateKey1,0xMixerPrivateKey2,0xMixerPrivateKey3,0xMixerPrivateKey4,0xMixerPrivateKey5'***

This will set the environment variables for the current terminal session. If you want these variables to be available in all terminal sessions, you can add these commands to your shell profile file (such as ~/.bashrc or ~/.bash_profile for bash, ~/.zshrc for zsh).

<h3>Windows</h3>

***set INFURA_API_KEY=tu_infura_api_key***

***set MIXER_ACCOUNTS=0xMixerAccount1,0xMixerAccount2,0xMixerAccount3,0xMixerAccount4,0xMixerAccount5***

***set MIXER_PRIVATE_KEYS=0xMixerPrivateKey1,0xMixerPrivateKey2,0xMixerPrivateKey3,0xMixerPrivateKey4,0xMixerPrivateKey5***

**Note:** Remember to replace your_infura_api_key, 0xMixerAccount1, 0xMixerAccount2, etc., with your own values. And be sure to keep these private keys secure and not share them with anyone.

<h2>Functionality</h2>.
The script performs the following operations:

**Smart contract compilation and deployment:** The script compiles an Ethereum smart contract written in Solidity that manages deposits and withdrawals. Once the contract is compiled, it deploys it to the Ethereum network using one of the accounts defined in the environment variables.

**Mixing of funds:** After the contract is operational, the script performs a series of transactions between the accounts defined in the environment variables. These transactions serve to "shuffle" the funds between these accounts, which helps to hide the original source of funds.

**Withdrawal of funds:** Finally, the script withdraws all funds to a final account specified in the script.

<h2>Warning</h2>.
This mixer does not guarantee complete anonymity. Blockchain analysts may use a variety of techniques to try to trace the origin of funds, even if they have passed through a mixer.

<h2>Security</h2>.
This script handles passwords and private keys carefully, storing them in environment variables, a recommended practice to protect this sensitive information. However, it is strongly recommended to never publish private keys visibly or in public repositories.

<h2>Transaction Costs</h2>.
Since this script interacts with the Ethereum network, each transaction incurs a gas cost that must be covered. Make sure you have enough ETH in your accounts to cover these costs.
