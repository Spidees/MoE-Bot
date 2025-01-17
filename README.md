# Myth of Empires Python Reward Bot

This wiki provides documentation for setting up and running the Python-based reward bot for **Myth of Empires**. The bot monitors chat logs for reward commands and executes RCON commands to reward players.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
  - [Environment Variables (`.env`)](#environment-variables-env)
  - [CSV File (`account_log.csv`)](#csv-file-account_logcsv)
  - [Log Files Directory](#log-files-directory)
- [Running the Bot](#running-the-bot)
- [Code Explanation](#code-explanation)
- [Troubleshooting](#troubleshooting)
- [Additional Notes](#additional-notes)
- [Support me](#support-me)

---

## Overview

The reward bot is designed to:
1. Monitor **chat logs** from Myth of Empires servers.
2. Detect when players type the `/reward` command.
3. Execute RCON commands to grant rewards (e.g., items, resources).
4. Log rewards in a CSV file to ensure daily limits are respected.

The bot also supports custom configurations through a `.env` file for database connections, commands, and Discord webhooks.

---

## Prerequisites

1. Python 3.8 or higher installed on your machine.
2. Myth of Empires server with RCON and MySQL configured.
3. Required Python packages installed (use `pip install -r requirements.txt`).
4. `mcrcon.exe` placed in the bot directory (for RCON command execution).
5. A `.env` file properly configured (see below).

---

## Setup

### Environment Variables (`.env`)

Create a `.env` file in the root directory of the bot. Here's an example configuration:

```dotenv
# Channels and their friendly names
CHANNELS="f37d4ffd832000=101,f5161ce4932000=102"

# Mapping of channels to IP addresses and ports
CHANNEL_101_IP="192.168.2.100"
CHANNEL_101_PORT="5030"
CHANNEL_101_RCON_PASSWORD="password"

CHANNEL_102_IP="192.168.2.100"
CHANNEL_102_PORT="5032"
CHANNEL_102_RCON_PASSWORD="password"

# Discord webhook
DISCORD_WEBHOOK="https://discord.com/api/webhooks/"

# Path to the CSV file
csv_file_path="account_log.csv"

# Database parameters
DB_HOST="127.0.0.1"
DB_USER="moediscord"
DB_PASSWORD="moediscord"
DB_DATABASE="moe_role"
DB_COLLATION="utf8mb4_general_ci"

# Path to the log files
LOG_DIRECTORY="C:/serverfiles/MatrixServerTool/chat_logs/"

# Reward command for the bot
REWARD_COMMAND="/reward"

# RCON commands for the bot
COMMAND_1="AddCopper {s_account_uid} 10000"
COMMAND_1_CHANCE=100

COMMAND_2="AddItemToPlayer {s_account_uid} 5412 1 1 1 -1 1.000000 false"
COMMAND_2_CHANCE=100

COMMAND_3="AddItemToPlayer {s_account_uid} 4905 1 1 1 -1 1.000000 false"
COMMAND_3_CHANCE=100

# Debug mode
DEBUG_MODE=True
```

### CSV File (account_log.csv)

Create a `account_log.csv` file in the same directory as the bot script. This file tracks rewards for players and ensures they do not exceed daily limits.

Initial content of `account_log.csv`:

```account_log.csv
s_account_uid,from_nick,Date,Status
```
- **s_account_uid:** Player's account ID.
- **from_nick:** Player's username.
- **Date:** Last date the reward was claimed.
- **Status:** 0 for active users, non-zero values for banned users.

### Log Files Directory

Ensure the chat log directory (LOG_DIRECTORY) specified in the .env file exists and contains server chat logs.

Chat logs are saved by default in `MatrixServerTool/chat_logs`. Here you can also find the `channel` ID for the `.env` `CHANNELS` setting, find example `gid":"f5161ce4932000` where `gid` is `ID` for `CHANNEL`.

---

## Running the Bot

Run the script using the following command:

```cmd run command
python reward.py
```

The bot will:

* Monitor chat logs in real-time.
* Process the /reward command when detected.
* Grant rewards to players based on the specified commands and chances.

---

## Code Explanation

**Key Features**

* Environment Configuration: The bot loads all settings from a .env file for easy configuration.
* Log Monitoring: Reads the latest chat logs in real-time to detect commands.
* Reward Management: Ensures players receive rewards only once per day.
* Discord Notifications: Sends reward messages to a Discord channel.
* RCON Integration: Executes game commands securely using mcrcon.

**Main Functions**

* initialize_csv(): Initializes the account_log.csv file if it doesn't exist.
* watch_log_file(directory): Continuously monitors the latest log file for changes.
* process_line(line): Processes a single log entry to check for /reward commands.
* execute_commands(channel_friendly_name, s_account_uid): Executes configured RCON commands based on random chances.
* send_to_discord(from_nick, content): Sends reward messages to a Discord channel.

---

## Troubleshooting

### Common Issues

**Bot doesn't detect commands:**

Ensure the log directory in the .env file is correct.
Check if the bot has read permissions for the log files.

**Rewards are not granted:**

Verify the RCON details (IP, Port, Password) in the .env file.
Check the format of commands in the .env file (e.g., {s_account_uid} placeholder).

**Discord notifications fail:**

Confirm the Discord webhook URL is correct.
Check the Discord server permissions for the webhook.

**Database connection issues:**

Verify the database credentials and collation in the .env file.

---

## Additional Notes

Use the DEBUG_MODE variable in the .env file to enable detailed logs for troubleshooting.

You can add as many channels as needed by incrementing the CHANNEL_XXX_IP, CHANNEL_XXX_PORT, CHANNEL_XXX_RCON_PASSWORD values in the .env file.

You can add as many commands as needed by incrementing the COMMAND_X and COMMAND_X_CHANCE values in the .env file.

---

## Support Me 
 
🙌 If you enjoy my work and want to support me, you can do so on:  

[![Ko-fi Badge](https://img.shields.io/badge/Support%20me%20on-Ko--fi-ff5e5b?style=flat&logo=ko-fi&logoColor=white)](https://ko-fi.com/playhub)  
[![PayPal Badge](https://img.shields.io/badge/Donate-PayPal-0070ba?style=flat&logo=paypal&logoColor=white)](https://paypal.me/spidees)

Thank you for your support! ❤️
