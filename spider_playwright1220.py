#-*- coding: utf-8 -*-
from playwright import sync_playwright
from playwright.sync_api import BrowserContext
from playwright.sync_api import Page
import time
import pandas as pd
import json
import re
import requests
from lxml import etree
import pandas as pd
import asyncio
from playwright import async_playwright


class MoviePage(BrowserContext):
    
    def __init__(self,context):
        self.context = context
    

    def to_url(self,i):
        page = self.context.newPage()
        # dimensions = page.evaluate('''() => {
        #                                 return {
        #                                     width: document.documentElement.clientWidth,
        #                                     height: document.documentElement.clientHeight,
        #                                     deviceScaleFactor: window.devicePixelRatio
        #                                 }
        #                                 }''')
        # print(dimensions)
        #page.on('dialog',lambda dialog:print(dialog.message,dialog.type))
        base_url="https://antispider1.scrape.center/page/{}".format(i)
        print(base_url)
        #waituntil设置，默认为load，可以设置['domcontentloaded', 'load', 'networkidle']，networkkidle意思为无网络连接时
        page.goto(base_url,waitUntil='networkidle')
        # js = '''
        #         ()=>{
        #             const newProto = navigator.__proto__;
        #             delete newProto.webdriver;
        #             navigator.__proto__ = newProto;
        #         }
        #     '''
        # page.evaluate(js)
        #time.sleep(5)
        print(page.frames)
        resp=page.content()
        #print(resp)
        with open(r'.\date\page.html','w',encoding='utf-8') as f:
            f.write(resp)
        # html=etree.HTML(resp)
        # movienames=html.xpath('//div[@class="el-card item m-t is-hover-shadow"]//h2/text()')
        # for moviename in movienames:
        #     print(moviename)
        movie_elements=page.querySelectorAll('//div[@class="el-card item m-t is-hover-shadow"]')
        for movie_element in movie_elements:
            text=movie_element.innerText()
            text_list=text.split('\n')
            #print(text_list)
            movie_name=text_list[0]
            score=text_list[-1]
            country=text_list[2]
            movie_type=text_list[1]
            release_time=text_list[3]
            print(movie_name,score,country,movie_type,release_time)
            resp=movie_element.innerHTML()
            html=etree.HTML(resp)
            movie_name=html.xpath('//h2[@class="m-b-sm"]/text()')[0]
            score=html.xpath('//p[@class="score m-t-md m-b-n-sm"]/text()')[0]
            country=html.xpath('//div[@class="m-v-sm info"][1]/span[1]/text()')[0]
            movie_types=html.xpath('//div[@class="categories"]//span/text()')
            movie_types=''
            for movie in movie_types:
                movie_types=movie_types+ movie.strip()+'、'
            release_time=html.xpath('//div[@class="m-v-sm info"][2]/span[1]/text()')[0]
            print(movie_name,score,country,movie_type,release_time)
            content={
                "电影名称":movie_name,
                "评分":score,
                "国家":country,
                "类型":movie_type,
                "上映时间":release_time
            }
            contents.append(content)
        page.close()
        print("第{}页分析完毕".format(i))
        



def write_excle(content,savefile):
    df=pd.DataFrame.from_dict(content)
    #df.set_index(df.columns[0],inplace=True)
    df.to_excel(savefile)


if __name__ == "__main__":
    contents = []
    #设置文件保存的地址
    savefile = ".\date\爬取电影数据.xlsx"
    playwright = sync_playwright().start()
    #无头浏览器模式
    #browser = playwright.chromium.launch()
    #打开浏览器模式
    browser = playwright.chromium.launch(headless=False,slowMo=200,args=[f'--window-size={1366},{768}'])
    context = browser.newContext()
    #在标签页增加一段代码，将window.navigator.webdriver的值修改，下面两种办法均可
    # context.addInitScript(source="""
    #         Object.defineProperty(navigator, 'webdriver', {
    #         get: () => undefined
    #         })
    #     """
    #     )
    context.addInitScript(source="""
                    const newProto = navigator.__proto__;
                    delete newProto.webdriver;
                    navigator.__proto__ = newProto;
        """
        )    
    #设置超时时间为30s
    context.setDefaultTimeout(30000)
    mp=MoviePage(context)
    for i in range(1,11):
        mp.to_url(i)
    context.close()
    browser.close()
    write_excle(contents,savefile)
    print("{}保存完毕".format(savefile))