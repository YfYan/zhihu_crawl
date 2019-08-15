#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 17:02:00 2019

@author: xijinping
"""
from get_questions_v2 import captcha_process
import requests
import threading

zhuanlan_info = {}

#多线程爬取专栏
class zhuanlan_thread(threading.Thread):
    def __init__(self,zhuanlans):
        threading.Thread.__init__(self)
        self.zhuanlans=zhuanlans
        
    def run(self):
        get_zhuanlan(self.zhuanlans)
        
headers = {
    'accept-language': 'zh-CN,zh;q=0.9',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    'accept': '*/*',
    'referer': 'https://zhuanlan.zhihu.com/',
    'authority': 'zhuanlan.zhihu.com',
    'x-requested-with': 'fetch',
    'x-zse-83': '3_2.0',
}

params = (
    ('include', 'data[*].admin_closed_comment,comment_count,suggest_edit,is_title_image_full_screen,can_comment,upvoted_followees,can_open_tipjar,can_tip,voteup_count,voting,topics,review_info,author.is_following,is_labeled,label_info'),
)

def get_zhuanlan(zhuanlans):
    for i in range(len(zhuanlans)):
        zhuanlans[i] = zhuanlans[i].split('/')[-1]
    
    for zhuanlan_name in zhuanlans:
        #试了几次 专栏的量不是很大 不太出验证码 
        url='https://zhuanlan.zhihu.com/api/columns/'+zhuanlan_name
        response = requests.get(url, headers=headers, params=params)
        jd=response.json()
        if jd.get('error')!=None:
            captcha_process(jd['error']['redirect'])
            #处理好验证码 重新请求
            response = requests.get(url,headers=headers,params=params)
            jd=response.json()
        title = jd['title']
        intro = jd['intro']
        print(title,intro)
        zhuanlan_info[zhuanlan_name] = {'title':title,'intro':intro}

def thread_running(thread_num,zhuanlans):
    l=int(len(zhuanlans)/thread_num)
    args=[]
    #将followers平均分割
    for i in range(thread_num-1):
        args.append(zhuanlans[l*i:l*(i+1)])
    args.append(zhuanlans[l*(thread_num-1):])
    
    ths=[]
    for i in range(thread_num):
        ths.append(zhuanlan_thread(args[i]))
    
    for th in ths:
        th.start()
        
    for th in ths:
        th.join()
if __name__=='__main__':
    f=open('followers_zhuanlans.txt','r')
    user_info = f.readlines()
    f.close()
    
    zhuanlans=[]
    for item in user_info:
        item=item[:-1]
        zhuanlans.extend(item.split(' ')[1:])
    
    zhuanlans=list(set(zhuanlans))
    
    thread_running(8,zhuanlans)
    f=open('zhuanlans_info.txt','w')
    f.writelines(str(zhuanlan_info))
    f.close()
        
        
