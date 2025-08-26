import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        # Define mobile viewport for an iPhone 12
        iphone_12_viewport = {
            "width": 390,
            "height": 844,
        }

        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("http://127.0.0.1:5000/")

        # 1. Desktop view verification
        await page.screenshot(path="jules-scratch/verification/desktop_view.png")

        # 2. Mobile view verification (menu closed)
        await page.set_viewport_size(iphone_12_viewport)
        await page.screenshot(path="jules-scratch/verification/mobile_view_closed.png")

        # 3. Mobile view verification (menu open)
        navbar_toggle = page.locator("#navbarToggle")
        await navbar_toggle.click()
        # Wait for the menu to be visible if there's an animation
        await page.wait_for_selector("#navbarLinks.active")
        await page.screenshot(path="jules-scratch/verification/mobile_view_open.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
