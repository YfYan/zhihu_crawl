#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 15:42:06 2019

@author: xijinping
"""
import numpy as np
import keras
from PIL import Image
import pylab
from keras.models import Sequential
from keras.layers import Dense, Dropout,Flatten
from keras.layers import Conv2D,MaxPooling2D,Activation,Conv1D
from keras.models import load_model

mapList = ['3','4','5','6','7','8','9','a','b','d','e','f','g','h','j','k',
           'm','n','p','r','s','t','u','v','x','y']
num_class=len(mapList)

f=open('captcha.txt','r')
all_captcha=f.readlines()
label=[]
for i in range(len(all_captcha)):
    string=all_captcha[i]
    s=string.split(' ')
    for j in range(4):
        label.append(s[1][j])
        
int_label=np.zeros((4000,1))
#int_label_test=np.zeros((400,1))
for i in range(4000):
    int_label[i]=mapList.index(label[i])
y_train=keras.utils.to_categorical(int_label,num_classes=num_class)

#for i in range(400):
#    int_label_test[i]=mapList.index(label[3600+i])
#y_test=keras.utils.to_categorical(int_label_test,num_classes=num_class)

x_train=np.zeros((4000,60,30,1))
#x_test=np.zeros((400,60,30,1))

for i in range(1000):
    for j in range(4):
        pil_im=Image.open('./single_captcha/data/'+str(i)+'_'+str(j)+'.png')#.convert('RGB')
        im=pylab.array(pil_im)
        im=im/255.0
        x_train[i*4+j,:,:,0]=im

#for i in range(100):
#    for j in range(4):
#        pil_im=Image.open('./single_captcha/data/'+str(900+i)+'_'+str(j)+'.png')
#        im=pylab.array(pil_im)
#        im=im/255.0
#        x_test[i*4+j,:,:,0]=im


model=Sequential()
model.add(Conv2D(filters=32,kernel_size=(5,5),activation='relu',input_shape=(60,30,1)))
#model.add(Conv2D(filters=3,kernel_size=(15,6),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2)))
#model.add(Conv2D(filters=3,kernel_size=(3,3),activation='relu'))
model.add(Conv2D(filters=64,kernel_size=(5,5),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2)))
model.add(Flatten())
#model.add(Dense(64))
#model.add(Activation('relu'))
model.add(Dense(64,activation='relu'))
model.add(Activation('relu'))
model.add(Dense(num_class,activation='softmax'))
model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

model.fit(x_train,y_train,batch_size=32,epochs=20,verbose=1,validation_split=0.3)

model.save('cnn_captcha_v6.h5')

#score=model.evaluate(x_test,y_test)

def pred_index(y_pred,num_class=26):
    index=-1
    mx=-1
    for i in range(num_class):
        if y_pred[0][i]>mx:
            index=i
            mx=y_pred[0][i]
    return index

def pred_char(dirname,model):
    x=np.zeros((1,60,30,1))
    pil=Image.open(dirname)
    im=pylab.array(pil)
    im=im/255.0
    x[0,:,:,0]=im
    y_pred=model.predict(x)
    index=pred_index(y_pred,26)
    return mapList[index]