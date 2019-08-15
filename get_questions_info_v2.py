#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 16:49:12 2019

@author: xijinping
"""

from get_questions_v2 import captcha_process

import requests
from bs4 import BeautifulSoup
import re
import random
import threading
import base64
from selenium import webdriver
from selenium.webdriver import ChromeOptions

from captcha_predict import Captcha_pred

pred=Captcha_pred()

class node(object):
    def __init__(self,var,next_node=None):
        self.var=var
        self.next_node=next_node
    
    def get_value(self):
        return self.var
    
    def get_next(self):
        return self.next_node

questions_info={}
    
#多线程爬取问题
class topic_threading(threading.Thread):
    def __init__(self,urls):
        threading.Thread.__init__(self)
        self.urls=urls
    
    def run(self):
        get_topics(self.urls)

#模拟登陆 并没有什么用
def simulate_login():
    option = ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome(options=option)
    driver.get("https://www.zhihu.com/signin?next=%2F")
    driver.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div[2]/div/form/div[1]/div[2]').click()
    driver.find_element_by_css_selector(".Login-content input[name='username']").send_keys("18661050766@163.com")
    driver.find_element_by_css_selector(".Login-content input[name='password']").send_keys("njuyyf17")
#    time.sleep(5)
    driver.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
    driver.close()


headers = {
    #cookie不能设 会让selenium失效
#    'cookie': '_xsrf=cb1hH6Qx8l446lSkIJUEDxw2roY0x2dT; _zap=58cee2ae-6203-4e38-9e52-c4a940ab916e; d_c0="AHAiZpozvg-PTnbxV3WMJrnRKJqooaktZT8=|1563242249"; tst=r; q_c1=17e5b14217734f349d210c33ed110ba3|1563247901000|1563247901000; __utmv=51854390.100--|2=registration_date=20190717=1^3=entry_date=20190716=1; l_n_c=1; l_cap_id="MmE2MTgxMWJjYTg3NGQxYThjZjU1ZjQ3MmI0NmFjNjY=|1565256811|ade728041146a19e70aedf40d3a465f30108e4b9"; r_cap_id="Y2QyMjQ4NzQxYzRmNDZiZDliMmRkYmJlMGVmOWQ2MGQ=|1565256811|c01e312503fd341c8fe3d5deb678a6451a626420"; cap_id="ZDQyOTM1OWQ1NDVlNGM5ZDk5NDk0NDdhMThjNDUxZDY=|1565256811|ed79a88d5fd7c9941c94b86b0e9c4941385579e4"; n_c=1; capsion_ticket="2|1:0|10:1565316179|14:capsion_ticket|44:MDcyOGM5MjY2NzJjNDNlY2JhNzM2ZGY5OTRlMzVlNzE=|689c1619efd3a719843ccf018b6a722ada038757fd41688cf5e7cc75336d4839"; z_c0="2|1:0|10:1565316182|4:z_c0|92:Mi4xR1ZJRUVRQUFBQUFBY0NKbW1qTy1EeVlBQUFCZ0FsVk5WU0k2WGdDMFlHWThQVHR1X3VVNVRaM0wycHRpNUtxS3BR|485037f2219b5691c7fc066fb2f597722ae96198d00004acb3fa6056ceb42b3d"; __utma=51854390.508210261.1564553661.1564553661.1565329493.2; __utmc=51854390; __utmz=51854390.1565329493.2.2.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/; tgw_l7_route=f2979fdd289e2265b2f12e4f4a478330',
    'accept-language': 'zh-CN,zh;q=0.9',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    'referer': 'https://www.zhihu.com/',
}

params = (
    ('include', 'data[*].answer_count,author,follower_count'),
    ('limit', '5'),
)

def get_topics(questions):
    complete=0
    for url in questions:
        #获得url中的question_id
        qid=url.split('/')[-1]
        response = requests.get(url, headers=headers)
        soup=BeautifulSoup(response.text,'lxml')
        #处理可能的错误
        if soup.find('head') != None:
            #需要的登陆
            if soup.find('head').text.find('知乎 - 有问题，上知乎') != -1:
                continue
            #输入验证码
            elif soup.find('head').text.find('安全验证 - 知乎')!=-1:
                print(url)
#                simulate_login()
                captcha_process(url)
                response = requests.get(url,headers=headers)
        
        #从meta中获得标签
        soup=BeautifulSoup(response.text,'lxml')
        items=soup.find('meta',{'itemprop':'keywords'})
        #itemProp的字母可能是大写
        if items == None:
            items=soup.find('meta',{'itemProp':'keywords'})
        #分割逗号  获得标签的列表
        try:
            topics=items['content'].split(',')
            print(topics)
       
            #从网页源代码的JavaScript中得到标题和内容
            title=soup.find('title',{'data-react-helmet':'true'}).text[:-5]
            script=soup.find('script',{'id':'js-initialData'})
            #从JavaScript中正则找到问题的内容
            pattern = re.compile(',"excerpt":"([\s\S]*)","commentPermission"')
            content=pattern.findall(script.text)[0]
            
            #去掉奇怪的内容
            content.replace('[图片]','')
            content.replace('\n','')
            if questions_info.get(qid)==None:
                questions_info[qid]={}
                questions_info[qid]['title']=title
                questions_info[qid]['topics']=topics
                questions_info[qid]['content']=content
        except:
            pass
        complete+=1
        print('\n{} / {} completed'.format(complete, len(questions)))

#封装多线程
def thread_running(thread_num,questions):
    l=int(len(questions)/thread_num)

    args=[]
    
    for i in range(thread_num-1):
        args.append(questions[l*i:l*(i+1)])
    args.append(questions[l*(thread_num-1):])
    
    ths=[]
    for i in range(thread_num):
        ths.append(topic_threading(args[i]))
    
    for th in ths:
        th.start()
        
    for th in ths:
        th.join()
    
    
if __name__ == '__main__':
    f=open('./followers_questions.txt','r')
    data=f.readlines()
    f.close()
    
    questions=[]
    
    for i in range(len(data)):
        data[i]=data[i][:-1]
        items=data[i].split(' ')
        questions.extend(items[1:])
    
    #避免重复
    questions=list(set(questions))
    
    thread_running(16,questions)
    
    f=open('questions_info.txt','w')
    f.write(str(questions_info))
    f.close()
    