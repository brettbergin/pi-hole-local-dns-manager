#!usr/bin/env python3

import os
import sys

import platform
import logging
from logging.handlers import TimedRotatingFileHandler


class Config:
    def __init__(self) -> None:
        self.platform = self._determine_platform()
        self.sshconfig = {
            "port": "22",
            "username": "pi",
            "hostnames": [
                "pi-hole-01.berginlabs.com",
                "pi-hole-02.berginlabs.com",
                "pi-hole-03.berginlabs.com",
            ],
            "key_file": self._determine_key_file(),
        }

    def _determine_platform(self):
        return platform.platform()

    def _determine_key_file(self):
        if self.platform.lower().startswith("windows"):
            return os.path.join("C:", "Users", "brett", ".ssh", "lethal")
        else:
            return os.path.join("/", "mnt", "c", "Users", "brett", ".ssh", "lethal")


class Logging:
    def __init__(self, here) -> None:
        self.here = here
        self.log_filename = "pihole-manager.log"

    def create_logging(self):
        logger = logging.getLogger("'pihole-manager")
        logger.setLevel(logging.DEBUG)
        log_file_path = os.path.join(self.here, self.log_filename)
        log_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        file_handler = TimedRotatingFileHandler(
            log_file_path, when="midnight", interval=5, backupCount=7
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.suffix = "%Y-%m-%d-BACKUP"

        file_handler.setFormatter(log_formatter)
        console_handler.setFormatter(log_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger
