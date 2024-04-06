#!/usr/bin/env python3

import re
import paramiko


class Validation:
    def __init__(self, logger) -> None:
        self.logger = logger

    def validate(self, ip, hostname=None):
        """ 
        """
        self.logger.debug(f"Validating: {ip} & {hostname}")
        valid_ip = self._validate_ip(ip)
        valid_dns = self._validate_hostname(hostname)

        return True if valid_ip or valid_dns else False

    def _validate_ip(self, ip):
        """
        """
        if not isinstance(ip, str):
            return False

        pattern = re.compile(
            r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        )

        return bool(pattern.match(ip))

    def _validate_hostname(self, hostname):
        """
        """
        if not isinstance(hostname, str):
            return False

        pattern = re.compile(r"^([a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]\.?)+$")
        
        return bool(pattern.match(hostname))


class PiHole:
    def __init__(self, hostname, port, username, key_file, logger) -> None:
        self.validator = Validation(logger)

        self.hostname  = hostname
        self.port      = port
        self.username  = username
        self.key_file  = key_file
        self.logger    = logger

        self.client    = None

    def connect(self):
        self.client = self._create_ph_client()
        resp = True if self.client else False
        
        self.logger.debug(f"Successfully created pihole client: {resp}")
        return resp

    def add_dns_record(self, ip_addr, hostname):
        self.logger.info(f"Adding DNS record: {ip_addr}={hostname}")

        is_valid = self.validator.validate(ip=ip_addr, hostname=hostname)
        if not is_valid:
            self.logger.error("Input Validation Failure.")
            return None

        ip_exists = self.check_ip_in_custom_dns(ip_addr)
        if ip_exists:
            self.logger.debug("Unable to add dns record. IP exists on host.")
            return False

        command = f'echo "{ip_addr} {hostname}" | sudo tee -a /etc/pihole/custom.list && pihole restartdns reload'
        self.logger.debug(f"Executing Command: {command}")

        result = self._execute(command)
        return result
    
    def delete_dns_record(self, ip, hostname):
        self.logger.info(f"Deleting DNS Record: {ip}={hostname}")

        is_valid = self.validator.validate(ip=ip)
        if not is_valid:
            return None
    
        ip_exists = self.check_ip_in_custom_dns(ip)
        if not ip_exists:
            self.logger.debug("IP wasnt found in custom dns. Nothing to delete!")
            return False

        command = f"sudo sed -i '/{ip} {hostname}/d' /etc/pihole/custom.list && pihole restartdns reload"
        
        self.logger.debug(f"Deleting DNS record with command: {command}")
        result = self._execute(command)

        return result

    def update_pihole(self):
        command = "pihole -up"

        self.logger.debug(f"Updating Pihole with command: {command}")
        result = self._execute(command)
        self.logger.debug(f"Update Pihole Result: {result}")
        
        return result

    def update_gravity(self):
        command = "pihole -g"

        self.logger.debug(f"Updating gravity with command: {command}")
        result = self._execute(command)
        self.logger.debug(f"Update Gravity Result: {result}")
        
        return result

    def check_ip_in_custom_dns(self, ip):
        command = f"cat /etc/pihole/custom.list | grep -i '{ip} ' | wc -l"
        
        self.logger.debug(f"Checking for existing ip with command: {command}")
        result = self._execute(command)
        print(result)
        self.logger.debug(f"Results From Existing IP Check: {result}")

        if result is None:
            self.logger.debug(f"Invalid result from command execution, Returning False.")
            return False
        
        resp = True if result["output"] == "1\n" else False
        self.logger.debug(f"Returning Response Fro Check IP In Custom DNS: {resp}")
        return resp



    def _execute(self, cmd):
        if self.client is None:
            self.logger.debug("No available pihole client. Cannot execute command.")
            return
        
        _, stdout, stderr = self.client.exec_command(cmd)

        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")
        
        self.logger.debug(f"Execution Results From PiHole Client: output={output} Error={error}")
        return {"error": error} if error else {"output": output}

    def _create_ph_client(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.logger.info(f"Attempting SSH connection to socket: {self.hostname}:{self.port}")
        client.connect(
            self.hostname, self.port, self.username, key_filename=self.key_file
        )

        return client
