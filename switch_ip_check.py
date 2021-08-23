#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Project      : Switch IP Check
# Created By   : Ryan M. Adzima <radzima@juniper.net>
# Created Date : 2021-08-11
# Version      : 0.1
# License      : MIT (see included LICENSE file)
# ------------------------------------------------------------------------------

"""
Quickly assess the validity of the Mist configurations across your entire organi-
-zation against the existing (un-managed) switch network configurations to ensure
that connectivity will remain after moving to a managed configuration.

    usage: switch_ip_check.py -o <Org ID> -t <API Token> [-i <CSV FILE> | -a] [-x] [-O <CSV FILE>] [-q | -d | -l LEVEL] [--hide] [-h]

    Required arguments:
      -o <Org ID>, --org <Org ID>
                            Mist organization ID
      -t <API Token>, --token <API Token>
                            Mist API token

    Input options:
      -i <CSV FILE>, --infile <CSV FILE>
                            CSV file containing switches to be checked (default: ./switches.csv)
      -a, --all             Check entire organization inventory

    Output arguments:
      -x, --export          Export checks to a CSV file (use the -O/--outfile option to set location, default: ./checked_switches.csv)
      -O <CSV FILE>, --outfile <CSV FILE>
                            Export switch data to CSV (default: ./checked_switches.csv)

    Display arguments:
      -q, --quiet           Hide terminal output (add '--hide' to also hide the results table)
      -d, --debug           Show terminal output at the DEBUG level
      -l LEVEL, --level LEVEL
                            Logging level for terminal output (choices: 'DEBUG', 'INFO', 'WARNING', 'ERROR')
      --hide                Hide results table after completing checks

    Additional arguments/options:
      -h, --help            Show this help message and exit

"""

import sys
import argparse
from mist import logger, Org
from logging import DEBUG, ERROR
from csv import DictReader


def process_csv(csvfile: str) -> (list, list):
    """
    Process CSV list of switches to extract the MAC addresses of switches to check

    :param str csvfile: String representation of the CSV location (relative or absolute)
    :return (list, list): Lists containing the sites and switch MAC addresses
    """
    csv_data = list()
    try:
        with open(csvfile, 'r') as csv_stream:
            reader = DictReader(csv_stream)
            for row in reader:
                csv_data.append(row)
    except FileNotFoundError:
        logger.warning(f"CSV file '{csvfile}' not loaded, file not found.")
        return None, None
    except Exception as exc:
        raise exc
    try:
        for switch in csv_data:
            switch['mac'] = switch['mac_address'].replace(":", "").lower()
            del switch['mac_address']
            switch['site'] = switch['site_name']
            del switch['site_name']
    except Exception as exc:
        raise exc
    switch_list = list({s['mac'] for s in csv_data})
    site_list = list({s['site'] for s in csv_data})
    return site_list, switch_list


def process_args(arguments: argparse.Namespace):
    """
    Process the logging/output/verbosity script arguments

    :param argparse.Namespace arguments: Parsed arguments namespace object
    """
    if arguments.level:
        logger.setLevel(arguments.level)
    elif arguments.quiet:
        logger.setLevel(ERROR)
    elif arguments.debug:
        logger.setLevel(DEBUG)
    del arguments.level, arguments.quiet, arguments.debug


def parse() -> argparse.Namespace:
    """
    Parse the CLI arguments of this script

    :return argparse.Namespace: The namespace object containing the argument key/value pairs
    """
    parser = argparse.ArgumentParser(add_help=False)

    # Required options/arguments group
    req_options = parser.add_argument_group("Required arguments")
    req_options.add_argument('-o', '--org',
                             type=str,
                             required=True,
                             metavar="<Org ID>",
                             help="Mist organization ID")
    req_options.add_argument('-t', '--token',
                             type=str,
                             required=True,
                             metavar="<API Token>",
                             help="Mist API token")

    # Input options/arguments group
    input_group = parser.add_argument_group("Input options")
    input_options = input_group.add_mutually_exclusive_group()
    input_options.add_argument('-i', '--infile',
                               type=str,
                               default="./switches.csv",
                               metavar="<CSV FILE>",
                               help="CSV file containing switches to be checked (default: ./switches.csv)")
    input_options.add_argument('-a', '--all',
                               default=False,
                               action="store_true",
                               help="Check entire organization inventory")

    # Output options/arguments group
    output_options = parser.add_argument_group("Output arguments")
    output_options.add_argument('-x', '--export',
                                default=False,
                                action="store_true",
                                help="Export checks to a CSV file (use the -O/--outfile option to set location, default: ./checked_switches.csv)")
    output_options.add_argument('-O', '--outfile',
                                type=str,
                                default="./checked_switches.csv",
                                metavar="<CSV FILE>",
                                help="Export switch data to CSV (default: ./checked_switches.csv)")

    # Display options/arguments group
    display_options = parser.add_argument_group("Display arguments")
    verbosity = display_options.add_mutually_exclusive_group()
    verbosity.add_argument('-q', '--quiet',
                           default=False,
                           action="store_true",
                           help="Hide terminal output (add '--hide' to also hide the results table)")
    verbosity.add_argument('-d', '--debug',
                           default=False,
                           action="store_true",
                           help="Show terminal output at the DEBUG level")
    verbosity.add_argument('-l', '--level',
                           type=str,
                           choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                           metavar="LEVEL",
                           help="Logging level for terminal output (choices: 'DEBUG', 'INFO', 'WARNING', 'ERROR')")
    display_options.add_argument('--hide',
                                 default=False,
                                 action="store_true",
                                 help="Hide results table after completing checks")

    # Other miscellaneous options/arguments group
    other_options = parser.add_argument_group("Additional arguments/options")
    other_options.add_argument('-h', '--help',
                               action="help",
                               help="Show this help message and exit")

    # Parse the script arguments
    a = parser.parse_args()

    # Process logging/output/verbosity script arguments
    process_args(arguments=a)

    # Process input file if present
    if a.infile and not a.all:
        a.sites, a.switches = process_csv(csvfile=a.infile)
        del a.all
    elif a.all:
        a.sites = a.switches = None
        del a.infile

    # Process output file if present
    if a.export:
        pass
    else:
        del a.outfile
    return a


def main():
    args = parse()
    logger.info(f"ARGS: {args}")
    org = Org(org_id=args.org, token=args.token, site_list=args.sites)
    logger.info(f"SITES: {len(org.sites)}")
    logger.info(f"SITE NAMES: {[(s['name'],s['id']) for s in org.sites]}")
    logger.info(f"SWITCHES: {len(org.switches)}")
    logger.info(f"SWITCHES: {[(s['name'],s['device_id']) for s in org.switches]}")
    if args.switches:
        switch_check_output = org.check_switches(switch_list=args.switches)
    else:
        switch_check_output = org.check_switches()
    if args.export:
        org.export_switches(csv_file=args.outfile)
    if not args.hide:
        print(switch_check_output)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("User cancelled, exiting.")
    except Exception as e:
        logger.error(f"Error: {e}")
