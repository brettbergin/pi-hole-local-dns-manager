#!/usr/bin/env python3

import re
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
            ipaddr = str(ipaddress.ip_address(ip))            
            is_valid = True if len(ipaddr) > 0 else False

        except ValueError as val_err:
            is_valid = False

        pattern = re.compile(
            r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )
        passes_pattern_match = bool(pattern.fullmatch(ip))
        return True if is_valid and passes_pattern_match else False

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

        return bool(pattern.fullmatch(hostname))

    def validate(self, ip=None, hostname=None):
        """_summary_

        Args:
            ip (_type_): _description_
            hostname (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        self.logger.debug(f"Validating: ip={ip} | hostname={hostname}")
        valid_ip = self._validate_ip(ip)
        valid_dns = self._validate_hostname(hostname)
        self.logger.debug(f"IP-Valid={valid_ip} | HN-Valid={valid_dns}")
    
        return True if valid_ip and valid_dns else False
