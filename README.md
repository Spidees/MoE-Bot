# Myth of Empires Reward Bot

This Python script allows you to execute RCON commands on a Myth of Empires server based on chat log file data. It is designed to process user commands, check for rewards, and execute specific commands in the game when a certain condition is met. It uses environment variables for configuration, integrates with Discord to send notifications, and can process account data stored in CSV format.

## Features

- **Reward System**: Allows users to claim daily rewards by typing a specific command.
- **CSV Logging**: Tracks user interactions and actions in a CSV file (`account_log.csv`).
- **Discord Integration**: Sends notifications to Discord when a reward is claimed.
- **Customizable Commands**: Commands are loaded from environment variables, with a chance factor.

## Prerequisites

Before running the script, ensure you have the following:

- **Python 3.x**: The script is written in Python and requires Python 3 to run.
- **Myth of Empires with RCON and MySQL**: The script interacts with your MoE server using RCON. You need to enable RCON. To fetch account IDs from a MySQL database, ensure you have access to a MySQL server with the required database and tables.
- **Discord Webhook**: The script sends notifications to a Discord channel. You will need a Discord webhook URL.

## Setup

### Configure the .env File
Create a .env file in the root of the project directory and configure it with the required environment variables. 
Example file is in project directory with name env_example .

Channels and their friendly names you can find in chat logs directory MatrixServerTool\chat_logs, and find example gid":"f5161ce4932000

### Install the external dependencies
To install the external dependencies, run the following command in cmd: 

pip install python-dotenv requests mysql-connector-python

### Running the Script
Once everything is configured, you can run the script by executing command in cmd: python reward.py

The script will:
- Monitor the chat log files in the directory specified by LOG_DIRECTORY.
- Check each log line for a reward command (e.g., /reward).
- If the user has not claimed their reward today, it will execute the corresponding RCON commands.
- Send a notification to Discord about the user's reward claim.
- Log the status to account_log.csv.
