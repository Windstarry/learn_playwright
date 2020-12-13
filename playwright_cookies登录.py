#-*- coding: utf-8 -*-
from playwright import sync_playwright
from playwright.sync_api import Browser
from playwright.sync_api import BrowserContext
from playwright.sync_api import Page
from datetime import datetime
import os
import time
import pandas as pd
import json
import re
import requests
from lxml import etree


class Test_loggin(object):
 
    def __init__(self, log_url, home_url, cookie_path='./date',cookie_name = 'cookie.txt', expiration_time = 30):
        '''
        :param log_url: 登录网址
        :param home_url: 首页网址
        :param cookie_path: cookie文件存放路径
        :param yuanshu: 进入主页后验证的元素
        :param cookie_path: 文件命名
        :param expiration_time: cookie过期时间,默认30分钟
        '''
        self.log_url = log_url
        self.home_url = home_url
        self.cookie_path = cookie_path
        self.cookie_name = cookie_name
        self.expiration_time = expiration_time
 
    def get_cookie(self):
        '''登录获取cookie'''
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
        page = context.newPage()
        #打开权力运行系统登陆网址
        page.goto(self.log_url,waitUntil="load")
        page.fill("input[name=\"userNameHeader\"]", USENAME)
        page.fill("input[name=\"password\"]", PASSWORD)
        page.check("input[id=\"recordAccount\"]")
        with page.expect_navigation():
            page.click('//a[@class="btn-login"]')
            print("登陆成功")
        page.waitForSelector(r'//div[@class="lw-navContent"]/ul/li/a[contains(text(), "权力事项管理")]')
        page.click(r'//div[@class="lw-navContent"]/ul/li/a[contains(text(), "权力事项管理")]')
        print("进入权力事项管理")
        with open(os.path.join(self.cookie_path, self.cookie_name), 'w') as cookief:    # 创建文本覆盖保存cookie
            # 将cookies保存为json格式
            cookief.write(json.dumps(context.cookies()))
        print("cookies保存完成")
        page.close()
        context.close()
        browser.close()

    def judge_cookie(self):
        '''获取最新的cookie文件，判断是否过期'''
        cookie_list = os.listdir(self.cookie_path)  # 获取目录下所有文件
        if not cookie_list:  # 判断文件为空时，直接执行手动登录
            self.get_cookie()
        else:
            cookie_list2 = sorted(cookie_list)  # 升序排序文件,返回新列表；sort是对原列表进行排列
            new_cookie = os.path.join(cookie_path, cookie_list2[-1])    # 获取最新cookie文件的全路径 
            file_time = os.path.getmtime(new_cookie)  # 获取最新文件的修改时间，返回为时间戳1590113596.768411
            t = datetime.fromtimestamp(file_time)  # 时间戳转化为字符串日期时间
            print('当前时间：', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print('最新cookie文件修改时间：', t.strftime("%Y-%m-%d %H:%M:%S"))
            date = (datetime.now() - t).seconds // 60  # 时间之差，seconds返回相距秒数//60,返回分数
            print('相距分钟:{0}分钟'.format(date))
            if date > self.expiration_time:  # 默认判断大于30分钟，即重新手动登录获取cookie
                print("cookie已经过期，请重新登录获取")
                return self.get_cookie()
            else:
                print("cookie未过期")
 
    def cookie_loggin(self):
        '''自动登录操作'''
        self.judge_cookie()  # 首先判断cookie是否已获取，是否过期
        print("自动登录开始...")
        # 加启动配置
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
        page = context.newPage()
        #打开权力运行系统登陆网址
        page.goto(self.log_url,waitUntil="load")
        context.clear_cookies()   # 清除旧cookies
        # with可以上下文管理上文进行设置部署，下文进行处理，然后把处理的结果赋值给变量（cookie）
        with open(os.path.join(self.cookie_path, self.cookie_name),'r') as cookief:
            #使用json读取cookies 注意读取的是文件 所以用load而不是loads
            cookieslist = json.load(cookief)
            # 方法1删除该字段
            cookies_dict = dict()
            for cookie in cookieslist:
                #该字段有问题所以删除就可以,浏览器打开后记得刷新页面 有的网页注入cookie后仍需要刷新一下
                if 'expiry' in cookie:
                    del cookie['expiry']
                cookies_dict[cookie['name']] = cookie['value']
        context.add_cookies(cookies_dict)
        page.goto(self.home_url,waitUntil='load')
        #等待10s查看网页是否cookies登录
        time.sleep(10)
        page.close()
        context.close()
        browser.close()
        print("浏览器退出")

        

if __name__ == "__main__":
    log_url = 'http://59.227.149.130:8060/was'
    home_url = 'http://59.227.149.130:8060/was'
    cookie_path = '.\date'
    USENAME="修武县_政务2019"
    PASSWORD="Abc123#$"
    test_loggin = Test_loggin(log_url=log_url, home_url=home_url, cookie_path=cookie_path)
    test_loggin.cookie_loggin()
