import playwright
from playwright.sync_api import Playwright


def main(playwright: Playwright):
    #打开浏览器的实例，使用chromium
    browser = playwright.chromium.launch(headless=False,slowMo=2000)
    #打开页面的实例
    page = browser.newPage(viewport=0)
    #页面设置一个按钮，clickme，点击会跳转到http://webkit.org
    page.setContent(
        "<button id=button onclick=\"window.open('http://webkit.org', '_blank')\">Click me</input>"
    )
    #如果页面能够跳转新的页面，点击button按钮
    with page.expect_popup() as popup_info:
        page.click("#button")
    print(popup_info.value)
    #查看浏览器窗口数量
    print("Contexts in browser: %d" % len(browser.contexts))
    #浏览器打开新的窗口
    print("Creating context...")
    context = browser.newContext(viewport=0)
    print("Contexts in browser: %d" % len(browser.contexts))
    #查看新的窗口打开的页面数量
    print("Pages in context: %d" % len(context.pages))
    #窗口打开1个新的页面
    print("\nCreating page1...")
    page1 = context.newPage()
    print("Pages in context: %d" % len(context.pages))
    #设置page1发生相关事件时，打印相关信息
    page1.on("framenavigated", lambda frame: print("Frame navigated to %s" % frame.url))
    page1.on("request", lambda request: print("Request %s" % request.url))
    page1.on(
        "requestFinished", lambda request: print("Request finished %s" % request.url)
    )
    page1.on(
        "response",
        lambda response: print(
            "Response %s, request %s in frame %s"
            % (response.url, response.request.url, response.frame.url)
        ),
    )
    print("Navigating page1 to https://example.com...")
    page1.goto("https://example.com")
    print("Page1 main frame url: %s" % page1.mainFrame.url)
    print("Page1 tile: %s" % page1.title())
    print("Frames in page1: %d" % len(page1.frames))
    page1.screenshot(path="./date/example.png")

    print("\nCreating page2...")
    page2 = context.newPage()
    page2.on("framenavigated", lambda frame: print("Frame navigated to %s" % frame.url))

    print("Navigating page2 to https://webkit.org...")
    page2.goto("https://webkit.org")
    print("Page2 tile: %s" % page2.title())
    print("Pages in context: %d" % len(context.pages))

    print("\nQuerying body...")
    body1 = page1.querySelector("body")
    assert body1
    print("Body text %s" % body1.textContent())

    print("Closing page1...")
    page1.close()
    print("Pages in context: %d" % len(context.pages))

    print("Navigating page2 to https://www.163.com...")
    page2.goto("https://www.163.com",timeout=60000)
    print("Page2 main frame url: %s" % page2.mainFrame.url)
    print("Page2 tile: %s" % page2.title())
    print("Frames in page2: %d" % len(page2.frames))
    print("Pages in context: %d" % len(context.pages))

    print("Closing context...")
    context.close()
    print("Contexts in browser: %d" % len(browser.contexts))
    print("Closing browser")
    browser.close()


if __name__ == "__main__":
    with playwright.sync_playwright() as p:
        main(p)