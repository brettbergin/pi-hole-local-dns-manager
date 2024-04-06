#!/usr/bin/env python3

from .pihole import PiHole

class ClusterManager:
    def __init__(self, logger, config) -> None:
        self.logger = logger
        self.config = config

    def _create_pihole_connection(self, server, port, username, keyfile):
        """
        """
        pi_hole = PiHole(
            hostname=server,
            port=port,
            username=username,
            key_file=keyfile,
            logger=self.logger
        )

        self.logger.debug(
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
        """
        """
        for ph_host in self.config.pihole_hosts:
            ph_host = ph_host['host']
            
            self.logger.info(f"Adding DNS records to server: {ph_host['hostname']}")
            
            pihole, is_connected = self._create_pihole_connection(
                server=ph_host['hostname'],
                port=ph_host['port'],
                username=ph_host["username"],
                keyfile=ph_host["ssh_key"],
            )
            if not is_connected:
                continue

            self.logger.info(f"Adding new dns record: {ip}={host}")

            try:
                new_record = pihole.add_dns_record(ip_addr=ip, hostname=host)
                if new_record is False:
                    self.logger.debug("IP address already exists in custom dns. Skipping this host.")
                    continue
                
                if new_record is None:
                    self.logger.debug("IP address failed IPv4 validation check.")
                    continue

                if "error" in new_record.keys():
                    self.logger.error(f"Failed To add new record: {new_record['error']}")

                elif "output" in new_record.keys():
                    self.logger.info("Created new record successfully.")

                else:
                    self.logger.error("Failed to add new record. Unknown reason.")

            except Exception as err:
                self.logger.error(f"[-] Failed to add record: {err}")

            pihole.client.close()
            self.logger.debug(f"SSH connection to host: {ph_host} successfully closed.")
        return

    def delete_dns_record_from_pihole(self, ip, host):
        """
        """
        for ph_host in self.config.pihole_hosts:
            ph_host = ph_host['host']
            
            self.logger.info(f"Deleting DNS entry from server: {ph_host['hostname']}")

            pihole, is_connected = self._create_pihole_connection(
                server=ph_host['hostname'],
                port=ph_host['port'],
                username=ph_host["username"],
                keyfile=ph_host["ssh_key"],
            )
            if not is_connected:
                continue

            try:
                result = pihole.delete_dns_record(ip, host)
                if result is False:
                    self.logger.debug("Host not found in custom dns. Nothing to delete.")
                    continue
                
                if result is None:
                    self.logger.debug("IP address failed IPv4 validation check.")
                    continue

                if "error" in result.keys():
                    self.logger.error(f"Delete Record Attempt Error: {result['error']}")

                elif "output" in result.keys():
                    self.logger.info(f"Delete Record Attempt Output: {result['output']}")

                else:
                    self.logger.error("Failed to delete record. Unknown reason.")

            except Exception as del_err:
                self.logger.error(
                    f"Cannot delete DNS record {host} from server: {ph_host['hostname']}. Error: {del_err}"
                )

    def invoke_gravity_cluster_update(self):
        """
        """
        for ph_host in self.config.pihole_hosts:
            ph_host = ph_host['host']
            self.logger.info(f"Updating gravity on pihole server: {ph_host['hostname']}")

            pihole, is_connected = self._create_pihole_connection(
                server=ph_host['hostname'],
                port=ph_host['port'],
                username=ph_host["username"],
                keyfile=ph_host["ssh_key"],
            )
            if not is_connected:
                continue

            try:
                result = pihole.update_gravity()
                self.logger.debug(f"Cluster Gravity Update Response: {result}")

            except Exception as update_err:
                self.logger.error(
                    f"Cannot update gravity server: {ph_host}. Error: {update_err}"
                )

    def invoke_pihole_cluster_update(self):
        """
        """
        for ph_host in self.config.pihole_hosts:
            ph_host = ph_host['host']
            self.logger.info(f"Updating pihole server: {ph_host['hostname']}")

            pihole, is_connected = self._create_pihole_connection(
                server=ph_host['hostname'],
                port=ph_host["port"],
                username=ph_host["username"],
                keyfile=ph_host["key_file"],
            )
            if not is_connected:
                continue

            try:
                result = pihole.update_pihole()
                self.logger.debug(f"Cluster Update Response: {result}")

            except Exception as update_err:
                self.logger.error(f"Cannot update server: {ph_host['hostname']}. Error: {update_err}")

    def check_cluster_ip_sync(self, ip):
        """
        """
        found_ips = {}
        for ph_host in self.config.pihole_hosts:
            ph_host = ph_host['host']
            self.logger.info(f"Checking for ip: {ip} on host: {ph_host['hostname']}.")
            
            pihole, is_connected = self._create_pihole_connection(
                server=ph_host['hostname'],
                port=ph_host['post'],
                username=ph_host['username'],
                keyfile=ph_host['ssh_key'],
            )
            if not is_connected:
                continue

            try:
                result = pihole.check_ip_in_custom_dns(ip)
                if result:
                    found_ips[ph_host['hostname']] = ip
                self.logger.debug(f"{ip} Found in Custom DNS: {result}")

            except Exception as del_err:
                self.logger.error(
                    f"Cannot check for ip {ip} on server: {ph_host['hostname']}. Error: {del_err}"
                )
        if len(found_ips) == len(self.config.pihole_hostnames):
            self.logger.info(f"{ip} is syncronized across entire cluster.")
            return True

        else:
            self.logger.error(f"{ip} not sync'd across cluster.")
            return False
