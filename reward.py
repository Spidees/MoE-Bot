#!/usr/bin/python3
import time
import json
from dotenv import load_dotenv
import os
import glob
import sqlite3
import csv
from datetime import datetime
import requests
import subprocess
import mysql.connector
from mysql.connector import Error
import random

# Load environment variables from .env file
load_dotenv()

# Read DEBUG_MODE value
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False') == 'True'

# Debug log function
def debug_log(message):
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

# Directory path for log files
log_directory = os.getenv('LOG_DIRECTORY')

# Processing channels and their friendly names
channel_names = {}
channels_raw = os.getenv('CHANNELS', '').split(',')
for channel in channels_raw:
    if '=' in channel:
        channel_id, friendly_name = channel.split('=')
        channel_names[channel_id] = friendly_name

local_channels = list(channel_names.keys())

# Vriable to enable/disable Discord messaging
ENABLE_DISCORD = os.getenv('ENABLE_DISCORD', 'True') == 'True'

# Discord webhook URL
webhook_url = os.getenv('DISCORD_WEBHOOK')

# Path to CSV file
csv_file_path = 'account_log.csv'

# Database parameters
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

# Function to initialize the CSV file
def initialize_csv():
    try:
        with open(csv_file_path, 'a+', newline='') as csvfile:
            csvfile.seek(0)
            if not csvfile.read(1):
                writer = csv.writer(csvfile)
                writer.writerow(['s_account_uid', 'from_nick', 'Date', 'Status'])
    except IOError as e:
        print(f"IO Error while initializing CSV file: {e}")

initialize_csv()

# Function to get the IP address, port and rcon password of a channel
def get_channel_ip_and_port_and_rcon(channel_friendly_name):
    ip = os.getenv(f'CHANNEL_{channel_friendly_name}_IP')
    port = os.getenv(f'CHANNEL_{channel_friendly_name}_PORT')
    rcon_password = os.getenv(f'CHANNEL_{channel_friendly_name}_RCON_PASSWORD')
    return ip, port, rcon_password

# Function to load commands from .env
def load_commands():
    commands = []
    command_index = 1
    while True:
        command = os.getenv(f'COMMAND_{command_index}')
        if not command:
            break  # If command does not exist, stop

        # Add command to the list
        commands.append({
            "command": command,
            "chance": int(os.getenv(f'COMMAND_{command_index}_CHANCE', 100))  # Default chance is 100 if not defined
        })
        command_index += 1

    return commands

# Function to execute commands for the player
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
        
        # If chance is met, execute the command
        if random.randint(0, 100) <= command["chance"]:
            debug_log(f"Executing command: {command_str}")
            subprocess.run(command_str, check=True, shell=True)

# Function to process the account
def process_account(account_id, from_nick, to_channel):
    today = datetime.now().strftime("%Y-%m-%d")
    found = False
    accounts = []

    # Get the friendly name of the channel
    channel_friendly_name = channel_names.get(to_channel, "Unknown Channel")

    # Load reward command from ENV
    reward_command = os.getenv('REWARD_COMMAND')

    try:
        with open(csv_file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)

            for row in reader:
                if row[0] == account_id:
                    found = True
                    if row[2] == today and row[3] == '0':
                        debug_log(f"User {from_nick} has already performed the command today.")
                        return
                    elif row[3] != '0':
                        debug_log(f"User {from_nick} is banned.")
                        return
                    else:
                        row[2] = today
                        debug_log(f"Date for user {from_nick} is updated to today.")
                        execute_commands(channel_friendly_name, account_id)
                        send_to_discord(from_nick, f"Received their daily reward by typing {reward_command} in the chat.")
                accounts.append(row)

        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(accounts)
            if not found:
                writer.writerow([account_id, from_nick, today, '0'])
                debug_log(f"Record for user {from_nick} has been added.")
                execute_commands(channel_friendly_name, account_id)
                send_to_discord(from_nick, f"Received their daily reward by typing {reward_command} in the chat.")

    except IOError as e:
        debug_log(f"IOError while processing account: {e}")

# Function to check if the user has performed the action today
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

# Function to find account id from database
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

# Function to process a log line
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

# Function to send a message to Discord
def send_to_discord(from_nick, content):
    if not ENABLE_DISCORD:
        debug_log("Discord messaging is disabled. Skipping message.")
        return

    def escape_markdown(text):
        markdown_chars = ['\\', '*', '_', '~', '`', '>', '|']
        for char in markdown_chars:
            text = text.replace(char, '\\' + char)
        return text

    def truncate_message(text, max_length=2000):
        return text if len(text) <= max_length else text[:max_length-3] + '...'
    
    from_nick = escape_markdown(from_nick)
    content = escape_markdown(content)
    content = truncate_message(content)
    message = f"{from_nick}: {content}"
    data = {"content": message}
    
    if webhook_url:
        response = requests.post(webhook_url, json=data)
        if response.status_code != 204:
            debug_log(f"Error sending message to Discord: {response.status_code} - {response.text}")
    else:
        debug_log("Webhook URL is not defined. Skipping Discord message.")

# Function to find the latest log file in the directory
def find_latest_file(directory):
    try:
        # Search for all log files in the specified directory
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

# Function to watch the log file
def watch_log_file(directory):
    current_file = find_latest_file(directory)
    if not current_file:
        debug_log(f"[INFO] Directory {directory} is empty or no log file exists.")
        time.sleep(5)  # Wait 5 seconds and try again
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
                    process_line(line)

        except Exception as e:
            debug_log(f"Error reading file: {e}")
            time.sleep(5)
            continue

        time.sleep(1)

if __name__ == "__main__":
    debug_log("[INFO] Script is running...")
    watch_log_file(log_directory)
