#!/usr/bin/env python
# encoding: utf-8
'''
@author: P.G
@contact: wxplmm@outlook.com
@file: DouBan_YP.py
@time: 2018/9/7 18:40
@desc: 
抓取网页数据
清理数据
用词云进行展示

代码整理
'''

import warnings
import jieba    #分词包
import numpy    #numpy计算包
import re
import pandas as pd
import matplotlib.pyplot as plt
from urllib import request
from bs4 import BeautifulSoup as bs
from wordcloud import WordCloud#词云包

# 解析网页函数
def getNowPlayingMovie_list():
    resp = request.urlopen('https://movie.douban.com/nowplaying/hangzhou/')
    html_data = resp.read().decode('utf-8')

    soup = bs(html_data, 'html.parser')
    # 解析电影id和电影名-目的是抓取后续短评内容时传递参数需要
    nowplaying_movie = soup.find_all('div', id = 'nowplaying')
    nowplaying_movie_list = nowplaying_movie[0].find_all('li', class_ = 'list-item')  # 查找class，用 class_ 下划线???
    # 内容保存在list中
    nowplaying_list = []
    for item in nowplaying_movie_list:
        nowplaying_dic = {}
        nowplaying_dic['id'] = item['data-subject']
        for tag_img_item in item.find_all('img'):
            nowplaying_dic['name'] = tag_img_item['alt']
            nowplaying_list.append(nowplaying_dic)

    return nowplaying_list

#爬取评论函数
def getCommentsById(movieId,pageNum):
    eachCommentList = []
    if pageNum > 0:
        start = (pageNum - 1) * 20
    else:
        return False
    requrl = 'https://movie.douban.com/subject/' + movieId + '/comments' + '?' + 'start='+str(start) + '&limit=20'
    print(requrl)
    resp = request.urlopen(requrl)
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data, 'html.parser')
    comment_div_lits = soup.find_all('div', class_ = 'comment')
    for item in comment_div_lits:
        comment_item = item.find('span', class_ = 'short').string
        if comment_item is not None:
            eachCommentList.append(comment_item)
    return eachCommentList

def main():
    # 循环获取第一个电影的前20页影评
    commonList=[]
    NowPlayingMovie_list = getNowPlayingMovie_list()
    for i in range(10):
        num = i+1
        commonList_temp = getCommentsById(NowPlayingMovie_list[0]['id'],num)
        commonList.append(commonList_temp)

    # 将列表中的数据转换为字符串
    comments = ''
    for k in range(len(commonList)):
        comments = comments + (str(commonList[k])).strip()

    # 使用正则去掉标点
    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    filterdata = re.findall(pattern, comments)
    cleaned_comments = ''.join(filterdata)

    # 使用‘结巴’分词库进行中文分词
    segment = jieba.lcut(cleaned_comments)
    words_df = pd.DataFrame({'segment': segment})

    # 去掉停用词
    stopwords = pd.read_csv('chineseStopWords.txt', index_col = False, quoting = 3, sep = "\t", names = ['stopword'],encoding = 'gbk')  # quoting=3全不引用
    words_df = words_df[~words_df.segment.isin(stopwords.stopword)]

    # 统计词频
    # words_stat = words_df.groupby(by=['segment'])['segment'].agg({"计数":numpy.size})
    # 上面代码改成下面代码就可以了。应该是版本问题。
    words_stat = words_df.groupby(by = ['segment'])['segment'].agg(numpy.size)
    words_stat = words_stat.to_frame()
    words_stat.columns = ['计数']
    words_stat = words_stat.reset_index().sort_values(by = ["计数"], ascending = False)

    #用词云进行显示
    wordcloud = WordCloud(font_path = "simhei.ttf", background_color = "black", max_font_size = 80)  # 指定字体类型、字体大小和字体颜色
    word_frequence = {x[0]: x[1] for x in words_stat.head(1000).values}
    word_frequence_list = []
    # 嵌套list
    for key in word_frequence:
        temp = (key, word_frequence[key])
        word_frequence_list.append(temp)

    # fit_words里应该是dict字典格式
    wordcloud = wordcloud.fit_words(dict(word_frequence_list))
    plt.imshow(wordcloud)

    plt.axis('off')  # show x, y axis or not
    plt.show()

main()