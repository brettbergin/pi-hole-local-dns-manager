#!usr/bin/env python3

import os
import sys

import platform
import logging

import yaml


class Config:
    def __init__(self, file_abspath) -> None:
        self.platform = self._determine_platform()
        self.default_config_filename = 'config.yaml'
        
        if not os.path.exists(file_abspath):
            self.config_file = None
        else:
            self.config_file = os.path.join(file_abspath, self.default_config_filename)
        
        self.config_file_content = self._parse_config_file()
    
        self.log_level = self._parse_log_config()
        self.pihole_hosts = self._parse_pihole_config()
        self.pihole_hostnames = [h['host']['hostname'] for h in self._parse_pihole_config()]

    def _determine_platform(self):
        return platform.platform()

    def _parse_config_file(self):
        with open(self.config_file, 'r') as file:
            data = yaml.safe_load(file)
        return data
    
    def _parse_log_config(self):
        return self.config_file_content['logging']['log_level']
        
    def _parse_pihole_config(self):
        return self.config_file_content['pihole']['hosts']


class Logging:
    def __init__(self, level) -> None:
        if not isinstance(level, str):
            self.log_level = None
        
        if level.lower() in ('info', 'debug', 'critical', 'error'):
            self.log_level = level.upper()
        
        if self.log_level == 'info'.upper():
            self.log_format = '%(asctime)s - %(levelname)s - %(message)s'

        else:
            self.log_format = '%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s'

    def create_logging(self):
        """_summary_

        Returns:
            _type_: returns logging module logger object.
        """
        logger = logging.getLogger("'pihole_manager")
        logger.setLevel(self.log_level)
        
        
        console_handler = logging.StreamHandler(sys.stdout)
        log_formatter = logging.Formatter(self.log_format)
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

        return logger
