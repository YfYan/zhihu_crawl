# 知乎爬虫

一个知乎用户可能自己关注的话题不多，为了获得更多的信息，可以爬取该用户关注者有关的问题、专栏等内容，进而可对该用户做用户画像。

代码在github上只给了最终版本version 2.0的，那个最快了。

## 知乎url的基本分析

知乎的url是非常有规律的

用户的url为： https://www.zhihu.com/people/ + 用户token

问题的url为：https://www.zhihu.com/question/ + 问题id

专栏的url为：https://zhuanlan.zhihu.com/ + 专栏id

因此，爬取的一个关键是获取这些token和id，之后就是通过获得的url爬取信息。另外对知乎的爬虫一定要有headers，否则会404。

# version 1.0

## 用户的关注者获取

![pic1](http://github.com/YfYan/YfYan.github.io/raw/master/images/pic1.png)

作为一个只初步了解爬虫的新手，一开始的基本思路自然是requests+BeautifulSoup。观察用户的关注者页面，翻页时是在url后加 ?page=X （X为页面），每一页有20个关注者，X的最大值根据关注者数量获得。然而真正跑的时候，BeauifulSoup通过正则表达只能在每个页面只能找出三个关注者，因为知乎的页面大多数都是异步加载的，右击页面的源代码里信息的很少的，页面的大多数信息都是JavaScript异步渲染的。念及我两天速成的稀烂js语法，我头大了。幸好找了半天，配置好了我实习阶段的第一个神器——selenium。 



selenium是一个web测试库，可以带动一个真实的Chrome，为网页中的JavaScript提供运行环境。这样以来，通过一个webdriver驱动一个Chome加载页面，这样之后通过page_source得到的页面html就是渲染过的了。原则上说，只要不怕慢，扔给一个url，都是完全加载出来的。



尽管如何，selenium使用过程也有很多坑。安装电脑Chrome版本对应的驱动到/usr/bin（mac用户）目录下，查看Chrome的版本：在空页面地址栏输入chrome://version，之后下载相应的版本即可。之后用用selenium打开知乎的url，知乎还是会报环境异常相关的错误，之后在运行前添加如下代码可正常运行：

```python
from selenium import webdriver
from selenium.webdriver import ChromeOptions
option = ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = webdriver.Chrome(options=option)
```

另外为提高速度，加载完一个页面，不要将webdriver关闭，因为每次打开Chrome都需要花费额外的时间，不如等所有的页面都搞定了再关掉webdriver。webdriver本身是可以通过DOM来定位xpath，但似乎这样会耗费更多的资源，所以本人还是用BeautifulSoup做正则表达。

## 关注者动态的获取

知乎用户的动态是可以通过鼠标往下拖再加载的，显然也是动态加载的，这里selenium可以模拟鼠标滚轮往下滑，滑一次可以多下载7个内容，同时要暂停一小段时间，否则会来不及加载。另外，图片信息是没有用的，不妨禁用图片加载，实现如下：

```python
import time
from selenium import webdriver
from selenium.webdriver import ChromeOptions
option = ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2} #禁止加载图片
option.add_experimental_option("prefs",prefs)
option.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = webdriver.Chrome(options=option)
for count in range(scroll_time): #scroll_time是预设的滚动次数
    driver.execute_script("window.scrollBy(0,3000)") #模拟鼠标滚轮滚动
    time.sleep(sleep_time) #暂停一小段时间供加载 实验得sleep_time最小0.2秒
```

这样就可以获得用户的问题、专栏等的url。

## 问题信息的获取

![pic4](http://github.com/YfYan/YfYan.github.io/raw/master/images/pic4.png)

上图是一个问题的图片，问题信息分为三部分，在上图中从上到下分为话题标签、标题、内容。很不幸，问题页面也是动态加载的，在Chrome中检查这三个部分，均不能在源代码中找到。如果这个也用selenium去做加载页面，实在是太慢了。观察页面的源代码，话题标签和标题在一个meta中可以找到，而较为完整的内容可以在源代码中的JavaScript中找到，用正则表达式可找。

![pic5](http://github.com/YfYan/YfYan.github.io/raw/master/images/pic5.png)

![pic6](http://github.com/YfYan/YfYan.github.io/raw/master/images/pic6.png)

爬取问题内容的正则表达式如下，目前使用还可以，但以后万一js改了需要进一步维护

```python
import re
pattern = re.compile(',"excerpt":"([\s\S]*)","commentPermission"') 
content=pattern.findall(script.text)[0] #script.text是页面源代码
```



# version 1.1

一个最原始的爬虫已经可以跑了，但问题是实在是太慢了，1.1版本主要是增加了多线程的功能。在并行处理方面，python主要有三种不同粒度的并行方法：多进程（muti-processing）、多线程（muti-threading）、协程（asyncio）。



多进程是进程数要和CPU核数相同，进程间通信较为麻烦。python中自带了封装好的mutiproccssing包，但mutiproccssing要在top of the module，否则会出can‘t pickel的问题，幸好老板给了[原因和解决方案](https://stackoverflow.com/questions/925100/python-queue-multiprocessing-queue-how-they-behave/925241#925241)，不然实在是一头雾水。



多线程是我最终采用的多线程方案，之后的各种任务我能多线程就多线程，看到spyder右下角CPU使用率90+非常爽。多线程的坑在于是否线程安全，python自带的数据结构，比如列表、字典都是线程安全的，但自己写的一些东西都不一定了，这个之后还会提到。个人觉得多线程的使用还是很灵活的，常用套路如下：

```python
import threading
class My_threading(threading.Thread):
  def __init__(self,arg):
    threading.Thread.__init__(self)
    self.args=args #arg是自定义函数的参数,事先先分割好
  def run(self):#重载run()方法
    my_function(self.arg) #my_function是想要多线程的函数
ths = [My_threading(args[i]) for i in range(thread_num)] #thread_num是线程数
for th in ths:
  th.start()
for th in ths:
  th.join()
```



协程据老板说也是非常有用的一个方法，可惜本人用的spyder对acyncio的支持不是很好，跑的时候会报错“RuntimeError: This event loop is already running”，在stackoverflow上查到一个方法说是可以解决，但我这儿似乎还是不work，这个坑暂时就先放着了，反正多线程挺好用的。

```python
import nest_asyncio
nest_asyncio.apply()
import asyncio
```



# version 1.2

多线程后速度大大提高，但又出了新的问题，爬的多了会出现验证码，实验后发现，只要在出现验证码后输入，再重新get那个url，就可以继续爬取了。多线程的时候，只要有一个线程的验证码输入完毕，其他线程的验证码问题也会自动解决。知乎登陆时的验证码是点击倒立的字，幸好这里没有这么麻烦，是输入四个字符。顺便一提，验证码图片的格式是base64的，非常有趣的一种用文本表示图片的方法，可以用base64库去解决。

<center>
<figure class="third">
  <img src = "http://github.com/YfYan/YfYan.github.io/raw/master/images/captcha39.png">
  <img src = "http://github.com/YfYan/YfYan.github.io/raw/master/images/captcha40.png">  
  <img src = "http://github.com/YfYan/YfYan.github.io/raw/master/images/captcha41.png">
</figure>
</center>

一开始的思路当然是看看有没有现成的库去处理，试用了采用OSR方法的pytesseract库，结果惨不忍睹，毕竟OSR是为了处理规则的图像中文字。那就只能采用自己标注数据+卷积神经网络训练的方法了。关于CNN，安利一篇自家学校的[CNN文章](http://github.com/YfYan/YfYan.github.io/raw/master/CNN.pdf)，零基础也可以看个大概，了解大致原理有利于调参。

首先要决定的问题上是验证码是整体预测还是切割后单个预测。简单的查阅要获得足够高的准确率，整体预测需要2万左右的训练集，事实上，1000个训练集我都标了一下午，我觉得标2万个不太现实，因此采取了分割后单个字符预测的方法。切割程序为crop_captcha.py

虽然验证码的图片都是60行150列的图片，但实际的验证码大约都是60行120列，如果直接平均分割成四份非常不准确。这里采用的策略是首先将图片灰度化，只留一个颜色通道，从左到右扫描，遇到第一个黑像素点设为起点，再从右到左扫描，遇到第一个黑像素点设为终点。把起点到终点区域的图像缩放成120列，之后再平均分成四份，目测结果还行，部分切割结果如下：

![pic7](http://github.com/YfYan/YfYan.github.io/raw/master/images/pic7.png)

之后的预测目标为，输入一个60 * 30 * 1的矩阵，经过神经网络和softmax层后返回一个one-hot label对应一个字符。在python中有很多机器学习的库，如果要快速实现想法的话，首推[Keras](https://keras.io/)，它把tensorflow作为backend，很多细节都隐藏了，除了第一层要指定数据维数外，其他层只需要指定每层的类型和activation函数即可，Keras会自动推测每层的维数。每次训练完成后，可以将整个网络存在本地，最后选择一个测试集效果最好的用于预测即可。本人最后采用的网络结构为：

```python
from keras.models import Sequential
from keras.layers import Conv2D,MaxPooling2D,Activation,Dense,Flatten
model=Sequential()#Sequential是Keras搭建神经网络的基本单位
model.add(Conv2D(filters=32,kernel_size=(5,5),activation='relu',input_shape=(60,30,1)))#加卷积层
model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2)))#加最大值池化层
model.add(Conv2D(filters=64,kernel_size=(5,5),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2)))
model.add(Flatten())
model.add(Dense(64,activation='relu'))#加全联接层
model.add(Activation('relu'))
model.add(Dense(num_class,activation='softmax'))#softmax层异常重要
```

调参主要能调的部分有：加多少层卷积层和池化层，filters和kernal_size，filters决定了下一层神经网络接受的图层数量，kernal_size是每次卷积或池化对多少像素做处理。具体调法是玄学，个人不是这方面的专家，也只能用控制变量法多试试了，最后要用的权重及网络结构存在cnn_captcha_v4.h5中，训练所在的文件为cnn_captcha.py



最后在captcha_predict.py中封装了一个Captcha_pred类，它会加载cnn_captcha_v4.h5中的网络，然后设定验证码图片的路径，再预测一个完整的结果(它会在内部完成分割)。由于单个预测的成功率约为90%，假设独立同分布，那么四个预测的成功率约为60%，有多线程的话，只要Chrome加载出来，几乎立刻就能预测出来。多线程还有其他的坑，Keras的后端tensorflow的session和graph在多线程会出问题，查了stackoverflow后，需要在Captcha_pred初始化化有所修改:

```python
import tensorflow as tf
from keras import backend as K
class Captcha_pred(object):#其他细节都忽略了 只写了多线程的坑
  def __init__(self):
    self.session = K.get_session()
    self.graph = tf.get_default_graph()
```

另外多线程时，验证码图片和分割后图片的命名都采用了随机数，这样可以防止命名冲突。



# version 2.0

在1.2版本后，在获取关注者动态的过程中，受制于selenium的加载页面速度，速度仍有大大提升的空间。老板教我一个好方法看network里的XHR和一个好用的工具mitm。

在滑动鼠标滚轮的过程中，其实是发出了一个XMLHttpRequest，得到的response是一个json格式的文档，再通过js加载到页面上，事实上json文档里已经有了所有需要的信息。同时response里还包含了下一次after_id，这个after_id决定了下一次的内容，实验后也发现after_id作为一个request的params，决定了该次请求返回的内容。

另外，这些XHR请求的url都是知乎的api，其他地方也都可以用，[整理点这里](https://www.jianshu.com/p/86139ab70b86) ，由此获得结构化数据比用正则等方法解析网页快的多。

```python
for count in range(scroll_num): #scroll_num相当于滚动次数
  if count == 0:
     params = (('limit', '7'),
               ('desktop', 'True'))
  else:
     params = (('limit', '7'),
               ('desktop', 'True'),
               ('after_id', after_id)) #after_id 在第一次循环之后才有
  response=requests.get('https://www.zhihu.com/api/v4/members/'+follower+'/activities', headers=headers, params=params) #xhr请求 知乎api
  jd=response.json()
  *********** #其他处理
  try:
    after_id=jd['paging']['next'].split('&')[2].split('=')[1] #获取after_id
  except:
    break #如果不存在after_id， 说明动态还没滚30下就没了 退出循环
```

最让我疑惑的是第一次after_id，它没有从再前一个获得了，我尝试了配置[mitmproxy](https://mitmproxy.org/)，用它监听了Chrome，再打开知乎，但似乎还是没有找到。之后实验了一下，直接在params里不放after_id，刚好就是最开始的7条内容。另外记录一下如何在mac命令行中打开一个无视证书，并设置代理的Chrome，这个找了一下午才找到:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --proxy-server='127.0.0.1:8080' --ignore-certificate-errors &> /dev/null &
```

之后只需要输入命名mitmweb，并在另一个浏览器（如safari）打开127.0.0.1:8080，即可监听Chrome中的内容。配合其他脚本，可以直接获取xhr，不需要每次对xhr先copy as cURL，在用在线工具转化为python的requests。虽然这次它似乎没有发挥功能，但如果要抓手机的包，这会是非常好用的。



回到爬虫，不需要用selenium滚动，我把scroll_time调成30次，仍然要比原来快，而且获取的信息多得多。对原本关注者url的获取也采取了类似的方法，采用了知乎的API，这样整个流程除了验证码输入，摆脱了selenium，速度大大提升。



## 流程重构

在version 1.x中，都是先获取关注者的主页url并存在本地，之后直接获取关注者的动态和相关动态的内容，这样做有两个缺点，一是第二步比较冗长，如果哪里出错了再调比较麻烦，二是很多问题都是重复的，这样爬取的重复率很高。

在version 2.0中，第一步仍然保持不变，第二步建立三个字典：用户-问题列表，用户-专栏列表，用户-关注话题列表，py可以把字典变成字符串存在本地，读取的时候eval一下就变回字典了。第三步把所有的问题放在一个，去重，对去重后的结果在爬取，可以快很多，在python中，只需要一行代码即可 ` questions = list(set(questions))` 。对专栏处理同理。

在进一步做用户画像的时候，由于字典是hash的，其实把用户和相关信息对应是O(1)的复杂度。



# 用户画像

获取用户关注者的各种信息后，可以通过文本挖掘的方法对用户进行分析。

在画像方法，也是试了很多的方法，最后能work的是tf-idf向量化，再做Kmeans聚类，获得关键词，做词云。



## tf-idf 向量化

先把单个关注者所有信息组成一个字符串，也就一篇article，有重复也加进去，这样就自带权重了。把所有的article放进一个列表，组成一个corpus，之后用sklearn的包tf-idf向量化

```python
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(stop_words=stopwords, tokenizer=tokenize) #stopwords是预先读取的挺次列表，tokenize是基于jieba.lcut自定义的分词韩函数
X = vectorizer.fit_transform(content) #content即为corpus X是向量化的结果
```

X是一个numpy的稀疏矩阵，行数为article的数量，列数是corpus中的词总数，第i行第j列的值即为第i篇文章，第j个单词在该文章中的tf-idf，j为单词在整个词库中的下标，不是在article i中的下标。

同时试过另一种组建corpus的方式，把一个问题的所有信息或一个专栏作为一个article，效果似乎也还好。



## Kmeans 聚类

向量化之后就可以用各种数值方法了，聚类方法里试了下最好用的似乎是Kmeans。先把聚类的数量设为10到30的区间，在根据肘部原则选择了目测比较合适的15类

```python
from sklearn.cluster import KMeans
centers = range(10,30)
models=[KMeans(n_clusrers=i,verbose=True) for i in centers]
score=[models[i].fit(X).score(X) for i in centers]
```

得到的聚类top词汇如下：

![pic8](http://github.com/YfYan/YfYan.github.io/raw/master/images/pic8.png)

之后做词云不知道怎么处理不同聚类top词汇的权重，可视化也就大致显示一下，就不放了。



## 填不完坑

感觉填不了坑挺多的

## 问题标签分类

如果能将问题的标签先做一个自动分类，在统计各类下问题的比重，显然是一个对用户画像的好办法。初步的想法是如果两个标签在同一个问题下出现，说明它们的距离比较近，如果两个标签要通过中间标签相连，则它们的距离较远。依此规则就可以构造出一个图，也就是affinity matrix。之后通过affinity propagation就能自动完成聚类。但是具体的距离构造怎么都想不出来一个合适的方法，也就作罢了。

另外numpy的内置函数计算是真的快，如果要自己循环做点什么实在是太慢了，就算要循环，也应该先转换为稀疏矩阵再循环。



## 测地线距离

在KMeans中，使用的是欧式距离，我想在再一次尝试上个坑中的思想，想采用测地线距离。

![pic9](http://github.com/YfYan/YfYan.github.io/raw/master/images/pic9.png)

在一个典型的面包卷中，左图是采用欧式距离的聚类结果，右图是采用测地线距离的聚类结果。

可以用floyd最短路算法近似测地线距离，但这是O(n^3)的时间复杂度，1万多个标签，稍微跑了一下，实在太慢了。

另外，在sklearn里的AgglomerativeClustering中可以设置连通性，达到相似的结果，但不接受稀疏矩阵X，变成普通矩阵后跑了一小时也没结果，也只能作罢。



# 图像处理

想帮一个同事在用OSR识别图像中的数字时提高准确率，也对python的一些图像处理做了了解。单纯就色度、对比度、锐度的调整，已经能够让图像稍微清晰一点了，[RGB与视觉的关系本身就很有意思](https://www.zhihu.com/question/265265004)。

另外的一个想法是用KMeans减少图片的颜色，让背景与数字的对比更加清晰。

还有一类超分辨率的方法，用一些奇奇怪怪的神经网络，获得比原图像素更高的图像。实验了一下，在github上找了一个能在终端跑的项目[ESPCN-Tensorflow](https://github.com/drakelevy/ESPCN-TensorFlow) ，跑之前把类似的图片放入images文件夹内做训练集，可惜这个项目是python2的，很多包要再pip2一遍。

