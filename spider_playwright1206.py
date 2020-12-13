#-*- coding: utf-8 -*-
from playwright import sync_playwright
from playwright.browser_context import BrowserContext
import time
import pandas as pd
import json
import re
from playwright.sync_api import Page
import requests
from lxml import etree
import pandas as pd


class MoviePage(BrowserContext):
    
    def __init__(self,context):
        self.context = context
    

    def to_url(self):
        page = self.context.newPage()
        # Go to http://59.207.104.12:8090//login
        base_url="https://spa3.scrape.center/"
        print(base_url)
        #waituntil设置，默认为load，可以设置['domcontentloaded', 'load', 'networkidle']，networkkidle意思为无网络连接时
        page.goto(base_url,waitUntil='networkidle',timeout=50000)
        #ParsePage(page).parse_page()
        movie_elements=page.querySelectorAll('//div[@class="el-card item m-t is-hover-shadow"]')
        last_ele=movie_elements[-1]
        last_ele.focus()
        print(last_ele.textContent())
        last_ele.scrollIntoViewIfNeeded()
        last_ele.waitForElementState("stable")
        page.keyboard.down("PageDown")
        page.keyboard.down("PageDown")
        time.sleep(5)
        load_state=True
        while load_state:
            with page.expect_load_state('networkidle'):
                movie_elements=page.querySelectorAll('//div[@class="el-card item m-t is-hover-shadow"]')
                movietext=movie_elements[-1].innerText()
            if movietext != last_ele.innerText():
                print(movietext)
                print(last_ele.innerText())
                page.keyboard.down("PageDown")
                page.keyboard.down("PageDown")
                last_ele=movie_elements[-1]
                last_ele.focus()
                last_ele.scrollIntoViewIfNeeded()
                last_ele.waitForElementState("stable")
                time.sleep(10)
                page.waitForLoadState(state='networkidle',timeout=50000)
            else:
                print("滚动条已经处于页面最下方!")
                break
        ParsePage(page).parse_page()
        page.close()
        print("分析完毕")


class ParsePage(Page):
    
    def __init__(self,page):
        self.page = page


    def parse_page(self):
        resp=self.page.content()
        #print(resp)
        with open(r'.\date\page.html','w',encoding='utf-8') as f:
            f.write(resp)
        # html=etree.HTML(resp)
        # movienames=html.xpath('//div[@class="el-card item m-t is-hover-shadow"]//h2/text()')
        # for moviename in movienames:
        #     print(moviename)
        movie_elements=self.page.querySelectorAll('//div[@class="el-card item m-t is-hover-shadow"]')
        for movie_element in movie_elements:
            #获取元素内的所有文本，按照对应的内容匹配
            text=movie_element.innerText()
            text_list=text.split('\n')
            #print(text_list)
            movie_name=text_list[0]
            score=text_list[-1]
            country=text_list[2]
            movie_type=text_list[1]
            release_time=text_list[3]
            print(movie_name,score,country,movie_type,release_time)
            #获取元素内所有编码内容，将内容转化为etree的Html格式，适合xpath解析
            # resp=movie_element.innerHTML()
            # html=etree.HTML(resp)
            # movie_name=html.xpath('//h2[@class="m-b-sm"]/text()')[0]
            # score=html.xpath('//p[@class="score m-t-md m-b-n-sm"]/text()')[0]
            # country=html.xpath('//div[@class="m-v-sm info"][1]/span[1]/text()')[0]
            # movie_types=html.xpath('//div[@class="categories"]//span/text()')
            # movie_types=''
            # for movie in movie_types:
            #     movie_types=movie_types+'、'+ movie.strip()
            # release_time=html.xpath('//div[@class="m-v-sm info"][2]/span[1]/text()')[0]
            # print(movie_name,score,country,movie_type,release_time)
            content={
                "电影名称":movie_name,
                "评分":score,
                "国家":country,
                "类型":movie_type,
                "上映时间":release_time
            }
            contents.append(content)




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
    browser = playwright.chromium.launch(headless=False,slowMo=200)
    context = browser.newContext()
    #设置超时时间为30s
    context.setDefaultTimeout(30000)
    mp=MoviePage(context)
    mp.to_url()
    context.close()
    browser.close()
    write_excle(contents,savefile)
    print("{}保存完毕".format(savefile))