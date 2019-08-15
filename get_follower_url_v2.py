#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 11:49:09 2019

@author: xijinping
"""

"""
该代码用于给定一个要分析的人 爬取所有关注ta的人的url 并存起来用于下一步爬取问题、文章
该步爬取暂时未遇到验证码 所以没有验证码处理模块 未来可加
一般关注者也不会特别多 所以没有用多线程
"""
import requests
headers = {
            'accept-language': 'zh-CN,zh;q=0.9',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'accept': '*/*',
            'referer': 'https://www.zhihu.com/',
            'authority': 'www.zhihu.com',
            'x-requested-with': 'fetch',
            'x-zse-83': '3_2.0',
        }
params = (
             ('include', 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'),
             ('offset','0'),
             ('limit', '20'),
        )
class getFollowers(object):
    def __init__(self,zhihu_name):
        #data列表用于存放关注者信息的字符串 格式为 用户名+用户主页url+用户token 保存在文件里
        self.data=[]

        #zhihu_name 是要分析用户的token
        self.zhihu_name=zhihu_name
    
    def get_and_store_followers(self):
        global headers,params
        #获取知乎用户关注者第一页的信息 该步没有放在循环中 为了获得关注者总数 以控制循环的数量
        response = requests.get('https://www.zhihu.com/api/v4/members/'+self.zhihu_name+'/followers', headers=headers, params=params)
        
        #获得resposne的json格式 jd是字典类型
        jd=response.json()
        #关注者总数
        totals=jd['paging']['totals']
        
        #将关注者的信息放入data
        for dic in jd['data']:
            self.data.append(dic['name']+' '+dic['url']+' '+ dic['url_token']+'\n')
        
        #处理所有关注者
        for i in range(20,totals,20):
            params = (
                ('include', 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'),
                ('offset', str(i)),
                ('limit', '20'),
            )
        
            response = requests.get('https://www.zhihu.com/api/v4/members/'+self.zhihu_name+'/followers', headers=headers, params=params)
        
            print(response.status_code)
        
            jd=response.json()
        
            for dic in jd['data']:
                print(dic['name'],dic['url'])
                self.data.append(dic['name']+' '+dic['url']+' '+ dic['url_token']+'\n')
    
        print(len(self.data))
        
        #将信息存取在followers_info.txt中
        f=open('./followers_info.txt','w')
        f.writelines(self.data)
        f.close()
        

if __name__=='__main__':
    get=getFollowers('cai-che-qu-ming-33')
    get.get_and_store_followers()