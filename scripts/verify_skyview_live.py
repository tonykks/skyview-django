import asyncio
import os
import sys
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="chrome")
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        url = "https://skyview.pythonanywhere.com/"
        print(f"Navigating to {url}...")
        resp = await page.goto(url, wait_until="networkidle")
        print(f"Status: {resp.status}")

        # Capture screenshot
        screenshot_dir = r"c:\Users\김광수\Desktop\skyview_final\docs\screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, "skyview_live_current.png")
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"Screenshot saved to: {screenshot_path}")

        # Inspect main-nav
        nav_buttons = await page.locator("nav.main-nav a.nav-circle").all()
        print(f"Found {len(nav_buttons)} nav buttons:")
        menu_info = []
        for btn in nav_buttons:
            text = (await btn.text_content()).strip()
            href = await btn.get_attribute("href")
            tooltip = await btn.get_attribute("data-tooltip")
            aria = await btn.get_attribute("aria-label")
            classes = await btn.get_attribute("class")
            info = {
                "text": text,
                "href": href,
                "tooltip": tooltip,
                "aria_label": aria,
                "class": classes
            }
            menu_info.append(info)
            print(f"  - [{text}] tooltip='{tooltip}', href='{href}', class='{classes}'")

        # Check response headers (like server, date, etc)
        headers = resp.headers
        print("\nResponse headers of interest:")
        for h in ['date', 'server', 'etag', 'last-modified', 'cache-control']:
            if h in headers:
                print(f"  {h}: {headers[h]}")

        await browser.close()
        return menu_info

if __name__ == "__main__":
    asyncio.run(main())
