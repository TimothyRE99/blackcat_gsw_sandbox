import argparse
import configparser
from datetime import datetime, timezone
import json
from pathlib import Path

from astropy.io import fits
import numpy as np

from blackcat_gsw_utils.email_alert import EmailConfig, send_email

def write_alert_line(
        name: str,
        timestamps_below: np.ndarray,
        timestamps_above: np.ndarray
) -> str:
    alert = f''
    if timestamps_below.size > 0:
        alert += f'\n{name} is below good region at:\n\t{timestamps_below}'
    if timestamps_above.size > 0:
        alert += f'\n{name} is above good region at:\n\t{timestamps_above}'
    return(alert)

def parse_time(
        telemetry: bool,
        idc_array: np.ndarray,
        file_contents: fits.fitsrec.FITS_rec
) -> np.ndarray:
    
    if not telemetry:
        return(idc_array)
    
    seconds_list = list(zip(
        file_contents['TIME(0)'][idc_array],
        file_contents['TIME(1)'][idc_array],
        file_contents['TIME(2)'][idc_array],
        file_contents['TIME(3)'][idc_array]
    ))
    subseconds_list = list(zip(
        file_contents['TIME(4)'][idc_array],
        file_contents['TIME(5)'][idc_array]
    ))
    timestamps = np.empty(len(seconds_list))
    for idx, seconds in enumerate(seconds_list):
        seconds = int.from_bytes(
            bytes(seconds), byteorder='big', signed=False
        )
        subseconds = int.from_bytes(
            bytes(subseconds_list[idx]), byteorder='big', signed=False
        )/65535
        timestamp = seconds + subseconds
        timestamps[idx] = timestamp
    return(timestamps)

def parse_section_list(
        section_list: list,
        downlinked_files: str,
        config: configparser.ConfigParser,
        compressed: bool,
        telemetry: bool = False
) -> str:
    alert = f''
    downlinked_files_path = Path(downlinked_files)
    for section in section_list:
        application, packet_type = section.upper().split('.')
        downlinked_file_name = f'{application}.fits'
        if compressed:
            downlinked_file_name += '.gz'
        downlinked_file = downlinked_files_path/downlinked_file_name
        downlinked_file_contents = fits.open(downlinked_file)[packet_type]
        for item, extrema in config[section].items():
            extrema = json.loads(extrema)
            item_contents = np.array(downlinked_file_contents.data[item])
            below_minimum_idc = np.where(
                item_contents < extrema.get('MIN', 0)
            )[0]
            above_maximum_idc = np.where(
                item_contents > extrema.get('MAX', 0)
            )[0]
            timestamps_below = parse_time(
                telemetry, below_minimum_idc, downlinked_file_contents.data
            )
            timestamps_above = parse_time(
                telemetry, above_maximum_idc, downlinked_file_contents.data
            )
            alert += write_alert_line(
                f'{application}.{packet_type}.{item.upper()}',
                timestamps_below, timestamps_above
            )
    return(alert)

def main(
        config_file: str,
        downlinked_files: str,
        compressed: bool
) -> None:
    config_file_path = Path(config_file)

    config = configparser.ConfigParser(
        # Interpolation allows variable expansion from the config file
        interpolation=configparser.ExtendedInterpolation()
    )
    config.read(config_file_path)

    telemetry_sections_list = json.loads(
        config['health_monitor']['telemetry_sections']
    )
    telemetry_alert = parse_section_list(
        telemetry_sections_list, downlinked_files, config, compressed,
        telemetry=True
    )

    command_sections_list =  json.loads(
        config['health_monitor']['command_sections']
    )
    command_alert = parse_section_list(
        command_sections_list, downlinked_files, config, compressed
    )

    total_alert = telemetry_alert + command_alert
    if total_alert.size > 0:
        email_config = EmailConfig.from_config(config)
        send_email(email_config, 'Downlinked Telemetry Alert', total_alert)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = 'Parse downlinked telemetry for out-of-spec values.'
    )
    parser.add_argument(
        '--config_file',
        help = 'Path to config file.',
        type = str,
        default = 'config.ini'
    )
    parser.add_argument(
        '--downlinked_files',
        help = 'Path to downlinked telemetry.',
        type = str,
        default = '../downlinked_data/telemetry_fits'
    )
    parser.add_argument(
        '-c', '--compressed',
        help = 'Compress the output fits files.',
        default = False,
        action='store_true'
    )
    args = parser.parse_args()

    main(args.config_file, args.downlinked_files, args.compressed)
