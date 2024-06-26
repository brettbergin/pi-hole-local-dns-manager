#!/usr/bin/env python3

import os
import argparse


class Arguments:
    def __init__(self) -> None:
        self.supported_operations = [
            "add-dns-record",
            "delete-dns-record",
            "update-pihole",
            "update-gravity",
            "check-record-sync",
        ]

    def parse_arguments(self, args=None):
        """_summary_

        Returns:
            _type_: _description_
        """

        parser = argparse.ArgumentParser(
            description="SSH Client to Manage Pi Hole DNS Configurations."
        )
        parser.add_argument(
            "--config",
            "-c",
            type=str,
            required=True,
            help="YAML Config file for pihole_manager",
        )
        parser.add_argument(
            "--operation",
            "-o",
            type=str,
            required=True,
            help="Available Operations: add-dns-record, delete-dns-record, update-pihole, update-gravity, check-record-sync",
        )
        parser.add_argument("--hostname", "-n", type=str, help="DNS hostname")
        parser.add_argument("--ipaddress", "-i", type=str, help="IP address")
        return parser.parse_args(args)

    def validate_arguments(self, args):
        """_summary_

        Args:
            args (_type_): _description_

        Returns:
            _type_: _description_
        """
        output_args = {}

        if not os.path.exists(args.config):
            return None

        if os.path.getsize(args.config) == 0:
            return None

        if not (args.config.endswith(".yaml") or args.config.endswith(".yml")):
            return None

        output_args["config_file"] = args.config

        if not args.operation in self.supported_operations:
            return None

        output_args["operation"] = {}
        output_args["operation"]["command"] = (
            str(args.operation).lower() if args.operation else ""
        )

        if output_args["operation"]["command"] in (
            "add-dns-record",
            "delete-dns-record",
            "check-record-sync",
        ):
            output_args["operation"]["requires"] = ["hostname", "ipaddress"]

            output_args["hostname"] = str(args.hostname) if args.hostname else ""
            output_args["ipaddress"] = str(args.ipaddress) if args.ipaddress else ""

            for req in output_args["operation"]["requires"]:
                if not req in output_args.keys():
                    return None

                if not len(output_args[req]) > 0:
                    return None

        else:
            output_args["operation"]["requires"] = []

        return output_args
