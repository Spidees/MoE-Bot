#!/usr/bin/python3
import os
import re
import csv
import glob
import json
import time
import random
import sqlite3
import subprocess
from datetime import datetime
import threading

# 3rd party
import requests
import discord
import asyncio
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========== DISCORD BOT (TOKEN-BASED, MULTI-CHANNEL) ==========

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_MAP = {
    "reward": int(os.getenv("REWARD_DISCORD_CHANNEL_ID", "0")),
    "chat": int(os.getenv("CHAT_DISCORD_CHANNEL_ID", "0")),
    "status": int(os.getenv("STATUS_DISCORD_CHANNEL_ID", "0"))
}

intents = discord.Intents.default()
discord_client = discord.Client(intents=intents)
discord_message_queue = asyncio.Queue()

@discord_client.event
async def on_ready():
    print(f"Discord bot logged in as {discord_client.user}")
    asyncio.create_task(discord_message_sender())

    if ENABLE_SERVER_STATUS:
        asyncio.create_task(update_server_status_loop())    

async def discord_message_sender():
    await discord_client.wait_until_ready()
    while True:
        message, target = await discord_message_queue.get()
        channel_id = CHANNEL_MAP.get(target, CHANNEL_MAP["reward"])
        channel = discord_client.get_channel(channel_id)
        if channel:
            try:
                await channel.send(message)
            except Exception as e:
                print(f"Error sending message to Discord: {e}")
        await asyncio.sleep(1)

def send_to_discord(nick, msg, target="reward"):
    # Checking permissions by target channel
    if (target == "reward" and not ENABLE_REWARD_TO_DISCORD) or \
       (target == "chat" and not ENABLE_CHAT_TO_DISCORD) or \
       (target == "status" and not ENABLE_SERVER_STATUS):
        debug_log(f"Discord messaging is disabled for target '{target}'. Skipping.")
        return

    formatted = msg
    asyncio.run_coroutine_threadsafe(
        discord_message_queue.put((formatted, target)),
        discord_client.loop
    )

async def start_discord_bot():
    await discord_client.start(TOKEN)

# ========== END DISCORD BLOCK ==========

# Read DEBUG_MODE value (controls debug logs)
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False') == 'True'

# Debug log function to output messages when DEBUG_MODE is enabled
def debug_log(message):
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

# Directory path where log files are stored
log_directory = os.getenv('LOG_DIRECTORY')

# Flags to enable/disable specific features
ENABLE_REWARD_SYSTEM = os.getenv('ENABLE_REWARD_SYSTEM', 'True') == 'True'
ENABLE_REWARD_TO_DISCORD = os.getenv("ENABLE_REWARD_TO_DISCORD", "True") == "True"
ENABLE_CHAT_TO_DISCORD = os.getenv('ENABLE_CHAT_TO_DISCORD', 'True') == 'True'
ENABLE_SERVER_STATUS = os.getenv('ENABLE_SERVER_STATUS', 'True') == 'True'

# Function to find the latest log file in the directory
def find_latest_file(directory):
    try:
        log_files = glob.glob(os.path.join(directory, "*.log"))
        if log_files:
            latest_file = max(log_files, key=os.path.getctime)  # File with the latest creation time
            debug_log(f"Latest file: {latest_file}")
            return latest_file
        else:
            debug_log("No log file found.")
            return None
    except Exception as e:
        debug_log(f"Error finding log files: {e}")
        return None

# Function to monitor the latest log file for new entries
def watch_log_file(directory):
    try:
        current_file = find_latest_file(directory)
        if not current_file:
            debug_log(f"[INFO] Directory {directory} is empty or no log file exists.")
            time.sleep(5)
            return

        debug_log(f"Starting to watch file: {current_file}")
        file_position = os.path.getsize(current_file)

        while True:
            try:
                new_file = find_latest_file(directory)
                if new_file != current_file:
                    current_file = new_file
                    file_position = 0
                    debug_log(f"[INFO] New file detected: {current_file}")

                with open(current_file, 'r', encoding='utf-8') as file:
                    file.seek(file_position)
                    lines = file.readlines()

                    if not lines:
                        debug_log("[INFO] No new lines to process.")
                    else:
                        debug_log(f"[INFO] Processing {len(lines)} lines.")

                    file_position = file.tell()

                if lines:
                    for line in lines:
                        if ENABLE_REWARD_SYSTEM:
                            process_line(line)
                        if ENABLE_CHAT_TO_DISCORD:
                            process_chat_line(line)

            except Exception as e:
                debug_log(f"Error reading file: {e}")
                time.sleep(5)
                continue

            time.sleep(1)

    except KeyboardInterrupt:
        debug_log("[INFO] Script interrupted by user (Ctrl+C). Exiting cleanly.")

# REWARD SYSTEM

if ENABLE_REWARD_SYSTEM:
    debug_log("[INFO] Reward system is enabled.")    

    # Database configuration (for managing accounts)
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_database = os.getenv('DB_DATABASE')
    db_collation = os.getenv('DB_COLLATION')

    db_config = {
        'host': db_host,
        'user': db_user,
        'password': db_password,
        'database': db_database,
        'collation': db_collation
    }

    # Reward channels (mapping channel IDs to friendly names)
    channel_names = {}
    channels_raw = os.getenv('CHANNELS', '').split(',')
    for channel in channels_raw:
        if '=' in channel:
            channel_id, friendly_name = channel.split('=')
            channel_names[channel_id] = friendly_name

    local_channels = list(channel_names.keys())

    # Path to CSV file where rewards are recorded
    csv_file_path = os.getenv('csv_file_path')

    # Enable/disable Discord messaging for rewards
    enable_reward_to_discord = os.getenv('ENABLE_REWARD_TO_DISCORD', 'True') == 'True'


    # Initialize the CSV file if it doesn't already exist
    def initialize_csv():
        try:
            with open(csv_file_path, 'a+', newline='') as csvfile:
                csvfile.seek(0)
                if not csvfile.read(1):  # If file is empty, write header
                    writer = csv.writer(csvfile)
                    writer.writerow(['s_account_uid', 'from_nick', 'Date', 'Status'])
        except IOError as e:
            print(f"IO Error while initializing CSV file: {e}")

    initialize_csv()

    # Get IP, port, and RCON password for a channel
    def get_channel_ip_and_port_and_rcon(channel_friendly_name):
        ip = os.getenv(f'CHANNEL_{channel_friendly_name}_IP')
        port = os.getenv(f'CHANNEL_{channel_friendly_name}_PORT')
        rcon_password = os.getenv(f'CHANNEL_{channel_friendly_name}_RCON_PASSWORD')
        return ip, port, rcon_password

    # Load custom commands from .env
    def load_commands():
        commands = []
        command_index = 1
        while True:
            command = os.getenv(f'COMMAND_{command_index}')
            if not command:
                break  # No more commands in .env

            # Add command to the list
            commands.append({
                "command": command,
                "chance": int(os.getenv(f'COMMAND_{command_index}_CHANCE', 100))  # Default chance is 100 if not defined
            })
            command_index += 1

        return commands

    # Execute custom commands for a specific player
    def execute_commands(channel_friendly_name, s_account_uid):
        ip, port, rcon_password = get_channel_ip_and_port_and_rcon(channel_friendly_name)
    
        if not ip or not port or not rcon_password:
            debug_log(f"IP or port or rcon password for channel {channel_friendly_name} is not defined in ENV.")
            return

        # Load commands from ENV
        commands = load_commands()

        # Execute commands based on chance
        for command in commands:
            # Replace {s_account_uid} with the current account ID
            command_str = command["command"].replace("{s_account_uid}", s_account_uid)
            command_str = f"mcrcon.exe -H {ip} -P {port} -p {rcon_password} -w 5 \"{command_str}\""
        
            # Execute command if chance condition is met
            if random.randint(0, 100) <= command["chance"]:
                debug_log(f"Executing command: {command_str}")
                subprocess.run(command_str, check=True, shell=True)

    # Process account to record rewards and check eligibility
    def process_account(account_id, from_nick, to_channel):
        today = datetime.now().strftime("%Y-%m-%d")
        found = False
        accounts = []

        # Get the friendly name of the channel
        channel_friendly_name = channel_names.get(to_channel, "Unknown Channel")

        # Reward command and message template from ENV
        reward_command = os.getenv('REWARD_COMMAND', '!reward')
        message_template = os.getenv('REWARD_DISCORD_MESSAGE_TEMPLATE', "Received their daily reward by typing {command} in the chat.")

        try:
            with open(csv_file_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)

                for row in reader:
                    if row[0] == account_id:
                        found = True
                        if row[2] == today and row[3] == '0':  # Already performed today
                            debug_log(f"User {from_nick} has already performed the command today.")
                            return
                        elif row[3] != '0':  # Banned
                            debug_log(f"User {from_nick} is banned.")
                            return
                        else:
                            row[2] = today
                            debug_log(f"Date for user {from_nick} is updated to today.")
                            execute_commands(channel_friendly_name, account_id)
                            message = message_template.format(command=reward_command, nick=from_nick, channel=channel_friendly_name)
                            send_to_discord(from_nick, message)
                    accounts.append(row)

            with open(csv_file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
                writer.writerows(accounts)
                if not found:
                    writer.writerow([account_id, from_nick, today, '0'])
                    debug_log(f"Record for user {from_nick} has been added.")
                    execute_commands(channel_friendly_name, account_id)
                    message = message_template.format(command=reward_command, nick=from_nick, channel=channel_friendly_name)
                    send_to_discord(from_nick, message)

        except IOError as e:
            debug_log(f"IOError while processing account: {e}")

    # Check if user has already performed the action today
    def check_csv_for_entry(account_id):
        today = datetime.now().strftime("%Y-%m-%d")
    
        try:
            with open(csv_file_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header

                for row in reader:
                    if row[0] == account_id:  # Check if account_id matches
                        if row[2] == today and row[3] == '0':  # Already performed today
                            return True, False
                        elif row[3] != '0':  # User is banned
                            return True, False
                        return True, True  # Entry exists, but not done today

            return False, False  # No entry found

        except IOError as e:
            debug_log(f"IOError while checking CSV for entry: {e}")
            return False, False     

    # Find account ID from database based on role UID
    def get_account_id(s_role_uid, db_config):
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                collation=db_config['collation']
            )
            cursor = conn.cursor()
            cursor.execute("SELECT s_account_id FROM moe_roles WHERE s_role_uid = %s", (s_role_uid,))
            account_id = cursor.fetchone()
            cursor.close()
            conn.close()
            return account_id[0] if account_id else None
        except Error as e:
            print(f"Database error: {e}")
            return None

    # Process each log line
    def process_line(line):
        try:
            debug_log(f"Processing log line: {line}")
            log_entry = json.loads(line)
            to_channel = log_entry.get("to")
            if to_channel in local_channels:
                from_role_uid = log_entry.get("from")
                from_nick = log_entry.get("from nick", "Unknown")
                content = log_entry.get("content", "")

                reward_command = os.getenv('REWARD_COMMAND', '/reward')

                if reward_command in content:
                    debug_log(f"Command {reward_command} detected in content: {content}")
                
                    # Check if user has already performed the command today
                    entry_exists, is_today = check_csv_for_entry(from_role_uid)

                    if entry_exists and is_today:
                        debug_log(f"User {from_nick} has already performed the command today.")
                        return

                    account_id = get_account_id(from_role_uid, db_config)
                    if account_id:
                        process_account(account_id, from_nick, to_channel)
                    else:
                        debug_log(f"Account ID for {from_role_uid} was not found.")
        except json.JSONDecodeError as e:
            debug_log(f"Error decoding JSON: {e}")

else:
    debug_log("[INFO] Reward system is disabled.")        

# CHAT TO DISCORD

if ENABLE_CHAT_TO_DISCORD:
    debug_log("[INFO] Chat to Discord integration is enabled.")

    # Load chat channels from .env
    chat_channels = os.getenv('CHAT_CHANNELS', '').split(',')
    chat_channel_names = {}
    for chat_channel in chat_channels:
        if '=' in chat_channel:
            channel_id, friendly_name = chat_channel.split('=')
            chat_channel_names[channel_id] = friendly_name


    # Template for Discord messages
    chat_message_template = os.getenv('CHAT_DISCORD_MESSAGE_TEMPLATE', "{server} - {chat_nick}: {chat_message}")

    # Function to send a chat message to Discord
    def send_chat_message_to_discord(server, chat_nick, chat_message):
        def escape_markdown(text):
            markdown_chars = ['\\', '*', '_', '~', '`', '>', '|']
            for char in markdown_chars:
                text = text.replace(char, '\\' + char)
            return text

        def truncate_message(text, max_length=2000):
            return text if len(text) <= max_length else text[:max_length - 3] + '...'

        chat_nick = escape_markdown(chat_nick)
        chat_message = escape_markdown(chat_message)
        chat_message = truncate_message(chat_message)
        msg = chat_message_template.format(server=server, chat_nick=chat_nick, chat_message=chat_message)
        send_to_discord(server, msg, target="chat")

    # Function to process chat log lines
    def process_chat_line(line):
        try:
            log_entry = json.loads(line)
            to_channel = log_entry.get("to")
            if to_channel in chat_channel_names:
                server_name = chat_channel_names.get(to_channel, "Unknown Server")
                chat_nick = log_entry.get("from nick", "Unknown")
                chat_content = log_entry.get("content", "")

                if ENABLE_REWARD_SYSTEM:
                    reward_command = os.getenv('REWARD_COMMAND', '/reward')
                    if reward_command in chat_content:
                        debug_log(f"Skipping message containing reward command: {chat_content}")
                        return

                if "^^&&" in chat_content:
                    guild_name, chat_message = chat_content.split("^^&&", 1)
                    chat_nick = f"<{guild_name}> {chat_nick}"
                else:
                    chat_message = chat_content

                send_chat_message_to_discord(server_name, chat_nick, chat_message)
        except json.JSONDecodeError as e:
            debug_log(f"Error decoding JSON in chat line: {e}")
else:
    debug_log("[INFO] Chat to Discord integration is disabled.")

# SERVER STATUS

if ENABLE_SERVER_STATUS:
    debug_log("[INFO] Server status integration is enabled.")

async def update_server_status_loop():
    await discord_client.wait_until_ready()
    status_channel_id = int(os.getenv("STATUS_DISCORD_CHANNEL_ID", "0"))

    embed_title = os.getenv("EMBED_LABEL_TITLE", "Server Status")
    total_players_label = os.getenv("TOTAL_PLAYERS", "Total Players Online")
    map_title = os.getenv("MAP_TITLE", "Map")
    type_title = os.getenv("TYPE_TITLE", "Type")
    offline_description = os.getenv("OFFLINE_DESCRIPTIONS", "server is currently offline or not found.")

    enable_presence = os.getenv("ENABLE_DISCORD_PRESENCE", "False") == "True"

    server_keys = [
        key for key in os.environ
        if re.match(r"^[A-Z0-9_]+_SERVER(_\d+)?$", key) and not key.endswith("_NAME")
    ]
    name_mapping = {key: os.getenv(f"{key}_NAME", key) for key in server_keys}

    pvp_types = {
        "PVP": os.getenv("PVP", "⚔️ PVP"),
        "PVE": os.getenv("PVE", "🛡️ PVE")
    }

    urls = [
        "https://l11-prod-list-moegame.angelagame.com/GameServerList_BigPrivate.json",
        "https://l11-prod-list-moegame.angelagame.com/GameServerList_Private.json",
        "https://l11-prod-list-moegame.angelagame.com/GameServerList_Listen.json"
    ]

    while True:
        try:
            server_list = []
            for url in urls:
                response = requests.get(url)
                data = response.json()
                server_list.extend(data.get("server_list", []))

            output_lines = []
            total_online = 0
            active_server_count = 0

            for key in server_keys:
                address = os.getenv(key)
                if not address or ":" not in address:
                    debug_log(f"[WARNING] Invalid server address format for '{key}': '{address}'")
                    continue
                ip, port = address.split(":", 1)
                server_data = next((s for s in server_list if s.get("addr") == ip and str(s.get("port")) == port), None)
                name = name_mapping.get(key, key)

                if server_data:
                    custom_info = json.loads(server_data.get("custom_info", "{}"))
                    online = int(server_data.get("online", 0))
                    maxplayers = int(custom_info.get("maxplayer", 100))

                    map_key = custom_info.get("map_name", "")
                    map_label = os.getenv(map_key, map_key)

                    pvp_key = "PVP" if custom_info.get("pvp_type") == 0 else "PVE"
                    pvp_label = pvp_types.get(pvp_key, pvp_key)

                    line = (
                        f"**{name}**\n"
                        f":green_circle: Online: {online}/{maxplayers}\n"
                        f"{map_title}: {map_label}\n"
                        f"{type_title}: {pvp_label}\n"
                    )
                    total_online += online
                    active_server_count += 1
                else:
                    line = (
                        f"**{name}**\n"
                        f":red_circle: Offline\n"
                        f"{name} {offline_description}\n"
                    )

                output_lines.append(line)

            embed_color_str = os.getenv("EMBED_COLOR", "#00ff00").lstrip("#")
            try:
                embed_color = discord.Color(int(embed_color_str, 16))
            except ValueError:
                embed_color = discord.Color.green()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            embed = discord.Embed(
                title=embed_title,
                description=f":people_holding_hands: **{total_players_label}: {total_online}**\n\n" + "\n".join(output_lines),
                color=embed_color
            )
            embed.set_footer(text=f"Last updated: {now}")

            channel = discord_client.get_channel(status_channel_id)
            if channel:
                async for message in channel.history(limit=20):
                    if message.author == discord_client.user and message.embeds:
                        await message.edit(embed=embed)
                        break
                else:
                    await channel.send(embed=embed)

            # 🌐 Update Discord presence if enabled
            if enable_presence:
                presence_text = f"{active_server_count} servers | {total_online} players"
                await discord_client.change_presence(activity=discord.Game(name=presence_text))

        except Exception as e:
            print(f"[ERROR] Server status fetch failed: {e}")

        await asyncio.sleep(60)

if not ENABLE_SERVER_STATUS:
    debug_log("[INFO] Server status integration is disasbled.")
    
# ANNOUNCEMENT SYSTEM

announcement_file = "announcement.txt"

ENABLE_SERVER_ANNOUNCEMENTS = os.getenv('ENABLE_SERVER_ANNOUNCEMENTS', 'False') == 'True'

# Parse announcement.txt into structured blocks
def parse_announcements(file_path):
    if not os.path.exists(file_path):
        debug_log("Announcement file does not exist.")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    announcements = []
    block = {}

    for line in lines:
        line = line.strip()
        if line.startswith("# --- announcement ---"):
            block = {}
        elif line.startswith("# --- end ---"):
            if "text" in block and "interval" in block and "servers" in block:
                block["interval"] = int(block["interval"])
                block["servers"] = block["servers"].split(",")
                announcements.append(block)
        elif "=" in line:
            key, value = line.split("=", 1)
            block[key.strip()] = value.strip()

    debug_log(f"Parsed {len(announcements)} announcement blocks.")
    return announcements

# Send announcement text to specified servers using RCON
def send_announcement_to_servers(text, target_server_ids):
    for channel_id, friendly_name in channel_names.items():
        if friendly_name not in target_server_ids:
            continue

        ip = os.getenv(f'CHANNEL_{friendly_name}_IP')
        port = os.getenv(f'CHANNEL_{friendly_name}_PORT')
        rcon_password = os.getenv(f'CHANNEL_{friendly_name}_RCON_PASSWORD')

        if not ip or not port or not rcon_password:
            debug_log(f"Missing RCON configuration for channel: {friendly_name}")
            continue

        command = [
            'mcrcon.exe',
            '-H', ip,
            '-P', port,
            '-p', rcon_password,
            '-w', '5',
            f'BroadcastNotifySysInfo "{text}" 1 0'
        ]

        try:
            debug_log(f"Executed announcement command: {' '.join(command)}")
            subprocess.run(command, check=True, timeout=5)
        except Exception as e:
            debug_log(f"Error executing announcement command: {e}")

# Async loop that manages timing and sending of announcements
async def announcement_loop():
    if not ENABLE_SERVER_ANNOUNCEMENTS:
        debug_log("Server announcements are disabled.")
        return

    announcements = parse_announcements(announcement_file)
    if not announcements:
        debug_log("No announcements loaded. Skipping loop.")
        return

    last_sent = [0] * len(announcements)

    while True:
        now = time.time()

        for i, anonce in enumerate(announcements):
            if now - last_sent[i] >= anonce["interval"]:
                send_announcement_to_servers(anonce["text"], anonce["servers"])
                last_sent[i] = now

        await asyncio.sleep(1)

# Main function starts the log monitoring
if __name__ == "__main__":
    debug_log("[INFO] Script is running...")

    def run_discord():
        asyncio.run(start_discord_bot())

    discord_thread = threading.Thread(target=run_discord, daemon=True)
    discord_thread.start()

    if ENABLE_SERVER_ANNOUNCEMENTS:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(announcement_loop())

        threading.Thread(target=loop.run_forever, daemon=True).start()

    watch_log_file(log_directory)
