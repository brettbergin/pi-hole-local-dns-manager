#!/usr/bin/env python3

import os
from unittest.mock import patch, MagicMock

import pytest


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
        """_summary_"""
        assert hasattr(self.pihole, "client") is True

    def test_pihole_logger_exists(self):
        """_summary_"""
        assert hasattr(self.pihole, "logger") is True

    def test_validator_positive_case(self):
        """_summary_"""
        ipaddr = "127.0.0.1"
        hostname = "localhost"

        is_valid = self.pihole.validator.validate(ip=ipaddr, hostname=hostname)

        assert is_valid is True

    def test_validator_negative_case(self):
        """_summary_"""
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
        """ """
        ipaddr = "127.0.0.1"
        hostname = "test.local && echo 'here' >> /tmp/flag > /dev/null 2>&1 #"

        is_valid = self.pihole.validator.validate(ip=ipaddr, hostname=hostname)
        assert is_valid is False, "Failed Command Injection Test Case!!"

    def test_ip_validation_edge_cases(self):
        """_summary_"""
        valid_ips = ["0.0.0.0", "255.255.255.255", "192.168.1.0", "192.168.1.255"]
        invalid_ips = [
            "256.0.0.0",
            "192.168.1.256",
            "-1.-1.-1.-1",
            "192.168",
            "192,168,1,1",
        ]

        for ip in valid_ips:
            assert self.pihole.validator.validate(
                ip=ip, hostname="localhost"
            ), f"Failed for {ip}"

        for ip in invalid_ips:
            assert not self.pihole.validator.validate(
                ip=ip, hostname="localhost"
            ), f"Failed for {ip}"

    def test_hostname_validation_edge_cases(self):
        """_summary_"""
        valid_hostnames = [
            "example.com",
            "sub.domain.co.uk",
            "a.b.c.d.e.f.g.h.i.j.k.l.example.com",
        ]
        invalid_hostnames = [
            "example!com",
            "domain@.com",
            "-example.com",
            "example-.com",
        ]

        for hostname in valid_hostnames:
            assert self.pihole.validator.validate(
                ip="192.168.1.1", hostname=hostname
            ), f"Failed for {hostname}"

        for hostname in invalid_hostnames:
            assert not self.pihole.validator.validate(
                ip="192.168.1.1", hostname=hostname
            ), f"Failed for {hostname}"

    @pytest.fixture
    def pi_hole_instance(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        logger = MagicMock()
        return self.PiHole("example.com", 22, "user", "path/to/key", logger)

    def test_paramiko_client_creation_success(self, pi_hole_instance):
        """_summary_

        Args:
            pi_hole_instance (_type_): _description_
        """
        with patch("paramiko.SSHClient") as mock_ssh:
            mock_instance = MagicMock()
            mock_ssh.return_value = mock_instance

            mock_instance.exec_command.return_value = (
                MagicMock(),
                MagicMock(),
                MagicMock(),
            )
            test_client = pi_hole_instance._create_ph_client()

            mock_ssh.assert_called_once()
            mock_instance.set_missing_host_key_policy.assert_called_once()
            mock_instance.connect.assert_called_once_with(
                pi_hole_instance.hostname,
                pi_hole_instance.port,
                pi_hole_instance.username,
                key_filename=pi_hole_instance.key_file,
            )

            assert test_client == mock_instance

    def test_create_ph_client_connection_failure(self, pi_hole_instance):
        """_summary_

        Args:
            pi_hole_instance (_type_): _description_
        """
        with patch("paramiko.SSHClient") as mock_ssh:
            mock_instance = MagicMock()
            mock_instance.connect.side_effect = Exception("Connection failed")
            mock_ssh.return_value = mock_instance

            with pytest.raises(Exception) as excinfo:
                pi_hole_instance._create_ph_client()

            assert str(excinfo.value) == "Connection failed"
            pi_hole_instance.logger.debug.assert_called_with(
                "Attempting SSH connection to socket: example.com:22"
            )

    def test_ip_exists_in_dns(self, pi_hole_instance, mocker):
        """_summary_

        Args:
            pi_hole_instance (_type_): _description_
            mocker (_type_): _description_
        """
        mocker.patch.object(
            pi_hole_instance, "_execute", return_value={"output": "1\n"}
        )
        mocker.patch.object(pi_hole_instance.validator, "validate", return_value=True)

        assert pi_hole_instance._check_ip_in_dns("192.168.1.1") == True

    def test_ip_does_not_exist_in_dns(self, pi_hole_instance, mocker):
        """_summary_

        Args:
            pi_hole_instance (_type_): _description_
            mocker (_type_): _description_
        """
        mocker.patch.object(
            pi_hole_instance, "_execute", return_value={"output": "0\n"}
        )
        mocker.patch.object(pi_hole_instance.validator, "validate", return_value=True)
        assert pi_hole_instance._check_ip_in_dns("192.168.1.2") == False

    def test_invalid_ip(self, pi_hole_instance, mocker):
        """_summary_

        Args:
            pi_hole_instance (_type_): _description_
            mocker (_type_): _description_
        """
        mocker.patch.object(pi_hole_instance.validator, "validate", return_value=False)
        assert pi_hole_instance._check_ip_in_dns("invalid-ip") is None

    def test_ssh_command_failure(self, pi_hole_instance, mocker):
        """_summary_

        Args:
            pi_hole_instance (_type_): _description_
            mocker (_type_): _description_
        """
        mocker.patch.object(pi_hole_instance, "_execute", return_value=None)
        mocker.patch.object(pi_hole_instance.validator, "validate", return_value=True)
        assert pi_hole_instance._check_ip_in_dns("192.168.1.3") == False

    def test_unexpected_ssh_output(self, pi_hole_instance, mocker):
        """_summary_

        Args:
            pi_hole_instance (_type_): _description_
            mocker (_type_): _description_
        """
        mocker.patch.object(
            pi_hole_instance, "_execute", return_value={"output": "unexpected output"}
        )
        mocker.patch.object(pi_hole_instance.validator, "validate", return_value=True)
        assert pi_hole_instance._check_ip_in_dns("192.168.1.4") == False
