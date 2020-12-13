#-*- coding: utf-8 -*-
from playwright import sync_playwright
from playwright.sync_api import Browser
from playwright.sync_api import BrowserContext
from playwright.sync_api import Page
import pandas as pd
from lxml import etree


def playwright_start(login_url):
    playwright = sync_playwright().start()
    #无头浏览器模式
    #browser = playwright.chromium.launch()
    #打开浏览器模式
    browser = playwright.chromium.launch(headless=False,slowMo=200)
    context = browser.newContext()
    #设置防爬的参数
    context.addInitScript(source="""
                    const newProto = navigator.__proto__;
                    delete newProto.webdriver;
                    navigator.__proto__ = newProto;
        """
        ) 
    #设置超时时间为30s
    context.setDefaultTimeout(30000)
    page= context.newPage()
    # page.on("request", lambda request: print("Request %s" % request.url))
    # page.on("requestfinished", lambda request: print("Request finished %s" % request.url))
    # page.on("response",lambda response: print("Response %s"% (response.text())))
    page.goto(login_url,waitUntil="networkidle")
    with open(r'.\date\1.html','w',encoding='utf-8') as f:
        f.write(page.content())
    # deptname_list=page.querySelectorAll('//div[@class="pub-people"]/ul[1]/div/li[@class="depItem"]/a')
    # for deptname in deptname_list:
    #     dept_name=deptname.getAttribute("title")
    #     dept_url=deptname.getAttribute("href")
    html=etree.HTML(page.content())
    deptname_list=html.xpath('//div[@class="pub-people"]/ul[1]/div/li[@class="depItem"]')
    for deptname in deptname_list:
        dept_name=deptname.xpath('.//a/@title')[0]
        dept_url=deptname.xpath('.//a/@href')[0]
        content={
                "单位名称":dept_name,
                "网站链接":dept_url,
                }
        print(content)
        contents.append(content)
    page.close()
    context.close()
    browser.close()    


def write_excle(content,savefile):
    df=pd.DataFrame.from_dict(content)
    df.to_excel(savefile)

if __name__ == '__main__':
        login_url="https://www.hnzwfw.gov.cn/410882000000/?region=410882000000"
        savefile = "./date/政务服务网单位网址.xlsx"
        contents = []
        playwright_start(login_url)    
        write_excle(contents,savefile)    
        print("{}保存完毕".format(savefile))






