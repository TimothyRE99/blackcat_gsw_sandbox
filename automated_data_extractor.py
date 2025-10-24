import argparse
from pathlib import Path
import re

from playwright.sync_api import sync_playwright, Playwright, expect

TEST_ID_ATTRIBUTE = "data-test"
DATA_EXTRACTOR_ADDRESS = "http://localhost:2900/tools/dataextractor"
EXTRA_DELAY = 100
EMPTY_TABLE_REGEX = re.compile(r"No data available")


def run_scraper(playwright: Playwright, download_directory: str) -> None:
    chromium = playwright.chromium
    browser = chromium.launch(downloads_path=Path(download_directory), headless=False)
    data_extractor = browser.new_page()
    data_extractor.goto(DATA_EXTRACTOR_ADDRESS)

    # ZZZ - Replace hard-coded password with .env
    data_extractor.get_by_role("textbox", name="Password").fill("Password")
    data_extractor.get_by_role("button", name="Login").click()

    telemetry_radio = data_extractor.get_by_role("radio", name="Telemetry")
    expect(telemetry_radio).to_be_visible()
    telemetry_radio.scroll_into_view_if_needed()  # Forces stability check
    telemetry_radio.click(force=True)

    data_extractor.get_by_role("button", name="File").click()
    tab_delim_radio = data_extractor.get_by_role("radio", name="Tab Delimited")
    expect(tab_delim_radio).to_be_visible()
    tab_delim_radio.scroll_into_view_if_needed()  # Forces stability check
    tab_delim_radio.click(force=True)

    mode_dropdown = data_extractor.get_by_role("button", name="Mode")
    mode_dropdown.click()
    fill_down_checkbox = data_extractor.get_by_role("checkbox", name="Fill Down")
    expect(fill_down_checkbox).to_be_visible()
    fill_down_checkbox.scroll_into_view_if_needed()
    if fill_down_checkbox.is_checked():
        fill_down_checkbox.click(force=True)
        mode_dropdown.click()

    matlab_header_checkbox = data_extractor.get_by_role(
        "checkbox", name="Matlab Header"
    )
    expect(matlab_header_checkbox).to_be_visible()
    matlab_header_checkbox.scroll_into_view_if_needed()  # Forces stability check
    if matlab_header_checkbox.is_checked():
        matlab_header_checkbox.click(force=True)
        mode_dropdown.click()

    unique_only_checkbox = data_extractor.get_by_role("checkbox", name="Unique Only")
    expect(unique_only_checkbox).to_be_visible()
    unique_only_checkbox.scroll_into_view_if_needed()  # Forces stability check
    if unique_only_checkbox.is_checked():
        unique_only_checkbox.click(force=True)
        mode_dropdown.click()

    normal_columns_radio = data_extractor.get_by_role("radio", name="Normal Columns")
    expect(normal_columns_radio).to_be_visible()
    normal_columns_radio.scroll_into_view_if_needed()  # Forces stability check
    normal_columns_radio.click(force=True)

    delete_all = data_extractor.get_by_test_id("delete-all")
    target_box = data_extractor.get_by_role("combobox").first
    packet_box = data_extractor.get_by_role("combobox").nth(1)

    target_box.click()
    first_target = data_extractor.get_by_role("option").first
    expect(first_target).to_be_visible()
    first_target.scroll_into_view_if_needed()  # Forces stability check
    targets = data_extractor.get_by_role("option").all()

    # Need to load in all targets, not just ones that start active
    prev_len = 0
    curr_len = len(targets)
    while curr_len != prev_len:
        data_extractor.keyboard.press("ArrowUp")  # Goes to last loaded element
        first_target.scroll_into_view_if_needed()  # Forces stability check
        targets = data_extractor.get_by_role("option").all()
        # Open and close box to get back to start
        target_box.click()
        target_box.click()
        expect(first_target).to_be_visible()
        first_target.scroll_into_view_if_needed()  # Forces stability check
        prev_len = curr_len
        curr_len = len(targets)

    for target in targets:
        target.click(force=True)

        packet_box.click()
        first_packet = data_extractor.get_by_role("option").first
        expect(first_packet).to_be_visible()
        first_packet.scroll_into_view_if_needed()  # Forces stability check
        packets = data_extractor.get_by_role("option").all()
        for packet in packets[1:]:
            packet.click(force=True)

            data_extractor.get_by_role("button", name="Add Packet").click()

            packet_table = data_extractor.get_by_role("table")
            expect(packet_table).not_to_have_text(EMPTY_TABLE_REGEX)

            data_extractor.get_by_role("button", name="Process").click()

            data_extractor.wait_for_timeout(EXTRA_DELAY)  # Avoid racing page
            process_progress = data_extractor.get_by_role("progressbar")
            expect(process_progress).to_have_attribute("aria-valuenow", "100")
            delete_all.click()
            expect(packet_table).to_have_text(EMPTY_TABLE_REGEX)

            packet_box.click()
            first_packet = data_extractor.get_by_role("option").first
            expect(first_packet).to_be_visible()
            first_packet.scroll_into_view_if_needed()  # Forces stability check

        target_box.click()
        first_target = data_extractor.get_by_role("option").first
        expect(first_target).to_be_visible()
        first_target.scroll_into_view_if_needed()  # Forces stability check

    # ZZZ - HANDLE RENAMING DOWNLOADS

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
