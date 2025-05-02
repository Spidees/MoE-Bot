# Myth of Empires Discord Bot

A multifunctional Discord bot for Myth of Empires, built for private servers to:

- Post player chat from in-game to Discord
- Reward players for using in-game commands (with RCON execution)
- Show server statuses from the official API (player count, map, type, etc.)
- Display current status in Discord presence ("X servers | Y players")

---

## ✅ Features

### 💬 Chat to Discord
- Forwards in-game chat messages to a specific Discord channel
- Handles custom formatting with guild tags and nickname

### 🎁 Reward System
- Players can use `/reward` (or custom command) in-game to trigger a reward
- Rewards are granted via RCON commands
- Logs reward claims in CSV
- Prevents multiple claims per day and blocks banned accounts
- MySQL integration for account validation

### 📊 Server Status to Discord
- Queries official Myth of Empires API every 1 minute
- Displays:
  - Online players / max players
  - Server map (with emoji)
  - PvP or PvE mode
  - Offline indicator with custom message
- Fully configurable in `.env` file

### 🟢 Discord Presence Update
- Automatically updates bot presence
- Format: `"X servers | Y players"`
- Can be toggled via `.env`

### 🧪 Debug Mode
- Controlled with `DEBUG_MODE=True`
- Prints detailed debug logs to help with setup and troubleshooting

---

## ⚙️ Environment Setup (`.env`)

```ini
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

---

## ▶️ Running

Install dependencies:
```bash
pip install -r requirements.txt
```

Start the bot:
```bash
python bot.py
```

---

## 🧩 Dependencies
- `discord.py`
- `python-dotenv`
- `requests`
- `mysql-connector-python`

---

## 📁 Structure

- `bot.py` – Main bot script
- `.env` – Configuration file
- `account_log.csv` – Reward tracking
- `mcrcon.exe` – RCON command utility (Windows)

---

## 🔧 Tips & Notes

- Commands use `{s_account_uid}` as a placeholder for RCON
- All servers matched by IP and port from the official MoE API
- Format of chat lines must be valid JSON log lines
- You can extend the number of reward commands and channels freely
- Offline status is shown for servers not found in the API response

---

## 🙌 Support

If you enjoy this project, consider supporting:

[![Ko-fi Badge](https://img.shields.io/badge/Support%20me%20on-Ko--fi-ff5e5b?style=flat&logo=ko-fi&logoColor=white)](https://ko-fi.com/playhub)  
[![PayPal Badge](https://img.shields.io/badge/Donate-PayPal-0070ba?style=flat&logo=paypal&logoColor=white)](https://paypal.me/spidees)

Thanks for your support!
