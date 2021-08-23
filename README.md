# Switch IP Check

Quickly assess the validity of the Mist configurations across your entire organization against the existing (un-managed) switch network configurations to ensure that connectivity will remain after moving to a managed configuration.

## Installation
Download the package and run `python3 switch_ip_check.py ...` with the appropriate options.

**No external library/module requirements - uses all standard library packages.**
## Usage
```bash
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
```

## License
Licensed under the MIT license, see [LICENSE](LICENSE) for license text.
