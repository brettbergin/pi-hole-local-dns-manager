#!/usr/bin/env python3

import sys

from pihole_manager.arguments import Arguments
from pihole_manager.config import Logging, Config
from pihole_manager.cluster import PiHoleCluster


def main():
    args = Arguments()
    options = args.validate_arguments(args.parse_arguments())

    if not options:
        print(f"Invalid input arguments have been provided. Please try again.")
        sys.exit(1)

    config = Config(file_abspath=options["config_file"])

    logger = Logging(level=config.log_level)
    logger = logger.create_logging()

    logger.info(f"pihole-manager started. Running on platform: {config.platform}.")

    cluster = PiHoleCluster(logger=logger, config=config)

    if options["operation"]["command"] == "add-dns-record":
        cluster.add_pihole_record(ip=options["ipaddress"], host=options["hostname"])

    elif options["operation"]["command"] == "delete-dns-record":
        cluster.delete_pihole_record(ip=options["ipaddress"], host=options["hostname"])

    elif options["operation"]["command"] == "check-record-sync":
        cluster.check_record_sync(ip=options["ipaddress"], host=options["hostname"])

    elif options["operation"]["command"] == "update-pihole":
        cluster.invoke_pihole_update()

    elif options["operation"]["command"] == "update-gravity":
        cluster.invoke_gravity_update()

    else:
        logger.error("Unsupported operation provided. Try again.")
        sys.exit(2)

    logger.info("pihole-manager has finished.")
    sys.exit(0)


if __name__ == "__main__":
    main()
