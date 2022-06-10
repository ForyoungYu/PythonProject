import os
import re
import requests
from pyquery import PyQuery as pq
import jieba
import matplotlib.pyplot as plt


def getdata():
    """ 循环爬取网页新闻，并按照年份保存在 news 文件夹下 """

    # 请求头
    headers = {
        "User-Agent":
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }

    # 定义网页地址的基本变量
    homepage = "https://www.sdtbu.edu.cn"
    tail = ".htm"
    newspage = "/index/ssyw"

    totalpage = 335  # 设定总页数
    set = True  # 设定循环标志，为假时停止循环

    def getNewsText(href: str, homepage: str, headers: dict, filename: str):
        """ 保存新闻文本 """
        _ = re.search('/[\w, /]*.htm', href).group()  # 去掉「..」
        addr = homepage + _  # 合并网址
        news_response = requests.get(url=addr, headers=headers)  # 请求新闻页面
        news_response.encoding = 'utf-8'  # 设定 UTF-8 编码
        news_page = pq(news_response.text)
        news = news_page('div#vsb_content').text()
        with open(filename, "a") as f:  # 追加写入文件
            f.write(news)

    print("正在爬取...")
    for index in range(totalpage):
        if index == 0:
            url = homepage + newspage + tail  # https://www.sdtbu.edu.cn/index/ssyw.htm
        else:
            url = homepage + newspage + "/" + str(totalpage - index) + tail

        response = requests.get(url=url, headers=headers)  # 请求新闻列表页
        response.encoding = 'utf-8'  # 设定编码
        news_list_page = pq(response.text)
        lis = news_list_page('ul.list li').items()  # 返回可遍历列表

        if set is True:
            # 遍历新闻列表
            for i in lis:
                href = pq('li a', i).attr('href')  # 获取标签 href 属性值
                date = pq('li p', i).text()  # 获取完整新闻日期
                year = re.search('[0-9]*', date).group()  # 获取新闻年份
                if year >= "2022":
                    getNewsText(href, homepage, headers, "news/2022.txt")
                if "2022" > year >= "2021":
                    getNewsText(href, homepage, headers, "news/2021.txt")
                if "2021" > year >= "2020":
                    getNewsText(href, homepage, headers, "news/2020.txt")
                if "2020" > year >= "2019":
                    getNewsText(href, homepage, headers, "news/2019.txt")
                if "2019" > year >= "2018":
                    getNewsText(href, homepage, headers, "news/2018.txt")
                if "2018" > year >= "2017":
                    getNewsText(href, homepage, headers, "news/2017.txt")
                if "2017" > year >= "2016":
                    getNewsText(href, homepage, headers, "news/2016.txt")
                if "2016" > year >= "2015":
                    getNewsText(href, homepage, headers, "news/2015.txt")
                if year < "2015":
                    print("爬取日期截至")
                    set = False
                    break  # 跳出循环
        else:
            break  # 跳出循环

    print("新闻爬取结束")


def wordStatustics(year: int, file: str) -> list:
    """
    统计前十个高频词汇出现的个数

    args:
        year - 年份
        file - 要打开的年份文件
    return:
        前十个高频词汇列表
    """
    txt = open(file, "r", encoding="utf-8").read()
    words = jieba.lcut(txt)  # 将文本导入
    wordsDict = {}  # 新建字典用于储存词及词频
    for word in words:
        if len(word) == 1:  # 单个的字符不作为词放入字典(其中包括标点)
            continue
        elif word.isdigit() == True:  # 剔除数字
            continue
        elif word in wordsDict:
            wordsDict[word] += 1  # 对于重复出现的词，每出现一次，次数增加1
        else:
            wordsDict[word] = 1

    wordsDict_seq = sorted(wordsDict.items(), key=lambda x: x[1],
                           reverse=True)  #按字典的值降序排序
    print("Year:", year)
    print(wordsDict_seq[:10])  # 输出前10个高频词
    return wordsDict_seq[:10]


def drawBarChart(newsWithYear: list):
    """
    绘制柱状图并保存在 saved_barchart 文件夹下
    
    agrs:
        newsWithYear - 每年的词频列表 
    """
    if not os.path.exists('saved_barchart'):
        os.makedirs("saved_barchart/")
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设定绘图字体
    year = 2022
    for yearTuple in newsWithYear:
        words = []
        num = []
        for tuple in yearTuple:
            words.append(tuple[0])
            num.append(tuple[1])
        plt.bar(words, num)
        plt.title(year)
        plt.savefig("saved_barchart/" + str(year) + ".png")
        plt.show()
        year -= 1


if __name__ == "__main__":
    if not os.path.exists('news/'):
        os.makedirs('news/')
        getdata()

    newsWithYear = []
    for year in range(2022, 2014, -1):
        words = wordStatustics(year, str("news/" + str(year) + ".txt"))
        newsWithYear.append(words)

    drawBarChart(newsWithYear)