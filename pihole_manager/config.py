#!usr/bin/env python3

import os
import sys
import logging
import platform

import yaml


class Config:
    def __init__(self, file_abspath) -> None:
        self.platform = self._determine_platform()

        self.config_file = file_abspath
        if not os.path.exists(file_abspath):
            raise FileNotFoundError(
                f"Unable to open provided config file: {self.config_file}"
            )

        self.config_file_content = self._parse_config_file()
        if not self.config_file_content:
            raise AssertionError(
                "No configuration details found in provided yaml file."
            )

        self.log_level = self._parse_log_level()
        self.pihole_hosts = self._parse_pihole_hosts()
        self.pihole_hostnames = self._parse_hostname_scope()

    def _determine_platform(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return platform.platform()

    def _parse_config_file(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        with open(self.config_file, "r") as file:
            data = yaml.safe_load(file)

        return data

    def _parse_log_level(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.config_file_content["logging"]["log_level"]

    def _parse_pihole_hosts(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.config_file_content["pihole"]["hosts"]
    
    def _parse_hostname_scope(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return [
            h["host"]["hostname"] for h in self._parse_pihole_hosts()
        ]


class Logging:
    def __init__(self, level) -> None:
        if not isinstance(level, str):
            self.log_level = None

        if level.lower() in ("info", "debug", "critical", "error"):
            self.log_level = level.upper()

        if self.log_level == "info".upper():
            self.log_format = "%(asctime)s - %(levelname)s - %(message)s"

        else:
            self.log_format = (
                "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s"
            )

    def create_logging(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        logger = logging.getLogger("pihole_manager")
        logger.setLevel(self.log_level)

        console_handler = logging.StreamHandler(sys.stdout)
        log_formatter = logging.Formatter(self.log_format)
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

        return logger
