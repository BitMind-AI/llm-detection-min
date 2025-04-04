# ⛏️ Mining 

## FAQ

We've collected some frequently asked questions in the Discord Channel and made a FAQ page, hope this help you to run your miners easier. We'll be updating it with fresh questions as they appear:
 
https://piquant-door-af5.notion.site/FAQ-0de42be01aa948c08cbfe982f2112aa8?pvs=4

## System Requirements

Miners will need enough processing power to inference models. The device the models are inferenced on is recommended to be a GPU (atleast NVIDIA RTX A4000) with minimum 16 GB of VRAM.


## Installation

1. Clone the repo

```bash
apt update && apt upgrade -y
git clone https://github.com/It-s-AI/llm-detection
```  

2. Setup your python [virtual environment](https://docs.python.org/3/library/venv.html) or [Conda environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands).

3. Install the requirements. From your virtual environment, run
```shell
cd llm-detection
python -m pip install -e .
```

4. Download models for LLM classification
```commandline
wget https://huggingface.co/sergak0/sn32/resolve/main/deberta-large-ls03-ctx1024.pth -O models/deberta-large-ls03-ctx1024.pth
wget https://huggingface.co/sergak0/sn32/resolve/main/deberta-v3-large-hf-weights.zip -O models/deberta-v3-large-hf-weights.zip
apt install zip unzip
unzip models/deberta-v3-large-hf-weights.zip -d models/deberta-v3-large-hf-weights
```

4. Make sure you've [created a Wallet](https://docs.bittensor.com/getting-started/wallets) and [registered a hotkey](https://docs.bittensor.com/subnets/register-and-participate).

```bash
btcli w new_coldkey
btcli w new_hotkey
btcli s register --netuid 32 --wallet.name YOUR_COLDKEY --wallet.hotkey YOUR_HOTKEY
```

5. (Optional) Run a Subtensor instance:  
Your node will run better if you are connecting to a local Bittensor chain entrypoint node rather than using Opentensor's. 
We recommend running a local node as follows and passing the ```--subtensor.network local``` flag to your running miners/validators. 
To install and run a local subtensor node follow the commands below with Docker and Docker-Compose previously installed.
```bash
git clone https://github.com/opentensor/subtensor.git
cd subtensor
docker compose up --detach
```

## Running the Miner



> **Note:** Recently, the public RPC endpoint has been under high load, so it's strongly advised that you use your local Subtensor instance!


Install PM2 and the jq package on your system.
```bash
sudo apt update && sudo apt install jq && sudo apt install npm && sudo npm install pm2 -g && pm2 update
```

To start your miner basic command is

```bash
pm2 start --name net32-miner --interpreter python3 ./neurons/miner.py -- --wallet.name YOUR_COLDKEY --wallet.hotkey YOUR_HOTKEY --neuron.device cuda:0 --axon.port 70000 
```

## Running the Miner on TESTNET

We have testnet subnet with netuid **87**. There is our validator running with uid 52 and hotkey `5Eo4PQvU4fhGLhk91UKpAaaEH59aHsVsw2jZ6ZhRT12s6JRA`.  

To start miner on testnet you have to run the following command

```bash
pm2 start --name net32-miner --interpreter python3 ./neurons/miner.py -- --wallet.name YOUR_COLDKEY --wallet.hotkey YOUR_HOTKEY --neuron.device cuda:0 --axon.port 70000 --subtensor.network test  --netuid 87 --blacklist.minimum_stake_requirement 0
```

> IMPORTANT: you should set `blacklist.minimum_stake_requirement` argument to 0 so our validator won't get blacklisted


```bash
pm2 start --name net32-miner ./neurons/miner.py -- --wallet.name default --wallet.hotkey miner --axon.port 80001 --subtensor.network test  --netuid 87
```
