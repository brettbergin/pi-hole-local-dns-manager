#!/usr/bin/env python3

from .pihole import PiHole


class PiHoleCluster:
    def __init__(self, logger, config) -> None:
        self.logger = logger
        self.config = config

    def _create_pihole_connection(self, server, port, username, keyfile):
        """_summary_

        Args:
            server (_type_): _description_
            port (_type_): _description_
            username (_type_): _description_
            keyfile (_type_): _description_

        Returns:
            _type_: _description_
        """
        pi_hole = PiHole(
            hostname=server,
            port=port,
            username=username,
            key_file=keyfile,
            logger=self.logger,
        )

        self.logger.debug(
            f"Connecting to: {pi_hole.hostname} | Port: {pi_hole.port} | User: {pi_hole.username} | Key: {pi_hole.key_file}"
        )

        connected = pi_hole.connect()

        if not connected:
            self.logger.error(f"Server not connected. Skipping host.")
            return pi_hole, False

        else:
            self.logger.debug(f"SSH connection to {server} successful.")
            return pi_hole, True

    def add_pihole_record(self, ip, host):
        """_summary_

        Args:
            ip (_type_): _description_
            host (_type_): _description_
        """
        for ph_host in self.config.pihole_hosts:
            ph_host = ph_host["host"]

            self.logger.info(f"Adding DNS records to server: {ph_host['hostname']}")

            pihole, is_connected = self._create_pihole_connection(
                server=ph_host["hostname"],
                port=ph_host["port"],
                username=ph_host["username"],
                keyfile=ph_host["ssh_key"],
            )
            if not is_connected:
                continue

            self.logger.info(f"Adding new dns record: {host}={ip}")

            try:
                new_record = pihole.add_dns_record(ip_addr=ip, hostname=host)
                if new_record is False:
                    self.logger.error(
                        "IP address already exists in custom dns. Skipping this pihole host."
                    )
                    continue

                if new_record is None:
                    self.logger.error("IP address failed IPv4 validation check.")
                    continue

                if "error" in new_record.keys():
                    self.logger.error(
                        f"Failed To add new record: {new_record['error']}"
                    )

                elif "output" in new_record.keys():
                    self.logger.info("Created new record successfully.")

                else:
                    self.logger.error("Failed to add new record. Unknown reason.")

            except Exception as err:
                self.logger.error(f"[-] Failed to add record: {err}")

            pihole.client.close()
            self.logger.debug(f"SSH connection to host: {ph_host} successfully closed.")
        return

    def delete_pihole_record(self, ip, host):
        """_summary_

        Args:
            ip (_type_): _description_
            host (_type_): _description_
        """
        self.logger.info(f"Deleting DNS Record: {host}={ip}")
        for ph_host in self.config.pihole_hosts:
            ph_host = ph_host["host"]

            self.logger.info(f"Deleting DNS entry from server: {ph_host['hostname']}")

            pihole, is_connected = self._create_pihole_connection(
                server=ph_host["hostname"],
                port=ph_host["port"],
                username=ph_host["username"],
                keyfile=ph_host["ssh_key"],
            )
            if not is_connected:
                continue

            try:
                result = pihole.delete_dns_record(ip, host)
                if result is False:
                    continue

                if result is None:
                    self.logger.error("IP address failed IPv4 validation check.")
                    continue

                if "error" in result.keys():
                    self.logger.error(f"Delete Record Attempt Error: {result['error']}")

                elif "output" in result.keys():
                    self.logger.info("Record deletion successful.")

                else:
                    self.logger.error("Failed to delete record. Unknown reason.")

            except Exception as del_err:
                self.logger.error(
                    f"Cannot delete DNS record {host} from server: {ph_host['hostname']}. Error: {del_err}"
                )

    def invoke_gravity_update(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        for ph_host in self.config.pihole_hosts:
            ph_host = ph_host["host"]
            self.logger.info(
                f"Updating gravity on pihole server: {ph_host['hostname']}"
            )

            pihole, is_connected = self._create_pihole_connection(
                server=ph_host["hostname"],
                port=ph_host["port"],
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
        return True

    def invoke_pihole_update(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        for ph_host in self.config.pihole_hosts:
            ph_host = ph_host["host"]
            self.logger.info(f"Updating pihole server: {ph_host['hostname']}")

            pihole, is_connected = self._create_pihole_connection(
                server=ph_host["hostname"],
                port=ph_host["port"],
                username=ph_host["username"],
                keyfile=ph_host["ssh_key"],
            )
            if not is_connected:
                continue

            try:
                result = pihole.update_pihole()
                self.logger.debug(f"Cluster Update Response: {result}")

            except Exception as update_err:
                self.logger.error(
                    f"Cannot update server: {ph_host['hostname']}. Error: {update_err}"
                )
        return True

    def check_record_sync(self, ip, host):
        """_summary_

        Args:
            ip (_type_): _description_
            host (_type_): _description_

        Returns:
            _type_: _description_
        """
        found_ips = {}
        for ph_host in self.config.pihole_hosts:
            ph_host = ph_host["host"]
            self.logger.info(f"Checking for ip: {ip} on host: {ph_host['hostname']}.")

            pihole, is_connected = self._create_pihole_connection(
                server=ph_host["hostname"],
                port=ph_host["port"],
                username=ph_host["username"],
                keyfile=ph_host["ssh_key"],
            )
            if not is_connected:
                continue

            try:
                result = pihole.check_record_in_dns(ip, host)
                if result:
                    found_ips[ph_host["hostname"]] = ip
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
