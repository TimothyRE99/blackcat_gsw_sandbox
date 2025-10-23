import argparse
from pathlib import Path
import re
import time

from playwright.sync_api import sync_playwright, Playwright, expect

TEST_ID_ATTRIBUTE = "data-test"
DATA_EXTRACTOR_ADDRESS = "http://localhost:2900/tools/dataextractor"
EXTRA_DELAY = 0.1
CLICK_DELAY = 10
EMPTY_TABLE_REGEX = re.compile(r"No data available")


def run_scraper(playwright: Playwright, download_directory: str) -> None:
    chromium = playwright.chromium
    browser = chromium.launch(headless=False)
    data_extractor = browser.new_page()
    data_extractor.goto(DATA_EXTRACTOR_ADDRESS)
    # Need to fix download to not overwrite
    data_extractor.on(
        "download",
        lambda download: download.save_as(
            Path(download_directory) / download.suggested_filename
        ),
    )

    # Replace hard-coded password with .env
    data_extractor.get_by_role("textbox", name="Password").fill("Password")
    data_extractor.get_by_role("button", name="Login").click(delay=CLICK_DELAY)

    telemetry_radio = data_extractor.get_by_role("radio", name="Telemetry")
    expect(telemetry_radio).to_be_visible()
    time.sleep(EXTRA_DELAY)
    telemetry_radio.click(delay=CLICK_DELAY, force=True)

    data_extractor.get_by_role("button", name="File").click(delay=CLICK_DELAY)
    tab_delim_radio = data_extractor.get_by_role("radio", name="Tab Delimited")
    expect(tab_delim_radio).to_be_visible()
    time.sleep(EXTRA_DELAY)
    tab_delim_radio.click(delay=CLICK_DELAY, force=True)

    mode_dropdown = data_extractor.get_by_role("button", name="Mode")
    mode_dropdown.click(delay=CLICK_DELAY)
    fill_down_checkbox = data_extractor.get_by_role("checkbox", name="Fill Down")
    expect(fill_down_checkbox).to_be_visible()
    time.sleep(EXTRA_DELAY)
    if fill_down_checkbox.is_checked():
        fill_down_checkbox.click(delay=CLICK_DELAY, force=True)
        mode_dropdown.click(delay=CLICK_DELAY)

    matlab_header_checkbox = data_extractor.get_by_role(
        "checkbox", name="Matlab Header"
    )
    expect(matlab_header_checkbox).to_be_visible()
    time.sleep(EXTRA_DELAY)
    if matlab_header_checkbox.is_checked():
        matlab_header_checkbox.click(delay=CLICK_DELAY, force=True)
        mode_dropdown.click(delay=CLICK_DELAY)

    unique_only_checkbox = data_extractor.get_by_role("checkbox", name="Unique Only")
    expect(unique_only_checkbox).to_be_visible()
    time.sleep(EXTRA_DELAY)
    if unique_only_checkbox.is_checked():
        unique_only_checkbox.click(delay=CLICK_DELAY, force=True)
        mode_dropdown.click(delay=CLICK_DELAY)

    normal_columns_radio = data_extractor.get_by_role("radio", name="Normal Columns")
    expect(normal_columns_radio).to_be_visible()
    time.sleep(EXTRA_DELAY)
    normal_columns_radio.click(delay=CLICK_DELAY, force=True)

    delete_all = data_extractor.get_by_test_id("delete-all")
    target_box = data_extractor.get_by_role("combobox").first
    packet_box = data_extractor.get_by_role("combobox").nth(1)

    target_box.click(delay=CLICK_DELAY)
    first_target = data_extractor.get_by_role("option").first
    expect(first_target).to_be_visible()
    time.sleep(EXTRA_DELAY)
    targets = data_extractor.get_by_role("option").all()
    for target in targets:
        target.click(delay=CLICK_DELAY, force=True)

        packet_box.click(delay=CLICK_DELAY)
        first_packet = data_extractor.get_by_role("option").first
        expect(first_packet).to_be_visible()
        time.sleep(EXTRA_DELAY)
        packets = data_extractor.get_by_role("option").all()
        for packet in packets[1:]:
            packet_box.click(delay=CLICK_DELAY)
            first_packet = data_extractor.get_by_role("option").first
            expect(first_packet).to_be_visible()
            time.sleep(EXTRA_DELAY)
            packet.click(delay=CLICK_DELAY, force=True)

            data_extractor.get_by_role("button", name="Add Packet").click(
                delay=CLICK_DELAY
            )

            packet_table = data_extractor.get_by_role("table")
            expect(packet_table).not_to_have_text(EMPTY_TABLE_REGEX)
            time.sleep(EXTRA_DELAY)

            data_extractor.get_by_role("button", name="Process").click(
                delay=CLICK_DELAY
            )

            time.sleep(EXTRA_DELAY)
            process_progress = data_extractor.get_by_role("progressbar")
            expect(process_progress).to_have_attribute("aria-valuenow", "100")
            delete_all.click(delay=CLICK_DELAY)
            expect(packet_table).to_have_text(EMPTY_TABLE_REGEX)
            time.sleep(EXTRA_DELAY)

        target_box.click(delay=CLICK_DELAY)
        first_target = data_extractor.get_by_role("option").first
        expect(first_target).to_be_visible()
        time.sleep(EXTRA_DELAY)

    browser.close()


def main(download_directory) -> None:
    with sync_playwright() as playwright:
        playwright.selectors.set_test_id_attribute(TEST_ID_ATTRIBUTE)
        run_scraper(playwright, download_directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="automated_data_extractor",
        description="Extract telemetry out of cosmos.",
    )
    parser.add_argument(
        "--download_directory",
        help="Path to download telemetry to.",
        type=str,
        default="../downlinked_data/telemetry_csvs",
    )
    args = parser.parse_args()

    main(args.download_directory)