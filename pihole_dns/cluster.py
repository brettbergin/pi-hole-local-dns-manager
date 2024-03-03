#!/usr/bin/env python3

from pihole import PiHole

class ClusterManager:
    def __init__(self, logger, config, ssh) -> None:
        self.logger = logger
        self.config = config
        self.ssh = ssh

    def create_pihole_connection(self, server, port, username, keyfile):
        pi_hole = PiHole(
            hostname=server,
            port=port,
            username=username,
            key_file=keyfile,
        )

        self.logger.info(
            f"Connecting to: {pi_hole.hostname} | Port: {pi_hole.port} | User: {pi_hole.username} | Key: {pi_hole.key_file}"
        )

        connected = pi_hole.connect()

        if not connected:
            self.logger.error(f"Server not connected. Skipping host.")
            return pi_hole, False

        else:
            self.logger.info(f"SSH connection to {server} successful.")
            return pi_hole, True


    def add_dns_record_to_pihole(self, ip, host):

        for ph_server in self.ssh["hostnames"]:
            self.logger.info(f"Adding DNS records to server: {ph_server}")

            pihole, is_connected = self.create_pihole_connection(
                server=ph_server,
                port=self.ssh["port"],
                username=self.ssh["username"],
                keyfile=self.ssh["key_file"],
            )
            if not is_connected:
                continue

            self.logger.info(f"Adding new dns record: {ip}={host}")

            try:
                new_record = pihole.add_dns_record(ip_addr=ip, hostname=host)

                if "error" in new_record.keys():
                    self.logger.error(f"Failed To add new record: {new_record['error']}")

                elif "output" in new_record.keys():
                    self.logger.info("Created new record successfully.")

                else:
                    self.logger.error("Failed to add new record. Unknown reason.")

            except Exception as err:
                self.logger.error(f"[-] Failed to add record: {err}")

            pihole.client.close()
            self.logger.debug(f"SSH connection to host: {ph_server} successfully closed.")
        return


    def invoke_gravity_cluster_update(self):
        for ph_server in self.ssh["hostnames"]:
            self.logger.info(f"Updating gravity on pihole server: {ph_server}")

            pihole, is_connected = self.create_pihole_connection(
                server=ph_server,
                port=self.ssh["port"],
                username=self.ssh["username"],
                keyfile=self.ssh["key_file"],
            )
            if not is_connected:
                continue

            try:
                result = pihole.update_gravity()
                self.logger.debug(f"Cluster Gravity Update Response: {result}")

            except Exception as update_err:
                self.logger.error(
                    f"Cannot update gravity server: {ph_server}. Error: {update_err}"
                )


    def invoke_pihole_cluster_update(self):
        for ph_server in self.ssh["hostnames"]:
            self.logger.info(f"Updating pihole server: {ph_server}")

            pihole, is_connected = self.create_pihole_connection(
                server=ph_server,
                port=self.ssh["port"],
                username=self.ssh["username"],
                keyfile=self.ssh["key_file"],
            )
            if not is_connected:
                continue

            try:
                result = pihole.update_pihole()
                self.logger.debug(f"Cluster Update Response: {result}")

            except Exception as update_err:
                self.logger.error(f"Cannot update server: {ph_server}. Error: {update_err}")


    def delete_dns_record_from_pihole(self, ip, host):
        for ph_server in self.ssh["hostnames"]:
            self.logger.info(f"Deleting DNS entry from server: {ph_server}")

            pihole, is_connected = self.create_pihole_connection(
                server=ph_server,
                port=self.ssh["port"],
                username=self.ssh["username"],
                keyfile=self.ssh["key_file"],
            )
            if not is_connected:
                continue

            try:
                result = pihole.delete_dns_record(ip, host)
                self.logger.debug(f"DNS Record Delete Response: {result}")

            except Exception as del_err:
                self.logger.error(
                    f"Cannot delete DNS record {host} from server: {ph_server}. Error: {del_err}"
                )
