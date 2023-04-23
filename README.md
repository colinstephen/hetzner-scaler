# Hetzner Cloud Server Scaler

This repository contains a Python script to scale a Hetzner cloud server by changing its type (CPU, RAM, and optionally SSD). The script reads configuration details from a file and allows overriding these settings using command-line arguments.

## Setup

1. Clone this repository:
   
   `git clone https://github.com/colinstephen/hetzner-scaler.git && cd hetzner-scaler`

2. Create a virtual environment and activate it:

    `python -m venv venv && source venv/bin/activate # On Windows, use "venv\Scripts\activate"`

3. Install the required packages:

   `pip install -r requirements.txt`

4. Copy `config_example.ini` to `config.ini` and update the settings with your Hetzner API key and server ID:

    `cp config_example.ini config.ini`

    Then open `config.ini` with your preferred text editor and update the `api_key` and `server_id` values.

## Usage

To run the script, execute the following command:

```bash
python rescale.py [--config CONFIG_PATH] [--api_key API_KEY] [--server_id SERVER_ID] [--server_type SERVER_TYPE] [--upgrade_disk]
```

### Arguments

- `--config`: Path to the configuration file. (default: config.ini)
- `--api_key`: Hetzner API key.
- `--server_id`: ID of the Hetzner server to scale.
- `--server_type`: Server type to scale to (e.g., 'cpx11', 'cpx21', 'cpx31', etc.).
- `--upgrade_disk`: Upgrade the SSD along with CPU and RAM.

## Example

To scale a server to the `cpx21` type with an upgraded SSD, run:

```bash
python rescale.py --server_type cpx21 --upgrade_disk
```

This will use the API key and server ID from the `config.ini` file and change the server type to `cpx21` while upgrading the SSD.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
