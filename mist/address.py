# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Project      : Switch IP Check
# Created By   : Ryan M. Adzima <radzima@juniper.net>
# Created Date : 2021-08-11
# Version      : 0.1
# License      : MIT (see included LICENSE file)
# ------------------------------------------------------------------------------

"""
IP address and network utilities
"""

from ipaddress import IPv4Address, IPv4Network


def get_network(address: str, netmask: str) -> IPv4Network:
    """
    Get the network object from a given address and netmask

    :param str address: A string representing the IP address in dotted decimal format
    :param str netmask: A string representing the subnet mask in dotted decimal format
    :return IPv4Network: An IPv4Network object
    """
    net = IPv4Network(f"{address}/{netmask}", strict=False)
    return net


def check_network_contains_ip(network: IPv4Network, address: str) -> bool:
    """
    Check if a given IP address is within a given network

    :param IPv4Network network: The network to check if it contains the provided address
    :param str address: A string representing the IP address in dotted decimal format
    :return bool: A boolean value whether or not the address is in the network
    """
    ip = IPv4Address(address)
    if ip in network:
        return True
    else:
        return False
