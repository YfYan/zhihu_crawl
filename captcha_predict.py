#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 09:32:18 2019

@author: xijinping
"""
import os
import shutil
import numpy as np
from PIL import Image
import pylab
from keras.models import load_model
import random
import tensorflow as tf
from keras import backend as K

class Captcha_pred(object):
    """
    能预测的验证码要求 width=150px，height=60px，不然可能出错
    """
    def __init__(self):
        #预测时下标到字符的集合
        self.mapList = ['3','4','5','6','7','8','9','a','b','d','e','f','g','h','j','k',
                   'm','n','p','r','s','t','u','v','x','y']
        self.num_class=len(self.mapList)
        #预先训练好的cnn模型在cnn_captcha_vX.h5中
        self.model=load_model('./cnn_captcha_v4.h5')
        self.model._make_predict_function()
        self.dirname=''
        #下面两步保证在多线程时可以正常运行 没有的话多线程会报错
        self.session = K.get_session()
        self.graph = tf.get_default_graph()
        
        #随机数 用于命名 防止多线程命名冲突
        self.ra=0
        
        #初始化时删除并清空to_be_classified文件夹 并重新创建
        try:
            shutil.rmtree('./to_be_classified')
        except:
            pass
        os.mkdir('./to_be_classified')
    
    #dirname是要预测的完整的验证码图片的地址 self.ra是切割完单个验证码名称的前半部分
    def set_dirname(self,dirname):
        self.ra=random.random()
        self.dirname=dirname
        
    #之前要先set_dirname
    def pred_whole_captcha(self):
        self.crop_captcha()
        ans=""
        for k in range(4):
            single_dirname='./to_be_classified/'+str(self.ra)+'_'+str(k)+'.png'
            single_char=self.pred_single_char(single_dirname)
            ans=ans+single_char
        return ans
    
    #寻找始末位置
    @staticmethod
    def find_start_end(im_array):
        start,end=1000,1000
        shape=im_array.shape
        width=shape[1]
        for i in range(width):
            if np.sum(im_array[:,i])<254*60:
                start=i
                break
        
        for i in range(width-1,0,-1):
            if np.sum(im_array[:,i])<254*60:
                end=i
                break
        
        return start,end
    
    #切割验证码 放在to_be_classified里
    def crop_captcha(self):
        #to_be_classified文件夹用于存放切割完的四张验证码
        pil_im=Image.open(self.dirname).convert('L')
        im=pylab.array(pil_im)
        start,end=self.find_start_end(im)
        pcrop=pil_im.crop((start,0,end,60))
        pcrop=pcrop.resize((120,60))
        for k in range(4):
            single=pcrop.crop((30*k,0,30*(k+1),60))
            single.save('./to_be_classified/'+str(self.ra)+'_'+str(k)+'.png')
        
    def pred_index(self,y_pred):
        #根据模型预测的softmax概率 找出概率最大的那个
        index=-1
        mx=-1
        for i in range(self.num_class):
            if y_pred[0][i]>mx:
                index=i
                mx=y_pred[0][i]
        return index
    
    def pred_single_char(self,single_dirname):
        #single_dirname是切割好的单个验证码的路径
        x=np.zeros((1,60,30,1))
        pil=Image.open(single_dirname)
        im=pylab.array(pil)
        im=im/255.0
        x[0,:,:,0]=im
        y_pred=self.model.predict(x)
        index=self.pred_index(y_pred)
        return self.mapList[index]
    
    def clear(self):
        shutil.rmtree('./to_be_classified')
        os.mkdir('./to_be_classified')
    
if __name__=='__main__':
    #对一个小的测试集测试 算成功率 以此选择之前训练好的各种不同结构的模型
    f=open('./captcha_test.txt','r')
    test_raw=f.readlines()
    test=[]
    for string in test_raw:
        s=string.split(' ')
        test.append(s[1][:4])
    
    pred=Captcha_pred()
    count=0
    for i in range(len(test)):
        dirname='./captcha/captcha'+str(i)+'.png'
        pred.set_dirname(dirname)
        ans=pred.pred_whole_captcha()
        print(ans,test[i])
        
        if ans == test[i]:
            count+=1
    
    print(count,count/len(test))
    
    pred.clear()
    