from lxml import etree
import pytesseract
import requests
import re
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
import numpy
import requests
import time
import hashlib
import json
from parsel import Selector

head = {
    'User-Agent': 'Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11',
    'Cookie': 's_ViewType=10; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_3873933078; ctu=b89fc343be9f57c7e6497ed347f181e53acef25861dd6cc642b3ea048eca1b4f; uamo=15081282707; _lxsdk_cuid=1706a8c6f65c8-05b62276ec41c-313f68-144000-1706a8c6f66c8; _lxsdk=1706a8c6f65c8-05b62276ec41c-313f68-144000-1706a8c6f66c8; _hc.v=43c9a00a-3629-9d64-f04c-ca92a0ae0f49.1582335554; cy=500; cye=gaopaidian; dper=f899f3495acee97041021c05bc9d10e35d9aa1dd058f4d75f599e04c4bfdbfa41ca6600103ebe8e69b259b2b426764f7ccc6f518556f65eb964c09b24ffc88ad45c375cef54eedf5ae51f137e1a00ceefaea5f7872dfbfa836a736c16f505a8b; dplet=63cc9e453fe0a80c4386ea9d7c8caede; _lxsdk_s=17070b551ea-3f-342-dd8%7C%7C23',
    'Referer': 'http://www.dianping.com/gaopaidian/ch10/g110',
    'Proxy-Connection': 'keep-alive'
}
# 提取订单
""" 
    orderId:提取订单号
    secret:用户密钥
    num:提取IP个数
    pid:省份
    cid:城市
    type：请求类型，1=http/https,2=socks5
    unbindTime:使用时长，秒/s为单位
    noDuplicate:去重，0=不去重，1=去重
    lineSeparator:分隔符
    singleIp:切换,0=切换，1=不切换
"""

orderId = "O202573520"
secret = "b9826454e1e73"
num = "1"
pid = "-1"
cid = ""
type = "1"
unbindTime = "60"
noDuplicate = "0"
lineSeparator = "0"
singleIp = "0"
time = str(int(time.time()))  # 时间戳

# 计算sign
txt = "orderId=" + orderId + "&" + "secret=" + secret + "&" + "time=" + time
sign = hashlib.md5(txt.encode()).hexdigest()
# 访问URL获取IP
url = "http://api.ipproxy.info:8422/api/getIp?type=1" + "&num=" + num + "&pid=" + pid + "&unbindTime=" + unbindTime + "&cid=" + cid + "&orderId=" + orderId + "&time=" + time + "&sign=" + sign + "&dataType=0" + "&lineSeparator=" + lineSeparator + "&noDuplicate=" + noDuplicate + "&singleIp=" + singleIp
my_response = requests.get(url).content
js_res = json.loads(my_response)

for dic in js_res["data"]:
    ip = dic["ip"]
    port = dic["port"]
    proxyUrl = "http://" + ip + ":" + str(port)
    proxy = {'http': proxyUrl, "https": proxyUrl}

print(proxy)
def getresponse(url):
    response = requests.get(url, proxies=proxy, headers=head)

    # print(response.text)
    return response


def fonturl(html):
    content = re.findall('type="text/css" href="(//s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/.*?.css)"', html)[0]
    print(content)
    content = 'https:' + content
    response = requests.get(content)
    # print(response.text)
    woffurl = re.findall(
        '@font-face{font-family: "PingFangSC-Regular-review";.*? format\("embedded-opentype"\),url\("(.*?)"\);} ',
        response.text)[0]
    font_name = woffurl.split('/')[-1]
    woffurl = 'https:' + woffurl
    font_content = requests.get(woffurl, proxies=proxy)
    with open(font_name, 'wb')as f:
        f.write(font_content.content)
    return font_name
    # return font_name


# 获取字体的映射规则
def font_convert(font_path):
    font = TTFont(font_path)  # 打开的字体文件
    # font.saveXML('font_xml')  # 将打开的字体文件保存成xml格式
    # map_list = base.getBestCmap() # 将文件中的映射规则转换出来
    # 创建一张图片
    im = Image.new('RGB', (1800, 1800), (255, 255, 255))
    image_draw = ImageDraw.Draw(im)
    # 并且创建一个字体对象。这个函数从指定的文件加载了一个字体对象，并且为指定大小的字体创建了字体对象。，已解决
    font1 = ImageFont.truetype(font_path, 40)
    # 获取glypyhorder字段的值，已解决
    code_list = font.getGlyphOrder()[2:]
    # print(code_list)
    # print(font_path)
    # 把所有字段提取到的内容等分成15份，已解决
    count = 15
    array_list = numpy.array_split(code_list, count)
    # print(array_list)
    for i in range(len(array_list)):
        # print('替换之前的', array_list[i])
        # 讲js的unicode码转化为python的unicode
        # print(len(array_list))
        new_list = [i.replace("uni", "\\u") for i in array_list[i]]
        # print('替换之后的', new_list)
        # 将列表变为字符串
        text = "".join(new_list)
        print(text)
        # print('列表变字符串', text)
        # encode decode
        # 把文字变成二进制
        # 将字符串进行反向编码
        text = text.encode('utf-8').decode('unicode_escape')
        # print('反向编码之后的', text)
        # 将文件绘制到图片
        # 指定字体进行绘制

        image_draw.text((0, 100 * i), text, font=font1, fill="#000000")
    # print(text)
    im.save("sss.jpg")
    # im.show()
    # im = Image.open("sss.jpg")  # 可以将图片保存到本地，以便于手动打开图片查看
    result = pytesseract.image_to_string(im, lang="chi_sim")
    # print(result)
    # # 去除空白及换行
    result_str = result.replace(" ", "").replace("\n", "")
    # 将内容替换成网页的格式，准备去网页中进行替换
    # print(code_list)
    # print(result_str)
    html_code_list = [i.replace("uni", "&#x") + ";" for i in code_list]
    # print(html_code_list)
    # print(len(html_code_list))
    # print(len(result_str))
    return dict(zip(html_code_list, list(result_str)))

#获取评论内容
def get_add(response):

    connect = Selector(response)

    adddress = connect.xpath('//ul[@class="comment-list J-list"]')
    for i in adddress:
        item = {}
        content = i.xpath('.//div[@class="content"]')
        for a in content:
            item['comment'] = ''.join(a.xpath('./p[2]/text()').getall())
            # print(item)
            #http://www.dianping.com/shop/15122272/review_all/p3翻页





    # adddress =''.join(adddress)







if __name__ == '__main__':
    respones = getresponse('http://www.dianping.com/shop/15122272')
    html = respones.text
    font_name = fonturl(html)
    ab = font_convert(font_name)
    #字体转换替换
    for key in ab:
        if key in html:
            html = html.replace(key,ab[key])
    a = get_add(html)
    print(a)
