#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 13:51:13 2019

@author: xijinping
"""

"""
对于要输验证码页面的error_url 通过selenium打开 反复点击验证码获取新的验证码
保存在本地 captcha 文件夹中
"""
import base64
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
#import time

headers = {

    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

#当时打开该url是要输入验证码的 现在不行 要换一个要输验证码的界面
error_url="https://www.zhihu.com/account/unhuman?type=unhuman&message=%E7%B3%BB%E7%BB%9F%E7%9B%91%E6%B5%8B%E5%88%B0%E6%82%A8%E7%9A%84%E7%BD%91%E7%BB%9C%E7%8E%AF%E5%A2%83%E5%AD%98%E5%9C%A8%E5%BC%82%E5%B8%B8%EF%BC%8C%E4%B8%BA%E4%BF%9D%E8%AF%81%E6%82%A8%E7%9A%84%E6%AD%A3%E5%B8%B8%E8%AE%BF%E9%97%AE%EF%BC%8C%E8%AF%B7%E8%BE%93%E5%85%A5%E9%AA%8C%E8%AF%81%E7%A0%81%E8%BF%9B%E8%A1%8C%E9%AA%8C%E8%AF%81%E3%80%82&need_login=true"
option = ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = webdriver.Chrome(options=option)
driver.get(error_url)

input_xpath = '//*[@id="root"]/div/div[2]/section/div/div/input'
verification_xpath = '//*[@id="root"]/div/div[2]/section/div/img'
submitt_xpath = '//*[@id="root"]/div/div[2]/section/button'


for count in range(1000):
    double = driver.find_element_by_xpath(verification_xpath)
    ActionChains(driver).double_click(double).perform()
    soup=BeautifulSoup(driver.page_source,'lxml')
    img=soup.find('img',{'class':'Unhuman-captcha'})['src']
    name='./captcha/'+str(count)+'.png'
    #验证码图片是以base64的格式显示的 通过base64库解析
    imgdata=base64.b64decode(img[22:])
    f=open(name,'wb')
    f.write(imgdata)
    f.close()
