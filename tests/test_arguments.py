#!/usr/bin/env python3


class TestArguments:
    def test_add_dns_record_arguments(self):
        from pihole_manager.arguments import Arguments

        args = Arguments()
        options = args.validate_arguments(
            args.parse_arguments(
                [
                    "-c",
                    "config.yaml",
                    "-o",
                    "add-dns-record",
                    "-n",
                    "test.example.com",
                    "-i",
                    "192.168.1.1",
                ]
            )
        )

        assert "config_file" in options.keys()
        assert "operation" in options.keys()
        assert "hostname" in options.keys()
        assert "ipaddress" in options.keys()

        assert "command" in options["operation"].keys()
        assert "requires" in options["operation"].keys()

    def test_delete_dns_record_arguments(self):
        from pihole_manager.arguments import Arguments

        args = Arguments()
        options = args.validate_arguments(
            args.parse_arguments(
                [
                    "-c",
                    "config.yaml",
                    "-o",
                    "delete-dns-record",
                    "-n",
                    "test.example.com",
                    "-i",
                    "192.168.1.1",
                ]
            )
        )

        assert "config_file" in options.keys()
        assert "operation" in options.keys()
        assert "hostname" in options.keys()
        assert "ipaddress" in options.keys()

        assert "command" in options["operation"].keys()
        assert "requires" in options["operation"].keys()

    def test_check_record_sync_arguments(self):
        from pihole_manager.arguments import Arguments

        args = Arguments()
        options = args.validate_arguments(
            args.parse_arguments(
                [
                    "-c",
                    "config.yaml",
                    "-o",
                    "check-record-sync",
                    "-n",
                    "test.example.com",
                    "-i",
                    "192.168.1.1",
                ]
            )
        )

        assert "config_file" in options.keys()
        assert "operation" in options.keys()
        assert "hostname" in options.keys()
        assert "ipaddress" in options.keys()

        assert "command" in options["operation"].keys()
        assert "requires" in options["operation"].keys()

    def test_update_gravity_arguments(self):
        from pihole_manager.arguments import Arguments

        args = Arguments()
        options = args.validate_arguments(
            args.parse_arguments(["-c", "config.yaml", "-o", "update-gravity"])
        )

        assert "config_file" in options.keys()
        assert "operation" in options.keys()
        assert "command" in options["operation"].keys()

    def test_update_pihole_arguments(self):
        from pihole_manager.arguments import Arguments

        args = Arguments()
        options = args.validate_arguments(
            args.parse_arguments(["-c", "config.yaml", "-o", "update-pihole"])
        )

        assert "config_file" in options.keys()
        assert "operation" in options.keys()
        assert "command" in options["operation"].keys()

    def test_invalid_operation_arguments(self):
        from pihole_manager.arguments import Arguments

        args = Arguments()
        options = args.validate_arguments(
            args.parse_arguments(["-c", "config.yaml", "-o", "update-foobar"])
        )

        assert options is None

    def test_invalid_configfile_arguments(self):
        from pihole_manager.arguments import Arguments

        args = Arguments()
        options = args.validate_arguments(
            args.parse_arguments(["-c", "config.foo", "-o", "update-pihole"])
        )

        assert options is None
