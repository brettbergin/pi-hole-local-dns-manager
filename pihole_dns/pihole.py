#!/usr/bin/env python3

import re
import paramiko


class Validation:
    def __init__(self) -> None:
        pass

    def validate(self, ip, hostname):
        valid_ip = self._validate_ip(ip)
        valid_dns = self._validate_hostname(hostname)
        return True if valid_ip and valid_dns else False

    def _validate_ip(self, ip):
        pattern = re.compile(
            r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        )
        return bool(pattern.match(ip))

    def _validate_hostname(self, hostname):
        pattern = re.compile(r"^([a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]\.?)+$")
        return bool(pattern.match(hostname))


class PiHole:
    def __init__(self, hostname, port, username, key_file) -> None:
        self.hostname = hostname
        self.port = port
        self.username = username
        self.key_file = key_file

        self.client = None

    def connect(self):
        self.client = self._create_ph_client()
        return True if self.client else False

    def add_dns_record(self, ip_addr, hostname):
        v = Validation()
        is_valid = v.validate(ip=ip_addr, hostname=hostname)
        if not is_valid:
            return False

        ip_exists = self._check_ip_in_custom_dns(ip_addr)
        if ip_exists:
            raise ValueError("IP Address Exists. Cannot Add DNS Record.")

        cmd = f'echo "{ip_addr} {hostname}" | sudo tee -a /etc/pihole/custom.list && pihole restartdns reload'
        result = self._execute(cmd)
        return result

    def update_pihole(self):
        command = "pihole -up"
        result = self._execute(command)
        return result

    def update_gravity(self):
        command = "pihole -g"
        result = self._execute(command)
        return result

    def _check_ip_in_custom_dns(self, ip):
        cmd = f"cat /etc/pihole/custom.list | grep -i '{ip}' | wc -l"
        result = self._execute(cmd)

        return True if "1" in result["output"] else False

    def delete_dns_record(self, ip, hostname):
        cmd = f"sudo sed -i '/{ip} {hostname}/d' /etc/pihole/custom.list && pihole restartdns reload"
        result = self._execute(cmd)
        return result

    def _execute(self, cmd):
        _, stdout, stderr = self.client.exec_command(cmd)

        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")

        return {"error": error} if error else {"output": output}

    def _create_ph_client(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(
            self.hostname, self.port, self.username, key_filename=self.key_file
        )
        return client
