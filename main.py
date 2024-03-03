#!/usr/bin/env python3

import argparse
import os
import sys


from pihole_dns.config import Logging, Config
from pihole_dns.cluster import ClusterManager

logger = Logging(here=os.path.dirname(os.path.abspath(__file__))).create_logging()
config = Config()
ssh = config.sshconfig


def parse_arguments():
    parser = argparse.ArgumentParser(description="add-dns-record.")
    parser.add_argument(
        "--operation",
        "-o",
        type=str,
        required=True,
        help="Operation To Execute Against PiHole Cluster",
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
    logger.info(f"Starting pihole-manager. Running on platform: {config.platform}.")

    args = parse_arguments()
    cluster = ClusterManager(logger=logger, config=config, ssh=ssh)

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

    else:
        logger.error(
            "Unsupported pihole cluster manager operation provided. Try again."
        )
        sys.exit(-2)

    logger.info("Script Complete.")
    sys.exit(0)
