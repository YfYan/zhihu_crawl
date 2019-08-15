#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 13:29:23 2019

@author: xijinping
"""

import requests
import threading

from selenium import webdriver
from selenium.webdriver import ChromeOptions
#import time
from bs4 import BeautifulSoup
import random
import base64
from captcha_predict import Captcha_pred

#基本url的前半部分 在后面加上各种id就是要爬取的网页
question='https://www.zhihu.com/question/'
article='https://zhuanlan.zhihu.com/p/'
zhuanlan='https://zhuanlan.zhihu.com/'

#列表存放的字符串 用户token+所有问题url/文章url/专栏url/关注话题 空格隔开
questions=[]
articles=[]
zhuanlans=[]
topics=[]

#做验证码预测的类
pred=Captcha_pred()

headers = {
    'Referer': 'https://www.zhihu.com/',
    'x-requested-with': 'fetch',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Zse-83': '3_2.0',
}

#多线程爬取所有用户的关注问题等 初始化时放入所有用户token的列表
class question_threading(threading.Thread):
    def __init__(self,followers):
        threading.Thread.__init__(self)
        self.followers=followers
    
    #重载run方法
    def run(self):
        get_questions(self.followers)

#此部分调试机会较少 还是用的selenium处理
def captcha_process(url):
    option = ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome(options=option)
    driver.get(url)
    soup=BeautifulSoup(driver.page_source,'lxml')
    #直到不是验证码界面结束
    while soup.find('head').text[:9].find('安全验证 - 知乎')!=-1:
        try:
            soup=BeautifulSoup(driver.page_source,'lxml')
            img=soup.find('img',{'class':'Unhuman-captcha'})['src']
            #此处命名用的一长串随机数 防止多线程处理时命名冲突
            name='./temp/'+str(random.random())+'.png'
            imgdata=base64.b64decode(img[22:])
            f=open(name,'wb')
            f.write(imgdata)
            f.close()
            pred.set_dirname(name)
            #预测的验证码
            captcha=pred.pred_whole_captcha()
            driver.find_element_by_xpath('//*[@id="root"]/div/div[2]/section/div/div/input').click()
            driver.find_element_by_xpath('//*[@id="root"]/div/div[2]/section/div/div/input').clear()
            driver.find_element_by_xpath('//*[@id="root"]/div/div[2]/section/div/div/input').send_keys(captcha)
            driver.find_element_by_xpath('//*[@id="root"]/div/div[2]/section/button').click()
        except:
            continue
        soup=BeautifulSoup(driver.page_source,'lxml')
    driver.close()
        
def get_questions(followers):
    complete=0
    for follower in followers:
        #用户信息的字符串初始化
        local_questions=follower+' '
        local_articles=follower+' '
        local_zhuanlans=follower+' '
        local_topics=follower+' '
        
        #limit相当于在浏览器中滚动滚轮的操作 一屏7个
        
        after_id=None
        
        for i in range(30):
            #第一次的请求不需要after_id 之后的after_id加在params中
            if i==0:
                params = (
                    ('limit', '7'),
                    ('desktop', 'True'),
                )
            else:
                params = (
                ('limit', '7'),
                ('after_id', after_id),
                ('desktop', 'True'),
            )
            
            response = requests.get('https://www.zhihu.com/api/v4/members/'+follower+'/activities', headers=headers, params=params)
            
            jd=response.json()
        
        
            if jd.get('error') != None:
                #前两个错误容易在一开始得出 是用户本身的问题 直接break跳出循环
                if jd['error']['message']=='该帐号已注销，主页无法访问':
                    break
                elif jd['error']['message'] == '身份未经过验证':
                    break
                #出验证码了 验证码在redirect的url里 不能直接用当前的url去传入captcha_process
                elif jd['error']['message'] == '系统监测到您的网络环境存在异常，为保证您的正常访问，请输入验证码进行验证。':
                    captcha_process(jd['error']['redirect'])
                    #处理好验证码  重新请求
                    response = requests.get('https://www.zhihu.com/api/v4/members/'+follower+'/activities', headers=headers, params=params)
                    jd=response.json()
            
            #处理信息 扩充当前的信息字符串
            for dic in jd['data']:
                if dic['action_text'] == '关注了问题' :
                    question_id=str(dic['target']['id'])
                    title=dic['target']['title']
                    local_questions+=(question+question_id+' ')
                    print(title)
                elif dic['action_text'] == '赞同了文章':
                    title=dic['target']['title']
                    article_id=str(dic['target']['id'])
                    local_articles+=(article+article_id+' ')
                    print(title)
                elif dic['action_text'] == '关注了专栏':
                    title=dic['target']['title']
                    zhuanlan_id = str(dic['target']['id'])
                    local_zhuanlans+=(zhuanlan+zhuanlan_id+' ')
                    print(title)
                elif dic['action_text'] =='关注了话题':
                    topic=dic['target']['name']
                    local_topics+=(topic+' ')
                    print(topic)
                elif dic['action_text'] in ('赞同了回答','收藏了回答','回答了问题'):
                    question_id=str(dic['target']['question']['id'])
                    title=dic['target']['question']['title']
                    local_questions+=(question+question_id+' ')
                    print(title)
        
            #如果页面没有新的动态了 结束break出去
            try:
                after_id=jd['paging']['next'].split('&')[2].split('=')[1]
            except:
                break
            
        #去掉最后的空格
        local_articles=local_articles[:-1]
        local_questions=local_questions[:-1]
        local_topics=local_topics[:-1]
        local_zhuanlans=local_zhuanlans[:-1]
        
        #加上换行符
        local_articles+='\n'
        local_questions+='\n'
        local_topics+='\n'
        local_zhuanlans+='\n'
            
        articles.append(local_articles)
        questions.append(local_questions)
        topics.append(local_topics)
        zhuanlans.append(local_zhuanlans)
        
        complete+=1
        print(follower,"{} / {} completed".format(complete,len(followers)))

def thread_running(thread_num,followers):
    l=int(len(followers)/thread_num)
    args=[]
    #将followers平均分割
    for i in range(thread_num-1):
        args.append(followers[l*i:l*(i+1)])
    args.append(followers[l*(thread_num-1):])
    
    ths=[]
    for i in range(thread_num):
        ths.append(question_threading(args[i]))
    
    for th in ths:
        th.start()
        
    for th in ths:
        th.join()
            
if __name__ == '__main__':
    f=open('./followers_info.txt','r')
    data=f.readlines()
    f.close()
    
    followers=[]
    
    for item in data:
        #只需要user token 并去掉最后的换行符
        followers.append(item.split(' ')[-1][:-1])
    
    thread_running(4,followers)
    
    #保存在本地
    f=open('followers_questions.txt','w')
    f.writelines(questions)
    f.close()
    f=open('followers_articles.txt','w')
    f.writelines(articles)
    f.close()
    f=open('followers_zhuanlans.txt','w')
    f.writelines(zhuanlans)
    f.close()
    f=open('followers_topics.txt','w')
    f.writelines(topics)
    f.close()
