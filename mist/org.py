# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Project      : Switch IP Check
# Created By   : Ryan M. Adzima <radzima@juniper.net>
# Created Date : 2021-08-11
# Version      : 0.1
# License      : MIT (see included LICENSE file)
# ------------------------------------------------------------------------------

"""
Organization definition and methods for evaluating the switches within an organization
"""

from typing import List
from .api import API
from .logger import logger, TextColors
from .address import get_network, check_network_contains_ip


# noinspection PyTypeChecker
class Org:
    """
    Organization definition and methods for evaluating the switches within an organization
    """

    oid: str = ""
    token: str = ""
    api: API = None
    host: str = "api.mist.com"
    sites: list = list()
    network_templates: list = list()
    switches: list = list()

    def __init__(self, org_id: str, token: str, site_list: list = None):
        """
        Initialize the Org object

        :param str org_id: Mist organization identifier string
        :param str token: Mist API authentication token
        """
        self.oid = org_id
        self.token = token
        self.api = API(org_id=org_id, token=token)

        logger.debug("Loading sites...")
        self.sites = list()
        self.load_sites(site_list=site_list)
        logger.debug(f"Loaded {len(self.sites)} sites.")

        logger.debug("Loading network templates from organization...")
        self.network_templates = list()
        self.load_network_templates()
        logger.debug(f"Loaded {len(self.network_templates)} network templates.")

        logger.debug("Matching and assigning network template data to sites...")
        self.match_network_template_to_site()
        logger.debug("Finished network template data correlation.")

        logger.debug("Loading switches...")
        self.switches = list()
        self.load_switches()
        logger.debug(f"Loaded {len(self.switches)} switches.")

    #### INITIAL LOADING METHODS ####

    def load_sites(self, site_list: list = None):
        """
        Get the organization sites, if a list of names is not provided then all sites will be loaded

        :param list site_list: A list containing the name of the sites to load
        """
        try:
            sites = self.api.get(host=self.host, endpoint=f"/api/v1/orgs/{self.oid}/sites")
        except Exception as e:
            logger.error(f"{TextColors.FAIL}Error getting org sites:{TextColors.ENDC} {e}")
            raise e
        if site_list:
            sites = [s for s in sites if s['name'] in site_list]
        self.sites = sites

    def load_network_templates(self) -> List:
        """
        Get the network templates for the organization
        """
        try:
            network_templates = self.api.get(host=self.host, endpoint=f"/api/v1/orgs/{self.oid}/networktemplates")
        except Exception as e:
            logger.error(f"{TextColors.FAIL}Error getting network templates:{TextColors.ENDC} {e}")
            raise e
        self.network_templates = network_templates

    def match_network_template_to_site(self):
        """
        Align sites with their respective network templates and add the contents of the template to the site object
        """
        for site in self.sites:
            if 'networktemplate_id' in site and site['networktemplate_id']:
                matched_network_template = [nt for nt in self.network_templates if nt['id'] == site['networktemplate_id']]
                if len(matched_network_template) >= 1:
                    site['network_template'] = matched_network_template[0]

    def load_switches(self):
        """
        Load the organization switches from the Mist API
        """
        new_switches = list()
        for site in self.sites:
            switches = self.get_switches_stats(site_id=site['id'])
            for switch in switches:
                if len(switch['name']) < 1:
                    switch['name'] = ':'.join([switch['mac'][i:i + 2].upper() for i in range(0, len(switch['mac']), 2)])
                new_switch = {
                    "name":      switch['name'],
                    "site":      site['name'],
                    "site_id":   site['id'],
                    "device_id": switch['id'],
                    "mac":       switch['mac'],
                    "mac_str":   ':'.join([switch['mac'][i:i + 2].upper() for i in range(0, len(switch['mac']), 2)]),
                    "ip_config": switch['ip_config'],
                    "ip_actual": switch['ip_stat'],
                    "net_obj": get_network(address=switch['ip_config']['ip'], netmask=switch['ip_config']['netmask']) if 'ip' in switch['ip_config'] else None
                }
                for vlan, addr in new_switch['ip_actual']['ips'].items():
                    if new_switch['ip_actual']['ip'] == addr:
                        new_switch['ip_actual']['vlan'] = vlan.strip('vlan')
                    else:
                        new_switch['ip_actual']['vlan'] = 0
                if new_switch['ip_config']['network'] and new_switch['ip_config']['network'] != "default":
                    new_switch['ip_config']['vlan'] = site['network_template']['networks'][new_switch['ip_config']['network']]['vlan_id']
                    logger.debug(f"Matched {new_switch['name']} management network '{new_switch['ip_config']['network']}' to VLAN {new_switch['ip_config']['vlan']}")
                elif new_switch['ip_config']['network'] and new_switch['ip_config']['network'] == "default":
                    new_switch['ip_config']['vlan'] = 1
                    logger.debug(f"Matched {new_switch['name']} management network '{new_switch['ip_config']['network']}' to VLAN {new_switch['ip_config']['vlan']}")
                else:
                    new_switch['ip_config']['vlan'] = 0
                    logger.error(f"Did not match {new_switch['name']} management network '{new_switch['ip_config']['network']}' to VLAN {new_switch['ip_config']['vlan']}")
                new_switches.append(new_switch)
        self.switches = new_switches

    #### STATS RETRIEVAL METHODS ####

    def get_switches_stats(self, site_id: str) -> List:
        """
        Get the stats and active config of the switches at a given site

        :param str site_id: The site identifier string
        :return list: A list containing the stats and config of all switches at a given site
        """
        try:
            stats = self.api.get(host=self.host, endpoint=f"/api/v1/sites/{site_id}/stats/devices?type=switch")
        except Exception as e:
            logger.error(f"{TextColors.FAIL}Error getting switch stats:{TextColors.ENDC} {e}")
            raise e
        return stats

    # def get_switch_stats(self, site_id: str, switch_id: str) -> Dict:
    #     """
    #     Get the stats and active config of the given switch
    #
    #     :param str site_id: The site identifier string
    #     :param str switch_id: The switch identifier string
    #     :return dict: A dictionary containing the stats and config of the switch
    #     """
    #     try:
    #         stats = self.api.get(host=self.host, endpoint=f"/api/v1/sites/{site_id}/stats/devices/{switch_id}")
    #     except Exception as e:
    #         logger.error(f"{TextColors.FAIL}Error getting switch stats:{TextColors.ENDC} {e}")
    #         raise e
    #     return stats

    #### VALIDATION METHODS ####

    def check_switches(self, switch_list: list = None) -> str:
        """
        Check the switch config against the Mist cloud config

        :param list switch_list: A list of MAC addresses to check, if None all switches will be checked
        :return str: A string containing a table of output for displaying the results of the check
        """
        if switch_list:
            switches = [s for s in self.switches for x in switch_list if s['mac'] == x]
        else:
            switches = self.switches
        switch_output = f"\n{TextColors.BOLD}{TextColors.UNDERLINE}{'Name':^24}{TextColors.ENDC} {TextColors.BOLD}{TextColors.UNDERLINE}{'MAC':^18}{TextColors.ENDC} {TextColors.BOLD}{TextColors.UNDERLINE}{'Network':^20}{TextColors.ENDC} {TextColors.BOLD}{TextColors.UNDERLINE}{'VLAN':^6}{TextColors.ENDC} {TextColors.BOLD}{TextColors.UNDERLINE}{'Result':^8}{TextColors.ENDC} {TextColors.BOLD}{TextColors.UNDERLINE}{'Additional Info':^90}{TextColors.ENDC}\n"
        for switch in switches:
            try:
                switch['ip_match'] = (switch['ip_config']['ip'] == switch['ip_actual']['ip']) if 'ip' in switch['ip_config'] else False
                switch['netmask_match'] = (switch['ip_config']['netmask'] == switch['ip_actual']['netmask']) if 'netmask' in switch['ip_config'] else False
                switch['gateway_match'] = (switch['ip_config']['gateway'] == switch['ip_actual']['gateway']) if 'gateway' in switch['ip_config'] else False
                switch['vlan_match'] = (switch['ip_config']['vlan'] == switch['ip_actual']['vlan'])

                if switch['net_obj']:
                    switch['gateway_on_net'] = check_network_contains_ip(network=switch['net_obj'], address=switch['ip_config']['gateway'])
                else:
                    switch['gateway_on_net'] = False
                if switch['ip_match'] and switch['gateway_match'] and switch['gateway_on_net']:  # and switch['vlan_match']:
                    result = "PASS"
                    reason = "None"
                else:
                    result = "FAIL"
                    if not switch['ip_match'] and switch['gateway_match']:
                        reason = f"{TextColors.WARNING}Management Interface IP Mis-match{TextColors.ENDC}"
                    elif switch['ip_match'] and not switch['gateway_match']:
                        reason = f"{TextColors.WARNING}Management Interface Gateway Mis-match{TextColors.ENDC}"
                    elif not switch['ip_match'] and not switch['gateway_match']:
                        reason = f"{TextColors.WARNING}Management Interface IP/Gateway Mis-match{TextColors.ENDC}"
                    else:
                        reason = f"{TextColors.WARNING}Unknown failure{TextColors.ENDC}"
                    if not switch['gateway_on_net']:
                        reason = f"{TextColors.WARNING}Management Interface IP/Gateway Missing or Dynamic{TextColors.ENDC}"
                    if not switch['vlan_match']:
                        reason = f"{TextColors.WARNING}Management Interface VLAN Incorrect: Configured as VLAN {switch['ip_config']['vlan']} but is actually using VLAN {switch['ip_actual']['vlan']}{TextColors.ENDC}"
                switch_output = f"{switch_output}{TextColors.BOLD}{switch['name']:<24.23}{TextColors.ENDC} {switch['mac_str']:<18} {switch['ip_config']['network']:<20} {switch['ip_config']['vlan']:<6} {TextColors.OK if result == 'PASS' else TextColors.FAIL}{result:<8}{TextColors.ENDC} {reason:<90}\n"
            except Exception as e:
                logger.error(f"{TextColors.FAIL}Error processing device details:{TextColors.ENDC} {switch['name']}")
                switch_output = f"{switch_output}{switch['name']:<24} {switch['mac_str']:<18} {TextColors.WARNING}Error processing device:{TextColors.ENDC} {e}\n"
                continue
        return switch_output

    #### DATA EXPORT METHODS ####

    def export_switches(self, csv_file: str):
        """
        Export the switch evaluation results to a CSV file

        :param str csv_file: File that the data will be written to. This will overwrite existing files.
        :return: None
        """
        if csv_file and len(self.switches) >= 1:
            # TODO: Output to CSV
            logger.debug(f"Exporting switch validation results to: {csv_file}")
            pass
