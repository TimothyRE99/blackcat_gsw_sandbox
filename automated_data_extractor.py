# Need to use a webscraper
    # Probably Playwright
    # https://playwright.dev/python/docs/api/class-playwright
        # Probably use the sync version
        # -> Remove "Blackcat" dummy target so it defaults to burst response (for testing)
        # -> Create a browser, launch it, create a new page, tell it to go to specific URL (http://<wherever_cosmos_is_running>/tools/dataextractor; for testing: http://localhost:2900/tools/dataextractor)
            # find the div for each required item; grab the div id; search for it using playwright; returns that item; click on it
            # For the three checkboxes, use selector (https://playwright.dev/python/docs/api/class-selectors); find that item; check "aria-checked = False"; if not click as above
            # For the drop-downs; find the item and click; will open up with dropdown; repeat until you get to the end
            # -> Add target
            # -> Need to wait some time for processing, will hard-code for now for testing
            # -> Process
            # -> Delete all
        # Final Step: Delete all items

# /html/body/div/div/main/div/div/div[1]/div/div/div/div/div[2]/div[1]/div[3]/div/div/div[1]/div[4]/button
# /html/body/div/div/main/div/div/div[1]/div/div/div/div/div[2]/div[1]/div[3]/div/div/div[1]/div[4]/button
    # This is an example for the 'add target' button xpath
    # On the selector for Playwright, can search for this sort of xpath instead of tags
    # Check to make sure restarting cosmos doesn't change this

# /html/body/div/div[1]/main/div/div/div[1]/div/div/div/div/div[2]/header/div/button[1]
# /html/body/div/div[1]/main/div/div/div[1]/div/div/div/div/div[2]/header/div/button[1]
    # This is an example for the 'process' button xpath

# For radio buttons; use the input tag for xpath