#!/usr/bin/env python3

import os


class TestPiHole:
    from pihole_manager.config import Config, Logging
    from pihole_manager.pihole import PiHole

    config_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "test.config.yaml"
    )
    config = Config(config_file)
    logger = Logging(level=config.log_level).create_logging()

    pihole = PiHole(
        hostname="test.local",
        port=22,
        username="test_user",
        key_file="rsa.key",
        logger=logger,
    )

    def test_pihole_validator_exists(self):
        assert hasattr(self.pihole, "validator") is True

    def test_pihole_client_exists(self):
        assert hasattr(self.pihole, "client") is True

    def test_pihole_logger_exists(self):
        assert hasattr(self.pihole, "logger") is True

    def test_validator_positive_case(self):
        ipaddr = "127.0.0.1"
        hostname = "localhost"
        
        is_valid = self.pihole.validator.validate(ip=ipaddr, hostname=hostname)
        
        assert is_valid is True
        
    def test_validator_negative_case(self):
        ipaddr = "not-an-ip-address"
        hostname = "localhost"
        
        is_valid = self.pihole.validator.validate(ip=ipaddr, hostname=hostname)
        assert is_valid is False
    
    def test_validator_evil_ip_case(self):
        ipaddr = "127.0.0.1 && echo 'here' >> /tmp/flag > /dev/null 2>&1 #" 
        hostname = "localhost"

        is_valid = self.pihole.validator.validate(ip=ipaddr, hostname=hostname)
        assert is_valid is False, "Failed Command Injection Test Case!!"

    def test_validator_evil_hostname_case(self):
        ipaddr = "127.0.0.1"
        hostname = "test.local && echo 'here' >> /tmp/flag > /dev/null 2>&1 #" 

        is_valid = self.pihole.validator.validate(ip=ipaddr, hostname=hostname)
        assert is_valid is False, "Failed Command Injection Test Case!!"

    def test_ip_validation_edge_cases(self):
        valid_ips = ["0.0.0.0", "255.255.255.255", "192.168.1.0", "192.168.1.255"]
        invalid_ips = ["256.0.0.0", "192.168.1.256", "-1.-1.-1.-1", "192.168", "192,168,1,1"]
        
        for ip in valid_ips:
            assert self.pihole.validator.validate(ip=ip, hostname="localhost"), f"Failed for {ip}"
        
        for ip in invalid_ips:
            assert not self.pihole.validator.validate(ip=ip, hostname="localhost"), f"Failed for {ip}"

    def test_hostname_validation_edge_cases(self):
        valid_hostnames = ["example.com", "sub.domain.co.uk", "a.b.c.d.e.f.g.h.i.j.k.l.example.com"]
        invalid_hostnames = ["example!com", "domain@.com", "-example.com", "example-.com"]
        
        for hostname in valid_hostnames:
            assert self.pihole.validator.validate(ip="192.168.1.1", hostname=hostname), f"Failed for {hostname}"
        
        for hostname in invalid_hostnames:
            assert not self.pihole.validator.validate(ip="192.168.1.1", hostname=hostname), f"Failed for {hostname}"
