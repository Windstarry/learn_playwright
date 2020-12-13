import asyncio
from playwright import async_playwright
import pysnooper



async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False,slowMo=200)
        page = await browser.newPage()
        await page.addInitScript(source='''
                                const newProto = navigator.__proto__;
                                delete newProto.webdriver;
                                navigator.__proto__ = newProto;
        ''')
        #page.on('dialog',lambda dialog:print(dialog.message,dialog.type))
        await page.goto('https://antispider1.scrape.center/',waitUntil='networkidle')
        # js2 = '''() => {
        #             alert (
        #                 window.navigator.webdriver
        #             )
        #         }'''
        # async with page.expect_dialog() as dialog:
        #         await page.evaluate(js2)
        #     #print("弹出窗口，查询navigator.wendriver的值")
        # await page.keyboard.press("Enter")
        await page.screenshot(path='example-firefox.png')
        await browser.close()

asyncio.get_event_loop().run_until_complete(main())