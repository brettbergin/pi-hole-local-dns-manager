#!/usr/bin/env python3

import argparse
import os
import sys


from pihole_manager.config import Logging, Config
from pihole_manager.cluster import ClusterManager


def parse_arguments():
    parser = argparse.ArgumentParser(description="SSH Client to Manage Pi Hole DNS Configurations.")
    parser.add_argument(
        "--operation",
        "-o",
        type=str,
        required=True,
        help="Available Operations: add-dns-record, delete-dns-record, update-pihole, update-gravity, check-ip-sync",
    )
    parser.add_argument(
        "--hostname",
        "-n",
        type=str,
        help="DNS hostname To Register with PiHole Infrastructure.",
    )
    parser.add_argument("--ipaddress", "-i", type=str, help="IP address")
    return parser.parse_args()


if __name__ == "__main__":
    config = Config(file_abspath=os.path.dirname(os.path.abspath(__file__)))
    
    logger = Logging(level=config.log_level)
    logger = logger.create_logging()

    logger.info(f"pihole-manager started. Running on platform: {config.platform}.")

    args = parse_arguments()
    
    cluster = ClusterManager(logger=logger, config=config)

    if str(args.operation).lower() == "add-dns-record":
        if args.hostname and args.ipaddress:
            cluster.add_dns_record_to_pihole(ip=args.ipaddress, host=args.hostname)

        else:
            logger.error("Missing IP address or Hostname argument. Quitting.")
            sys.exit(-1)

    elif str(args.operation).lower() == "delete-dns-record":
        if args.hostname and args.ipaddress:
            cluster.delete_dns_record_from_pihole(ip=args.ipaddress, host=args.hostname)

        else:
            logger.error("Missing IP address or Hostname argument. Quitting.")
            sys.exit(-1)

    elif str(args.operation).lower() == "update-pihole":
        logger.info("Checking For Updates Across Entire Pihole Cluster.")
        cluster.invoke_pihole_cluster_update()

    elif str(args.operation).lower() == "update-gravity":
        logger.info("Checking For Gravity Updates Across Entire Pihole Cluster.")
        cluster.invoke_gravity_cluster_update()

    elif str(args.operation).lower() == "check-ip-sync":
        logger.info("Checking if IP is registered in all servers.")

        if args.ipaddress:
            cluster.check_cluster_ip_sync(ip=args.ipaddress)

        else:
            logger.error("Missing IP address or Hostname argument. Quitting.")
            sys.exit(-1)

    else:
        logger.error(
            "Unsupported pihole cluster manager operation provided. Try again."
        )
        sys.exit(-2)

    logger.info("Script Complete.")
    sys.exit(0)
