# ******************
# 通过cookie登录网站
# ******************
 
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import json
from time import sleep
from datetime import datetime
import os
 
class Test_loggin(object):
 
    def __init__(self, log_url, home_url, cookie_path, yuanshu, cookie_name = 'cookie.txt', expiration_time = 30):
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
        self.yuanshu = yuanshu
        self.cookie_name = cookie_name
        self.expiration_time = expiration_time
 
    def get_cookie(self):
        '''手动登录获取cookie'''
        driver = webdriver.Chrome(executable_path=driver_path)
        driver.get(self.log_url)
        driver.maximize_window()
        # 显性等待2，当页面出现某个元素时就执行下列的操作
        WebDriverWait(driver, 60, 2).until(lambda x: x.find_element_by_xpath(self.yuanshu))
        print("进入主页验证1成功")
        with open(os.path.join(self.cookie_path, self.cookie_name), 'w') as cookief:    # 创建文本覆盖保存cookie
            # 将cookies保存为json格式
            cookief.write(json.dumps(driver.get_cookies()))
        print("cookie保存成功")
        driver.close()
 
    def pd_Cookie(self):
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
                print("cookie已经过期，请重新手动登录获取")
                return self.get_cookie()
            else:
                print("cookie未过期")
 
    def cookie_loggin(self):
        '''自动登录操作'''
        self.pd_Cookie()  # 首先判断cookie是否已获取，是否过期
        print("自动登录开始...")
        # 加启动配置
        option = webdriver.ChromeOptions()
        # 关闭“chrome正受到自动测试软件的控制”
        # V75以及以下版本
        # option.add_argument('disable-infobars')
        # V76以及以上版本
        option.add_experimental_option('useAutomationExtension', False)
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 不自动关闭浏览器
        option.add_experimental_option("detach", True)
        # 打开chrome浏览器
        driver = webdriver.Chrome(executable_path=driver_path,chrome_options=option)
 
        driver.get(self.log_url)
        driver.delete_all_cookies()     # 清除旧cookies
 
        # with可以上下文管理上文进行设置部署，下文进行处理，然后把处理的结果赋值给变量（cookie）
        with open(os.path.join(self.cookie_path, self.cookie_name),'r') as cookief:
            #使用json读取cookies 注意读取的是文件 所以用load而不是loads
            cookieslist = json.load(cookief)
 
            # 方法1删除该字段
            for cookie in cookieslist:
                #该字段有问题所以删除就可以  浏览器打开后记得刷新页面 有的网页注入cookie后仍需要刷新一下
                if 'expiry' in cookie:
                    del cookie['expiry']
                driver.add_cookie(cookie)
 
            driver.maximize_window()
            driver.get(self.home_url)
            sleep(2)
            driver.close()
            print("浏览器退出")
 
 
if __name__ == "__main__":
    log_url = 'https://passport.jd.com/new/login.aspx'       # 这里测试用的是京东的网址
    home_url = 'https://www.jd.com/'
    cookie_path = '.\date' 
    yuanshu = "//input[@id='key']"
    driver_path='.\source\chromedriver.exe'
    test_loggin = Test_loggin(log_url=log_url, home_url=home_url, cookie_path=cookie_path, yuanshu=yuanshu)
    test_loggin.cookie_loggin()