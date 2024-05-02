# dnsman

I have multiple pihole servers in my home lab. I became tired of manually administering my local DNS records in their user interfaces. This project attempts to solve this problem using python.

Pi-hole Local DNS Manager (dnsman) is a command-line interface (CLI) tool designed to manage local DNS configurations across a fleet of pihole servers. This utility allows users to easily add, delete, and update DNS records, ensuring their Pi-hole configuration is always up-to-date.

If you would like to use this program, checkout the installation section. You will be able to run `dnsman` afterwards.

## Features
- **Add DNS Records**: Add new local DNS entries to your Pi-hole local dns configuration, across all pihole hosts.
- **Delete DNS Records**: Remove existing local DNS entries to your Pi-hole local dns configuration, across all pihole hosts.
- **Update DNS Records**: Modify existing local DNS entries to your Pi-hole local dns configuration, across all pihole hosts.
- **Check DNS Records Across Pihole Cluster**: Determine if a local DNS entry has been added across all pihole hosts.
- **Update Gravity**: Update Gravity across all pihole hosts.
- **Update Pihole**: Update Pihole across all pihole hosts.

```bash
% dnsman -h
usage: dnsman [-h] --config CONFIG --operation OPERATION [--hostname HOSTNAME] [--ipaddress IPADDRESS]

SSH Client to Manage Pi Hole DNS Configurations.

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG (required)
                        YAML Config file for pihole_manager
  --operation OPERATION, -o OPERATION (required)
                        Available Operations: add-dns-record, delete-dns-record, update-pihole, update-gravity, check-record-sync
  --hostname HOSTNAME, -n HOSTNAME
                        DNS hostname
  --ipaddress IPADDRESS, -i IPADDRESS
                        IP address
```
## Installation

### Prerequisites

- Python 3.6 or later.
- SSH Access to a Pi-hole installation(s).

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/brettbergin/pi-hole-local-dns-manager.git
   ```
2. Navigate to the cloned directory:
   ```bash
   cd pi-hole-local-dns-manager
   ```
3. Create and activate a virtualenv:
   ```bash
   virtualenv .venv && source .venv/bin/activate
   ```
4. Install project
   ```bash
   python3 setup.py install
   ```
5. Run `dnsman`
   ``` bash
   dnsman -h
   ```
6. Close virtual env.
   ```bash
   deactivate
   ```

## Configuration

### Yaml File Configuration
Create a `config.yaml` file with the following contents. Add a `-host` section for each pihole server you are running. This program currently only supports key based ssh authentication to the pihole server. SSH password authentication is not supported at this time.
```yaml
pihole:
  hosts:
    - host:
        hostname: test.local
        port: 22
        username: test_user
        ssh_key: /path/to/test/rsa.key
logging:
  log_level: debug
```

The `pihole` section of the yaml defines the pihole server hosts and the ssh authentication needed to login to the pihole host(s).

The `logging` section of the yaml currently only defines the desired log level. You can set this to `debug`, `info`, `error`, and `critical` at this time. logging is currently only being sent to stdout.

## Testing
Unit testing is currently implemented using pytest. From the project root, run: pytest.
```bash
pytest
```
to see with logging:
```bash
pytest -s
```

## Usage
To use the Pi-hole Local DNS Manager, run `dnsman` with the necessary arguments:

```bash
dnsman --config config.yaml --operation <operation> [--hostname <hostname>] [--ipaddress <ip_address>]
```

### Command Line Arguments

- `--config`, `-c`: Specify the YAML configuration file for Pi-hole settings.
- `--operation`, `-o`: Define the operation to perform (e.g., `add-dns-record`, `delete-dns-record`).
- `--hostname`, `-n`: (Optional) Specify the hostname for DNS operations that require it.
- `--ipaddress`, `-i`: (Optional) Specify the IP address for DNS operations that require it.

## Examples

Adding a DNS record:

```bash
dnsman --config config.yaml --operation add-dns-record --hostname example.com --ipaddress 192.168.1.100
```
Deleting a DNS record:

```bash
dnsman --config config.yaml --operation delete-dns-record --hostname example.com --ipaddress 192.168.1.100
```
Checking if all pihole servers have a specific DNS entry:
```bash
dnsman --config config.yaml --operation check-record-sync --hostname example.com --ipaddress 192.168.1.100
```
Update gravity across all pihole servers
```bash
dnsman --config config.yaml --operation update-gravity
```
Update pihole across all pihole servers
```bash
dnsman --config config.yaml --operation update-pihole
```

## Contributing

Contributions to the Pi-hole Local DNS Manager are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Pi-hole community for their continuous support and feedback.
