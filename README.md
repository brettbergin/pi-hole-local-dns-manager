# Pi-hole Local DNS Manager

Pi-hole Local DNS Manager is a command-line interface (CLI) tool designed to manage DNS configurations locally on a Pi-hole server. This utility allows users to easily add, delete, and update DNS records, ensuring their Pi-hole configuration is always up-to-date.

## Features

- **Add DNS Records**: Add new local DNS entries to your Pi-hole configuration, across all pihole hosts.
- **Delete DNS Records**: Remove existing local DNS entries from your Pi-hole configuration, across all pihole hosts.
- **Update DNS Records**: Modify existing local DNS entries from your Pi-hole configuration, across all pihole hosts.
- **Check DNS Records Across Pihole Cluster**: Ensure DNS entries are sync'd across all pihole hosts.
- **Update Gravity**: Update Gravity across all pihole hosts.
- **Update Pihole**: Update Pihole across all pihole hosts.

## Installation

### Prerequisites

- Python 3.6 or later.
- Access to a Pi-hole installation.

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/brettbergin/pi-hole-local-dns-manager.git
   ```
2. Navigate to the cloned directory:
   ```bash
   cd pi-hole-local-dns-manager
   ```
3. Install necessary Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To use the Pi-hole Local DNS Manager, run the `pihole_manager.py` script with the necessary arguments:

```bash
python pihole_manager.py --config config.yaml --operation <operation> [--hostname <hostname>] [--ipaddress <ip_address>]
```

### Command Line Arguments

- `--config`, `-c`: Specify the YAML configuration file for Pi-hole settings.
- `--operation`, `-o`: Define the operation to perform (e.g., `add-dns-record`, `delete-dns-record`).
- `--hostname`, `-n`: (Optional) Specify the hostname for DNS operations that require it.
- `--ipaddress`, `-i`: (Optional) Specify the IP address for DNS operations that require it.

## Examples

Adding a DNS record:

```bash
python pihole_manager.py --config config.yaml --operation add-dns-record --hostname example.com --ipaddress 192.168.1.100
```

Deleting a DNS record:

```bash
python pihole_manager.py --config config.yaml --operation delete-dns-record --hostname example.com
```

## Contributing

Contributions to the Pi-hole Local DNS Manager are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Pi-hole community for their continuous support and feedback.
- Special thanks to all contributors who have helped to improve this tool.
