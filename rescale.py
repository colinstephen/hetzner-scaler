#!/usr/bin/env python

"""
Hetzner Cloud Server Scaler

A script to scale a Hetzner cloud server by changing its type (CPU, RAM, and optionally SSD).
The script reads configuration details from a file and allows overriding these settings using command-line arguments.

The script performs the following steps:
1. Check the current server status.
2. If the server is running, stop it.
3. Ask for confirmation to proceed with scaling.
4. Change the server type based on the specified settings.
5. Restart the server.

Usage:
    python hetzner_scaler.py [--config CONFIG_PATH] [--api_key API_KEY] [--server_id SERVER_ID]
                             [--server_type SERVER_TYPE] [--upgrade_disk]

Arguments:
    --config         Path to the configuration file. (default: config.ini)
    --api_key        Hetzner API key.
    --server_id      ID of the Hetzner server to scale.
    --server_type    Server type to scale to (e.g., 'cpx11', 'cpx21', 'cpx31', etc.).
    --upgrade_disk   Upgrade the SSD along with CPU and RAM.
"""


import argparse
import configparser
import requests
import sys
import time

# Constrain possible server types
server_type_choices = ["cpx11", "cpx21", "cpx31", "cpx41", "cpx51"]
server_type_default = "cpx11"

# Set up argument parser
parser = argparse.ArgumentParser(description="Scale a Hetzner cloud server.")
parser.add_argument(
    "--config", default="config.ini", help="Path to the configuration file."
)
parser.add_argument("--api_key", help="Hetzner API key.")
parser.add_argument("--server_id", help="ID of the Hetzner server to scale.")
parser.add_argument(
    "--server_type",
    default=server_type_default,
    choices=server_type_choices,
    help="Server type (e.g., 'cpx11', 'cpx21', 'cpx31', etc.).",
)
parser.add_argument(
    "--upgrade_disk",
    action="store_true",
    help="Upgrade the SSD along with CPU and RAM.",
)

# Parse command-line arguments
args = parser.parse_args()

# Parse the configuration file
config = configparser.ConfigParser()
config.read(args.config)

# Extract the necessary information and override with command-line arguments
api_key = args.api_key or config.get("hetzner", "api_key")
server_id = args.server_id or config.get("hetzner", "server_id")
server_type = args.server_type
upgrade_disk = args.upgrade_disk or config.getboolean(
    "hetzner", "upgrade_disk", fallback=False
)

# Hetzner Cloud API base URL
base_url = "https://api.hetzner.cloud/v1"

# Set up the request headers
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def get_server(server_id):
    """Get the details of a specific server by its ID."""
    response = requests.get(f"{base_url}/servers/{server_id}", headers=headers)
    return response


def server_action(server_id, action):
    """Perform an action (poweron, poweroff, reboot) on a server by its ID."""
    response = requests.post(
        f"{base_url}/servers/{server_id}/actions/{action}", headers=headers
    )
    return response


def change_server_type(server_id, server_type, upgrade_disk):
    """Change the type of a specific server by its ID."""
    payload = {"server_type": server_type, "upgrade_disk": upgrade_disk}

    response = requests.post(
        f"{base_url}/servers/{server_id}/actions/change_type",
        headers=headers,
        json=payload,
    )
    return response


def wait_for_server_status(server_id, status, status_code=200, timeout=300):
    """Wait for a server to reach the specified status."""

    def spinner():
        """Display a simple spinner to indicate progress."""
        while True:
            for cursor in "|/-\\":
                yield cursor

    spin = spinner()

    start_time = time.time()
    while True:
        response = get_server(server_id)
        if response.status_code == status_code:
            server_status = response.json()["server"]["status"]
            if server_status == status:
                sys.stdout.write("\b \n")  # Clear the spinner
                return True
        else:
            print(f"Error {response.status_code}: {response.text}")
            return False

        if time.time() - start_time > timeout:
            print("Timed out waiting for server status change.")
            return False

        # Update spinner
        sys.stdout.write("\b" + next(spin))
        sys.stdout.flush()
        time.sleep(1)


def server_is_running(server_id):
    """Check if a server is currently running."""
    response = get_server(server_id)
    if response.status_code == 200:
        server_status = response.json()["server"]["status"]
        return server_status == "running"
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


def stop_server(server_id):
    """Stop a server by its ID."""
    stop_response = server_action(server_id, "poweroff")
    if stop_response.status_code == 201:
        print("Server stopping...")
        if wait_for_server_status(server_id, "off"):
            print("Server stopped successfully.")
            print("Waiting 5 seconds before proceeding.")
            time.sleep(5)
            return True
        else:
            print("Failed to stop server.")
            return False
    else:
        print(f"Error {stop_response.status_code}: {stop_response.text}")
        return False


def scale_server(server_id, server_type, upgrade_disk):
    """Scale a server by changing its type."""
    change_response = change_server_type(server_id, server_type, upgrade_disk)
    if change_response.status_code == 201:
        print(f"Server scaling to {server_type} started successfully.")
        return True
    else:
        print(f"Error {change_response.status_code}: {change_response.text}")
        return False


def main():

    # Ask for confirmation
    print("The server will be stopped if it is already running, to rescale it.")
    confirm = input(
        f"Do you want to proceed with scaling the server to {server_type}? (y/n): "
    )
    if confirm.lower() != "y":
        sys.exit("Aborted.")

    # Get current server status
    running = server_is_running(server_id)
    if running is None:
        print("Error occurred while checking server's running status.")
        sys.exit("Aborted.")
    elif running:
        print("Server is currently running.")
        if not stop_server(server_id):
            sys.exit("Aborted.")
    else:
        print("Server is not running.")

    # Change the server type
    if not scale_server(server_id, server_type, upgrade_disk):
        sys.exit("Aborted.")
    else:
        print("Waiting for server to boot.")
        if not wait_for_server_status(server_id, "running"):
            sys.exit("Failed to restart rescaled server.")
        else:
            print("Rescaled server now accessible")


if __name__ == "__main__":
    main()
