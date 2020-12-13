#-*- coding: utf-8 -*-
from playwright import sync_playwright
from playwright.sync_api import Browser
from playwright.sync_api import BrowserContext
from playwright.sync_api import Page
from lxml import etree
import time
import pysnooper
import json
import pandas as pd



class ParsePage(BrowserContext):
    

    def __init__(self,context):
        self.context = context


    def playwright_start(self,login_url,dept_name):
        # page.on("request", lambda request: print("Request %s" % request.url))
        # page.on("requestfinished", lambda request: print("Request finished %s" % request.url))
        # page.on("response",lambda response: print("Response %s"% (response.text())))
        page = self.context.newPage() 
        page.goto(login_url,waitUntil="load")
        with open(r'.\date\1.html','w',encoding='utf-8') as f:
            f.write(page.content())    
        next_btns=page.querySelectorAll('//button[@class="btn-next"]')
        if len(next_btns)>0:
            next_btn=next_btns[0]
            self.parse_page(page,dept_name)
            while True:
                next_btn.scrollIntoViewIfNeeded()
                next_btn.click()
                page.waitForSelector('//div[@class="el-collapse"]/div')
                self.parse_page(page,dept_name)
                next_btn_state=next_btn.getAttribute("disabled")
                print(next_btn_state)
                if next_btn_state=="disabled":
                    print("已到达最后一页")
                    break
        else:
            self.parse_page(page,dept_name)
        page.close()
    
    
    def parse_page(self,page,dept_name): 
        code_list=page.querySelectorAll('//div[@class="el-collapse"]/div')
        for code in code_list:
            html=etree.HTML(code.innerHTML())
            page_list=html.xpath('//div[1]//div[@class="collapse-header"]/span/text()')
            print(page_list)
            for service_name in page_list[1:]:
                catalogname=page_list[0]
                content={
                        "办理单位":dept_name,
                        "事项目录":catalogname,
                        "业务办理项名称":service_name
                }
                contents.append(content)


def write_excle(content,savefile):
    df=pd.DataFrame.from_dict(content)
    df.set_index(df.columns[0],inplace=True)
    df.to_excel(savefile)


class HandleExcle(object):
    
    def __init__(self,filename):
        self.filename = filename
        self.df=pd.read_excel(self.filename)
        self.max_num=self.df.shape[0]

    def get_url(self,x):
        url=self.df['网站链接'].at[x]
        return url

  
    def get_deptname(self,x):
        deptname=self.df['单位名称'].at[x]
        return deptname
    

if __name__ == '__main__':
    filename="./date/修武县政务服务网单位网址1226.xlsx"
    savefile = "./date/修武县政务服务网事项.xlsx"
    contents=[]
    playwright = sync_playwright().start()
    #无头浏览器模式
    browser = playwright.chromium.launch()
    #打开浏览器模式
    #browser = playwright.chromium.launch(headless=False,slowMo=200)
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
    pp=ParsePage(context)
    he=HandleExcle(filename)
    for i in range(0,he.max_num):
        url=he.get_url(i)
        deptname=he.get_deptname(i)
        pp.playwright_start(url,deptname)
    context.close()
    browser.close()
    write_excle(contents,savefile)
    print("{}保存完毕".format(savefile))