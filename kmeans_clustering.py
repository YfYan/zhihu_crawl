#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 17:41:46 2019

@author: xijinping
"""
from scipy import sparse
import jieba, re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
import re
import random
from sklearn.metrics.pairwise import euclidean_distances

#将questions_info读取 字典类型
f=open('questions_info.txt','r')
questions_info = eval(f.read())
f.close()

#将zhuanlans_info读取 字典类型
f=open('zhuanlans_info.txt','r')
zhuanlans_info = eval(f.read())
f.close()

with open('followers_questions.txt') as f:
    questions = f.read().splitlines()
    followers_questions={}
    for item in questions:
        itemList = item.split(' ')
        follower = itemList[0]
        followers_questions[follower] = itemList[1:]

with open('followers_topics.txt') as f:
    topics = f.read().splitlines()
    followers_topics = {}
    for item in topics:
        itemList = item.split(' ')
        follower = itemList[0]
        followers_topics[follower] = itemList[1:]
        #让jieba分词添加所有topic词汇 增加分词准确性
        for topic in itemList[1:]:
            jieba.add_word(topic)

with open('followers_zhuanlans.txt') as f:
    zhuanlans = f.read().splitlines()
    followers_zhuanlans = {}
    for item in zhuanlans:
        itemList = item.split(' ')
        follower=itemList[0]
        followers_zhuanlans[follower]=itemList[1:]

with open('followers_info.txt') as f:
    followers_info = f.read().splitlines()

content=[]

#对于一个关注者 把与之有关的所有内容都放在一个article里 允许重复 这样会提高重复部分的tf-idf值
for line in followers_info:
    follower = line.split(' ')[-1]
    current_content=''
    if followers_questions.get(follower)!=None:
        current_question = followers_questions[follower]
        for question in current_question:
            question_id = question.split('/')[-1]
            if questions_info.get(question_id)!=None:
                current_content+=questions_info[question_id]['title']+' '.join(questions_info[question_id]['topics'])+questions_info[question_id]['content']
    if followers_topics.get(follower)!=None:
        current_content+=' '.join(followers_topics[follower])
    
    if followers_zhuanlans.get(follower)!=None:
        current_zhuanlan = followers_zhuanlans[follower]
        for zhuanlan in current_zhuanlan:
            zhuanlan_id = zhuanlan.split('/')[-1]
            if zhuanlans_info.get(zhuanlan_id)!=None:
                current_content+=zhuanlans_info[zhuanlan_id]['title']+zhuanlans_info[zhuanlan_id]['intro']
    content.append(current_content)

def tokenize(sentence):
    without_duplicates = re.sub(r'(.)\1+', r'\1\1', sentence)
    without_punctuation = re.sub(r'[^\w]', '', without_duplicates)
    return jieba.lcut(without_punctuation)



#把每个问题的信息（标题+标签+内容）放进content
#for key,value in questions_info.items():
#    sentence=value['title']+' '+' '.join(value['topics'])+' '+value['content']
#    content.append(sentence)

#打乱
random.seed(10)
random.shuffle(content)


with open('stopwords.txt') as f:
    stopwords = f.read().splitlines()

vectorizer = TfidfVectorizer(stop_words=stopwords, tokenizer=tokenize)
#vectorizer = CountVectorizer(stop_words=stopwords,tokenizer=tokenize)
print("phase 1 done.")
X = vectorizer.fit_transform(content)

# 一个没有填的坑 用floyd算测地距离 速度太慢
def geodesic_floyd(X):
    dimension=X.shape
    distance=np.zeros((dimension,dimension))
    """
    """
    return distance

#Kmeans 通过肘部原则选择最合适的聚类数量 15左右比较合适 把这些都注释掉
#centers = range(15,25)
#models=[]
#for i in centers:
#    models.append(KMeans(n_clusters=i,verbose = False))
#
#score = []
#
#for i in range(len(models)):
#    score.append(models[i].fit(X).score(X))
#    print(i)
#    print('==================================')
#
#plt.gca().invert_yaxis()
#plt.plot(score)
#    
#print("Top terms per cluster:")
#order_centroids = models[0].cluster_centers_.argsort()[:, ::-1]
#terms = vectorizer.get_feature_names()
#for i in range(10):
#    print("X")
#    top_ten_words = [terms[ind] for ind in order_centroids[i, :15]]
#    print("Cluster {}: {}".format(i, ' '.join(top_ten_words)))
#    print(i)   

#没有填上的坑 想通过稍微修改距离的相对大小 但是用于kmeans时计算过于缓慢
#distance = euclidean_distances(X,X)
#distance = np.exp(distance) - 1
#distance = sparse.csr_matrix(distance)


final_model = KMeans(n_clusters=12,verbose=True,n_jobs=-1)
final_model.fit(X)

#没有填上的坑 Agglomerative可以使用测地线距离进行聚类
#final_model = AgglomerativeClustering(n_clusters=15,connectivity=True)
#final_model.fit(X.toarray())


terms = vectorizer.get_feature_names()
centroids = final_model.cluster_centers_.argsort()[:,::-1]

#这个类是废话的类
check_words=['采纳','会员']
cloud_words={}
for i in range(12):
    #top_words是代表词汇 weight是相应的权重
    top_words = [terms[ind] for ind in centroids[i, :20]]
    weight = final_model.cluster_centers_[i][centroids[i, :20]]
    flag=True
    for word in check_words:
        if word in top_words:
            flag=False
    if flag:
        print(weight)
        print(top_words)
        for i in range(len(top_words)):
            cloud_words[top_words[i]]=weight[i]/weight[0]


#没有填上的坑 SVD降维以后还原不回去         
#X_reduced = TruncatedSVD(n_components=3).fit_transform(X)
#
#做词云
wc=WordCloud(font_path='simfang.ttf',background_color='white')
wc.generate_from_frequencies(cloud_words)
plt.figure(figsize=(10,10),dpi=100)
plt.imshow(wc)    

    
    
    

