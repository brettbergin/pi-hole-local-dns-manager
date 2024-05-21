#!/usr/bin/env python3

import paramiko

from .validators import PiHoleInstanceValidator


class PiHole:
    def __init__(self, hostname, port, username, key_file, logger) -> None:
        self.hostname = hostname
        self.port = port
        self.username = username
        self.key_file = key_file

        self.logger = logger
        self.client = None

        self.validator = PiHoleInstanceValidator(self.logger)

    def _get_remote_platform(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        try:           
            command = 'cat /etc/os-release|grep "ID=raspbian"'
            _, stdout, stderr = self.client.exec_command(command)

            output = str(stdout.read().decode("utf-8"))
            error = str(stderr.read().decode("utf-8"))
            
            if len(error) > 0:
                self.logger.error(f"Received error: {error}")
                return {"error": error}

            self.logger.debug(f"Results from {command} : {output}")
            
            if output == 'ID=raspbian\n':
                platform = output.split('=')[1].strip('"').strip("\n")
                return platform

            else:
                return None
        
        except Exception as err:
            self.logger.error(f"Unable to fetch platform information. Error={err}")
            return None

    def _execute(self, cmd):
        """_summary_

        Args:
            cmd (_type_): _description_

        Returns:
            _type_: _description_
        """
        if self.client is None:
            self.logger.error("No available pihole client. Cannot execute command.")
            return {"error": "No available pihole client. Cannot execute command."}

        platform = self._get_remote_platform()        
        if platform != "raspbian":
            self.logger.error("Not a raspbian host. Cannot execute command.")
            return {'error': "Not a raspbian host. Cannot execute command."}

        else:
            self.logger.info(f"Executing command on platform: {platform}")

        _, stdout, stderr = self.client.exec_command(cmd)

        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")
                
        if len(error) > 0:
            self.logger.error(f"Received command execution error: {error}")
            return {"error": error.strip("\n")}

        return {"output": output.strip("\n")}

    def _create_ph_client(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.logger.debug(
            f"Attempting SSH connection to socket: {self.hostname}:{self.port}"
        )
        client.connect(
            self.hostname, self.port, self.username, key_filename=self.key_file
        )

        return client

    def _check_ip_in_dns(self, ip):
        """_summary_

        Args:
            ip (_type_): _description_

        Returns:
            _type_: _description_
        """
        is_valid = self.validator.validate(ip=ip)
        if not is_valid:
            self.logger.error("IPAddress Input Validation Failure.")
            return None

        command = f"cat /etc/pihole/custom.list | grep -i '{ip} ' | wc -l"
        self.logger.debug(f"Checking for existing ip with command: {command}")

        result = self._execute(command)

        if result is None:
            self.logger.debug(
                f"Invalid result from command execution, Returning False."
            )
            return False

        if "error" in result.keys():
            self.logger.debug(f"Error Fron Existing IP Check: {result['error']}")

        else:
            self.logger.debug(f"Results Frin Existing IP Check: {result['output']}")

        resp = True if result["output"] == "1\n" else False
        self.logger.debug(f"IP Check in DNS Result: ---> {resp} <---")
        return resp

    def connect(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        self.client = self._create_ph_client()
        resp = True if self.client else False

        self.logger.debug(f"Successfully created pihole client: {resp}")
        return resp

    def add_dns_record(self, ip_addr, hostname):
        """_summary_

        Args:
            ip_addr (_type_): _description_
            hostname (_type_): _description_

        Returns:
            _type_: _description_
        """
        self.logger.info(f"Adding DNS record: {ip_addr}={hostname}")

        is_valid = self.validator.validate(ip=ip_addr, hostname=hostname)
        if not is_valid:
            self.logger.error("Input Validation Failure.")
            return None

        ip_exists = self._check_ip_in_dns(ip_addr)
        if ip_exists:
            self.logger.debug("Unable to add dns record. IP exists on host.")
            return False

        command = f'echo "{ip_addr} {hostname}" | sudo tee -a /etc/pihole/custom.list && pihole restartdns reload'
        self.logger.debug(f"Executing Command: {command}")

        result = self._execute(command)
        return result

    def delete_dns_record(self, ip, hostname):
        """_summary_

        Args:
            ip (_type_): _description_
            hostname (_type_): _description_

        Returns:
            _type_: _description_
        """
        is_valid = self.validator.validate(ip=ip, hostname=hostname)
        if not is_valid:
            return None

        ip_exists = self._check_ip_in_dns(ip)
        if not ip_exists:
            self.logger.error("IP wasnt found in custom dns. Nothing to delete.")
            return False

        command = f"sudo sed -i '/{ip} {hostname}/d' /etc/pihole/custom.list && pihole restartdns reload"
        self.logger.debug(f"Executing Command: {command}")

        result = self._execute(command)
        return result

    def update_pihole(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        command = "pihole -up"

        self.logger.debug(f"Updating Pihole with command: {command}")
        result = self._execute(command)
        self.logger.debug(f"Update Pihole Result: {result}")

        return result

    def update_gravity(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        command = "pihole -g"

        self.logger.debug(f"Updating gravity with command: {command}")
        result = self._execute(command)
        self.logger.debug(f"Update Gravity Result: {result}")

        return result

    def check_record_in_dns(self, ip, host):
        """_summary_

        Args:
            ip (_type_): _description_
            host (_type_): _description_

        Returns:
            _type_: _description_
        """
        is_valid = self.validator.validate(ip=ip, hostname=host)
        if not is_valid:
            return None

        command = (
            f"cat /etc/pihole/custom.list | grep -i '{ip}' | grep -i '{host}' | wc -l"
        )

        self.logger.debug(f"Checking for existing ip with command: {command}")
        result = self._execute(command)
        self.logger.debug(f"Results From Existing IP Check: {result['output']}")

        if result is None:
            self.logger.debug(
                f"Invalid result from command execution, Returning False."
            )
            return False

        resp = True if result["output"] == "1" else False
        self.logger.debug(f"Record Check in DNS Result: ---> {resp} <---")

        return resp
