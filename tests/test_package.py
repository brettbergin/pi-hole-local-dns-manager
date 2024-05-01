#!usr/bin/env python3

import os


class TestPkgImportability:
    def test_args_import(self):
        from pihole_manager.arguments import Arguments

        args = Arguments()

        assert args is not None

    def test_config_import(self):
        from pihole_manager.config import Config

        config = Config(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.config.yaml")
        )

        assert config is not None

    def test_logging_import(self):
        from pihole_manager.config import Config, Logging

        config = Config(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.config.yaml")
        )
        logger = Logging(level=config.log_level)

        assert logger is not None

    def test_cluster_import(self):
        from pihole_manager.config import Config, Logging
        from pihole_manager.cluster import PiHoleCluster

        config = Config(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.config.yaml")
        )
        logger = Logging(level=config.log_level)
        cluster = PiHoleCluster(logger=logger, config=config)

        assert cluster is not None

    def test_pihole_import(self):
        from pihole_manager.config import Config, Logging
        from pihole_manager.pihole import PiHole

        config = Config(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.config.yaml")
        )
        logger = Logging(level=config.log_level)
        pihole = PiHole(
            hostname="test.example.com",
            port=22,
            username="test_user",
            key_file="test_key_file",
            logger=logger,
        )

        assert pihole is not None
