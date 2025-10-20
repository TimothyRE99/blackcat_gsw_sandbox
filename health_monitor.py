import argparse
import configparser
from datetime import datetime, timezone
import json
from pathlib import Path

from astropy.io import fits

def parse_time():
    return()

def parse_section_list(
        section_list: list,
        downlinked_files: str,
        config: configparser.ConfigParser,
        telemetry: bool = False
) -> None:
    downlinked_files_path = Path(downlinked_files)

    for section in section_list:
        application, packet_type = section.split('.')
        for item, extrema in config[section].items():
            extrema = json.loads(extrema)

def main(
        config_file: str,
        downlinked_files: str
) -> None:
    config_file_path = Path(config_file)

    config = configparser.ConfigParser(
        # Interpolation allows variable expansion from the config file
        interpolation=configparser.ExtendedInterpolation()
    )
    config.read(config_file_path)
    
    print(type(config))

    telemetry_sections_list = json.loads(
        config['health_monitor']['telemetry_sections']
    )
    parse_section_list(telemetry_sections_list, downlinked_files, config, True)

    command_sections_list =  json.loads(
        config['health_monitor']['command_sections']
    )
    parse_section_list(command_sections_list, downlinked_files, config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = 'Parse downlinked telemetry for out-of-spec values.'
    )
    parser.add_argument(
        '-c', '--config_file',
        help = 'Path to config file.',
        type = str,
        default = './health_monitor_config.ini'
    )
    parser.add_argument(
        '-f', '--downlinked_files',
        help = 'Path to downlinked telemetry.',
        type = str,
        default = '../downlinked_data/telemetry_fits'
    )
    args = parser.parse_args()

    main(args.config_file, args.downlinked_files)
