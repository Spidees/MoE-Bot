# Myth of Empires Python Bot

This wiki provides documentation for setting up and running the Python-based bot for **Myth of Empires**.

Main feature:
1. Daily Reward System - The bot monitors chat logs for reward commands and executes RCON commands to reward players.
2. Ingame Chat to Discord - The bot monitors chat logs and sending ingame chat to Discord.
3. Server Status - TODO

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
5. Sending discord reward confirmation messages.
6. Sending ingame chat to Discord

The bot also supports custom configurations through a `.env` file for database connections, commands, and discord token etc..

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
# ╔════════════════════════════════════════════════════════════╗
#                     BASIC SETTINGS
# ╚════════════════════════════════════════════════════════════╝

# Path to the chat log files
LOG_DIRECTORY="C:/serverfiles/MatrixServerTool/chat_logs/"

# Enter your discord bot token here
DISCORD_BOT_TOKEN=54d2eESs12w1we545s1q2w3e4a6w12ea1s23aw5e64as321ew3qw468fg9g4h6j

# ╔════════════════════════════════════════════════════════════╗
#                     REWARD SYSTEM INTEGRATION
# ╚════════════════════════════════════════════════════════════╝

# Enable or disable the reward system
ENABLE_REWARD_SYSTEM=True

# MySQL Database parameters
DB_HOST="127.0.0.1"
DB_USER="moediscord"
DB_PASSWORD="moediscord"
DB_DATABASE="moe_role"
DB_COLLATION="utf8mb4_general_ci"

# Command to trigger the reward
REWARD_COMMAND="/reward"

# Path to the CSV file
csv_file_path="account_log.csv"

# Mapping of channels and their friendly names
# Format: channel_id=friendly_name
CHANNELS="f37d4ffd832000=101,f5161ce4932000=102"

# Define the IP address, port, and RCON password for each channel
CHANNEL_101_IP="192.168.2.100"
CHANNEL_101_PORT="5030"
CHANNEL_101_RCON_PASSWORD="password"

CHANNEL_102_IP="192.168.2.100"
CHANNEL_102_PORT="5032"
CHANNEL_102_RCON_PASSWORD="password"

CHANNEL_103_IP="192.168.2.100"
CHANNEL_103_PORT="5032"
CHANNEL_103_RCON_PASSWORD="password"

# Define RCON commands with a chance of execution (0-100%)
# {s_account_uid} will be replaced by the player’s ID

COMMAND_1="AddCopper {s_account_uid} 10000"
COMMAND_1_CHANCE=100

COMMAND_2="AddItemToPlayer {s_account_uid} 5412 1 1 1 -1 1.000000 false"
COMMAND_2_CHANCE=100

COMMAND_3="AddItemToPlayer {s_account_uid} 4905 1 1 1 -1 1.000000 false"
COMMAND_3_CHANCE=100

# Enable or disable Discord notifications
ENABLE_REWARD_TO_DISCORD=True

# Discord channel for sending messages
REWARD_DISCORD_CHANNEL_ID=1367623754548772924

# Template for the Discord message sent when a reward is given
# Available shortcodes: {command}, {nick}, {channel}
REWARD_DISCORD_MESSAGE_TEMPLATE="**{nick}** received their daily reward by typing **{command}** in the chat."

# ╔════════════════════════════════════════════════════════════╗
#                   CHAT TO DISCORD INTEGRATION
# ╚════════════════════════════════════════════════════════════╝

# Enable or disable chat messages being sent to Discord
ENABLE_CHAT_TO_DISCORD=True

# Mapping of channels and their friendly names
CHAT_CHANNELS="132d7951a8b2000=County 101,132d795eba32000=County 102,132d79f50a32000=County 103"

# Discord channel for sending ingame chat
CHAT_DISCORD_CHANNEL_ID=1367623754548772924

# Template for the Discord message
# Available shortcodes: {chat_message}, {server}, {chat_nick}
CHAT_DISCORD_MESSAGE_TEMPLATE="**{server} - {chat_nick}:** {chat_message}"

# ╔════════════════════════════════════════════════════════════╗
#                   SERVER STATUS TO DISCORD INTEGRATION
# ╚════════════════════════════════════════════════════════════╝

# Enable or disable server status messages being sent to Discord
ENABLE_SERVER_STATUS=True
ENABLE_DISCORD_PRESENCE=True

# Discord channel for sending server status
STATUS_DISCORD_CHANNEL_ID=1088603624743125125

# IP adress and port game server status
LOGIN_SERVER=51.51.51.51:7010
CLUSTER_SERVER_1=51.51.51.51:5010
CLUSTER_SERVER_2=51.51.51.51:5010
CLUSTER_SERVER_3=51.51.51.51:5010
BATTLE_SERVER_1=51.51.51.51:5010
BATTLE_SERVER_2=51.51.51.51:5010
BATTLE_SERVER_3=51.51.51.51:5010
BATTLE_SERVER_4=51.51.51.51:5010

# Optional: Status labels for different game modes or servers

LOGIN_SERVER_NAME=Login
CLUSTER_SERVER_1_NAME=County 101
CLUSTER_SERVER_2_NAME=County 102
CLUSTER_SERVER_3_NAME=County 103
BATTLE_SERVER_1_NAME=Battle 1
BATTLE_SERVER_2_NAME=Battle 2
BATTLE_SERVER_3_NAME=Battle 3

EMBED_COLOR=#00ff00
EMBED_LABEL_TITLE=MYTH OF EMPIRES SERVER STATUS

TOTAL_PLAYERS=TOTAL PLAYERS ONLINE
MAP_TITLE=Map
TYPE_TITLE=Type
OFFLINE_DESCRIPTIONS=server is currently offline or not found.

Map_Lobby=Lobby
LargeTerrain_Central2_Main=Island Dongzhou
LargeTerrain_Central_Main=Zhongzhou
LargeTerrain_Desert_Main=Xizhou
Battlefield_Main_New=Plain
Battlefield_Gorge_Main=Gobi Canyon
CountyTown_Main=County town
CountyTown_Main_Special=Castle siege
Newyear_01_Main=New Years event
Racehorse_01_Main=Horse racing
Prefecturewar_Main_Special=Prefecture Battle
WarOfThePass_Main_Special=Fortress Battle

PVP=PvP
PVE=PvE

# ╔════════════════════════════════════════════════════════════╗
#                          DEBUGGING SETTINGS
# ╚════════════════════════════════════════════════════════════╝

# Set to True to enable debugging
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
python bot.py
```

The bot will:

* Monitor chat logs in real-time.
* Process the /reward command when detected.
* Grant rewards to players based on the specified commands and chances.
* Send messages to Discord.

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
