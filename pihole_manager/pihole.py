#!/usr/bin/env python3

import re
import paramiko

import ipaddress


class PiHoleInstanceValidator:
    def __init__(self, logger) -> None:
        self.logger = logger

    def _validate_ip(self, ip):
        """_summary_

        Args:
            ip (_type_): _description_

        Returns:
            _type_: _description_
        """
        if not isinstance(ip, str):
            return False
        
        try:
            ipaddr = ipaddress.ip_address(ip)
            ipaddr = str(ipaddr)
            is_valid = True
            
        except ValueError as val_err:
            is_valid = False
                        
        pattern = re.compile(
            r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )
        if is_valid:
            return bool(pattern.fullmatch(ip))
        else:
            return False

    def _validate_hostname(self, hostname):
        """determines the validity of the provided dns hostname by evaluating
        the hostname string with a regular expression.

        Args:
            hostname (str): dns hostname as a string.

        Returns:
            bool: True or False whether string matches dns regex.
        """
        if not isinstance(hostname, str):
            return False

        pattern = re.compile(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$")

        return bool(pattern.match(hostname))

    def validate(self, ip=None, hostname=None):
        """_summary_

        Args:
            ip (_type_): _description_
            hostname (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        self.logger.debug(f"Validating: {ip} & {hostname}")
        valid_ip = self._validate_ip(ip)
        valid_dns = self._validate_hostname(hostname)
        self.logger.debug(f"IP Valid: {valid_ip} | HN Valid: {valid_dns}")
    
        return True if valid_ip and valid_dns else False


class PiHole:
    def __init__(self, hostname, port, username, key_file, logger) -> None:
        self.validator = PiHoleInstanceValidator(logger)

        self.hostname = hostname
        self.port = port
        self.username = username
        self.key_file = key_file

        self.logger = logger
        self.client = None

    def _execute(self, cmd):
        """_summary_

        Args:
            cmd (_type_): _description_

        Returns:
            _type_: _description_
        """
        if self.client is None:
            self.logger.debug("No available pihole client. Cannot execute command.")
            return

        _, stdout, stderr = self.client.exec_command(cmd)

        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")

        self.logger.debug(
            f"Execution Results From PiHole Client: output={output} Error={error}"
        )

        return {"error": error} if error else {"output": output}

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
        command = f"cat /etc/pihole/custom.list | grep -i '{ip} ' | wc -l"

        self.logger.debug(f"Checking for existing ip with command: {command}")
        result = self._execute(command)
        self.logger.debug(f"Results From Existing IP Check: {result['output']}")

        if result is None:
            self.logger.debug(
                f"Invalid result from command execution, Returning False."
            )
            return False

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
        is_valid = self.validator.validate(ip=ip)
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

        resp = True if result["output"] == "1\n" else False
        self.logger.debug(f"Record Check in DNS Result: ---> {resp} <---")

        return resp
