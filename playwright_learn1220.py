from typing import List
from playwright.sync_api import ConsoleMessage, Page
import playwright
from playwright.sync_api import Playwright
from playwright import sync_playwright
from playwright.sync_api import BrowserContext


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
    context = browser.newContext(viewport=0)
    page1 = context.newPage()
    page1.goto("about:blank")
    messages = []
    page.on("console", lambda m: messages.append(m.text))
    with page.expect_console_message() as event_info:
        page.evaluate('() => console.log("hello", 5, {foo: "bar"})')
    message=event_info.value
    print(message,messages)
    page1.close()
    print("Closing context...")
    context.close()
    print("Contexts in browser: %d" % len(browser.contexts))
    print("Closing browser")
    browser.close()

def test_console_should_work(page: Page, server):
    messages: List[ConsoleMessage] = []
    page.once("console", lambda m: messages.append(m))
    with page.expect_console_message():
        page.evaluate('() => console.log("hello", 5, {foo: "bar"})'),
    assert len(messages) == 1
    message = messages[0]
    assert message.text == "hello 5 JSHandle@object"
    assert str(message) == "hello 5 JSHandle@object"
    assert message.type == "log"
    assert message.args[0].json_value() == "hello"
    assert message.args[1].json_value() == 5
    assert message.args[2].json_value() == {"foo": "bar"}


def test_console_should_emit_same_log_twice(page, server):
    messages = []
    page.on("console", lambda m: messages.append(m.text))
    page.evaluate('() => { for (let i = 0; i < 2; ++i ) console.log("hello"); } ')
    assert messages == ["hello", "hello"]


def test_console_should_use_text_for__str__(page):
    messages = []
    page.on("console", lambda m: messages.append(m))
    page.evaluate('() => console.log("Hello world")')
    assert len(messages) == 1
    assert str(messages[0]) == "Hello world"


def test_console_should_work_for_different_console_api_calls(page, server):
    messages = []
    page.on("console", lambda m: messages.append(m))
    # All console events will be reported before 'page.evaluate' is finished.
    page.evaluate(
        """() => {
      // A pair of time/timeEnd generates only one Console API call.
      console.time('calling console.time');
      console.timeEnd('calling console.time');
      console.trace('calling console.trace');
      console.dir('calling console.dir');
      console.warn('calling console.warn');
      console.error('calling console.error');
      console.log(Promise.resolve('should not wait until resolved!'));
    }"""
    )
    assert list(map(lambda msg: msg.type, messages)) == [
        "timeEnd",
        "trace",
        "dir",
        "warning",
        "error",
        "log",
    ]

    assert "calling console.time" in messages[0].text
    assert list(map(lambda msg: msg.text, messages[1:])) == [
        "calling console.trace",
        "calling console.dir",
        "calling console.warn",
        "calling console.error",
        "JSHandle@promise",
    ]


def test_console_should_not_fail_for_window_object(page: Page, server):
    messages = []
    page.once("console", lambda m: messages.append(m))
    with page.expect_console_message():
        page.evaluate("() => console.error(window)")
    assert len(messages) == 1
    assert messages[0].text == "JSHandle@object"


def test_console_should_trigger_correct_Log(page, server):
    page.goto("about:blank")
    with page.expect_console_message() as message:
        page.evaluate("url => fetch(url).catch(e => {})", server.EMPTY_PAGE),
    assert "Access-Control-Allow-Origin" in message.value.text
    assert message.value.type == "error"


def test_console_should_have_location_for_console_api_calls(page, server):
    page.goto(server.EMPTY_PAGE)
    with page.expect_console_message() as message:
        page.goto(server.PREFIX + "/consolelog.html")
    message = message.value
    assert message.text == "yellow"
    assert message.type == "log"
    location = message.location
    # Engines have different column notion.
    assert location.url == server.PREFIX + "/consolelog.html"
    assert location.line == 7


def test_console_should_not_throw_when_there_are_console_messages_in_detached_iframes(
    page: Page, server
):
    page.goto(server.EMPTY_PAGE)
    with page.expect_popup() as popup:
        page.evaluate(
            """async() => {
                // 1. Create a popup that Playwright is not connected to.
                const win = window.open('');
                window._popup = win;
                if (window.document.readyState !== 'complete')
                new Promise(f => window.addEventListener('load', f));
                // 2. In this popup, create an iframe that console.logs a message.
                win.document.body.innerHTML = `<iframe src='/consolelog.html'></iframe>`;
                const frame = win.document.querySelector('iframe');
                if (!frame.contentDocument || frame.contentDocument.readyState !== 'complete')
                new Promise(f => frame.addEventListener('load', f));
                // 3. After that, remove the iframe.
                frame.remove();
            }"""
        )
    # 4. Connect to the popup and make sure it doesn't throw.
    assert popup.value.evaluate("1 + 1") == 2

if __name__ == "__main__":
    with playwright.sync_playwright() as p:
        main(p)
