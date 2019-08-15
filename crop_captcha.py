#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 10:40:39 2019

@author: xijinping
"""

"""
此程序将训练集中的验证码做切分 
切分的规则是先找到验证码像素始末位置 平均切成四份 再resize成30*60
还有另一种规则 在末尾注释里 效果目测不如现在的规则
"""
from PIL import Image
import pylab
import numpy as np
import math

#找到一个验证码实际开始结束的像素位置 返回始末位置
def find_start_end(im_array):
    start,end=1000,1000
    shape=im_array.shape
    width=shape[1]
    #列数从前向后循环寻找开始
    for i in range(width):
        #某一列不全是白色像素点 说明验证码从这里开始
        if np.sum(im_array[:,i])<254*60:
            start=i
            break
    #列数从后向前循环寻找结束
    for i in range(width-1,0,-1):
        if np.sum(im_array[:,i])<254*60:
            end=i
            break
    return start,end

#指定宽度final_width 返回含有最多像素点的开始位置
def find_best_start(im_array,final_width=120):
    shape=im_array.shape
    width=shape[1]
#    height=shape[0]
    best=[]
    mi=1e10
    for i in range(width-final_width):
        SUM=np.sum(im_array[:,i:i+final_width+1])
        if SUM<mi:
            mi=SUM
            best=[]
            best.append(i)
        elif SUM == mi:
            best.append(i)
    return int(np.median(best))

#将图片左右两边扩展 扩展宽度为discrepancy 扩展方法是全部变成白色
def fill_blank(im_array,discrepancy):
    left=int(discrepancy/2)
    right=discrepancy-left
    a=np.zeros((60,left))
    b=np.zeros((60,right))
    a.fill(254)
    b.fill(254)
    im_array=np.hstack((a,im_array))
    im_array=np.hstack((im_array,b))
    return im_array

if __name__=='__main__':
    for i in range(1000):
        pil_im=Image.open('./captcha/'+str(i)+'.png').convert('L')
        im=pylab.array(pil_im)
        start,end=find_start_end(im)
        pcrop=pil_im.crop((start,0,end,60))
        pcrop=pcrop.resize((120,60))
        """
           切割方法1
        """
        for k in range(4):
            single=pcrop.crop((30*k,0,30*(k+1),60))
            single.save('./single_captcha/data/'+str(i)+'_'+str(k)+'.png')
        print(i)
            
        """
           切割方法2
        """
#        if end-start+1>120:
#            l=120
#            start=find_best_start(im,l)
#            w=int(l/4)
#            for k in range(4):
#                single=pil_im.crop((start+k*w,0,start+(k+1)*w,60))
#                single.save('./single_captcha/data/'+str(i)+'_'+str(k)+'.png')
#            print(i)
#        else:
#            im=im[:,start:end+1]
#            clen=end-start+1
#            upper=math.ceil(clen/4)*4
#            im=fill_blank(im,upper-clen)
#            print(im.shape)
#            w=int(upper/4)
#            single_discrepency=30-w
#            for k in range(4):
#                single_im=im[:,k*w:(k+1)*w]
#                single_im=fill_blank(single_im,single_discrepency)
#                single=Image.fromarray(single_im.astype('uint8')).convert('L')
#                single.save('./single_captcha/data/'+str(i)+'_'+str(k)+'.png')
#                
     