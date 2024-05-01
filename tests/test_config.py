#!usr/bin/env python3

import os


class TestConfig:
    from pihole_manager.config import Config

    config = Config(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.config.yaml")
    )

    def test_config_init(self):
        assert self.config is not None

    def test_config_valid_file(self):
        assert self.config.config_file is not None
        assert self.config.config_file_content is not None

    def test_pihole_hosts(self):
        assert len(self.config.pihole_hosts) > 0

    def test_pihole_host(self):
        test_host = self.config.pihole_hosts[0]
        test_host_details = test_host["host"]

        assert "host" in test_host.keys()
        assert "hostname" in test_host_details.keys()
        assert "port" in test_host_details.keys()
        assert "username" in test_host_details.keys()
        assert "ssh_key" in test_host_details.keys()

    def test_hostname_scope(self):
        assert len(self.config.pihole_hostnames) > 0

    def test_config_loglevel(self):
        assert self.config.log_level is not None
