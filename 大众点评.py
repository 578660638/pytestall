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

head = {
    'User-Agent': 'Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11',
    'Cookie': 's_ViewType=10; dper=f899f3495acee97041021c05bc9d10e30994cb275efcc444ce7ec4505ec28d5d268c59c6324c5f0796e03de378b4b614eb72abd8fef1ff3aaa3c46efd7516897; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_3873933078; ctu=b89fc343be9f57c7e6497ed347f181e53acef25861dd6cc642b3ea048eca1b4f; uamo=15081282707; _lxsdk_cuid=1706a8c6f65c8-05b62276ec41c-313f68-144000-1706a8c6f66c8; _lxsdk=1706a8c6f65c8-05b62276ec41c-313f68-144000-1706a8c6f66c8; _hc.v=43c9a00a-3629-9d64-f04c-ca92a0ae0f49.1582335554; cy=500; cye=gaopaidian; dplet=26e60b17e0ec766229f7681c0f9aaff6; _lxsdk_s=1706c330fa0-bf5-543-037%7C%7C3',
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

orderId = "O2】"
secret = "b98】"
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


def getresponse(url):
    response = requests.get(url, proxies=proxy,headers=head)

    # print(response.text)
    return response


def fonturl(html):
    content = re.findall('type="text/css" href="(//s3plus.sankuai.com/v1/mss_.*?/svgtextcss/.*?.css)"', html)[0]
    # print(content)
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
    font.saveXML('font_xml')  # 将打开的字体文件保存成xml格式
    # map_list = base.getBestCmap() # 将文件中的映射规则转换出来
    # 创建一张图片
    im = Image.new('RGB', (1800, 1800), (255, 255, 255))
    # 获取需要绘制的原始图像
    code_list = font.getGlyphOrder()[2:]
    print(code_list)
    image_draw = ImageDraw.Draw(im)
    # 字体图片，需要传入字体
    print(font_path)
    font1 = ImageFont.truetype(font_path, 40)
    # 把所有文字等分成15份
    count = 15
    array_list = numpy.array_split(code_list, count)
    print(array_list)
    for i in range(len(array_list)):
        print('替换之前的', array_list[i])
        # 讲js的unicode码转化为python的unicode
        new_list = [i.replace("uni", "\\u") for i in array_list[i]]
        # print('替换之后的', new_list)
        # 将列表变为字符串
        text = "".join(new_list)
        # print('列表变字符串', text)
        # encode decode
        # 把文字变成二进制
        # 将字符串进行反向编码
        text = text.encode('utf-8').decode('unicode_escape')
        # print('反向编码之后的', text)
        # 将文件绘制到图片
        # 指定字体进行绘制
        image_draw.text((0, 100 * i), text, font=font1, fill="#000000")

    im.save("sss.jpg")
    im.show()
    im = Image.open("sss.jpg")  # 可以将图片保存到本地，以便于手动打开图片查看
    result = pytesseract.image_to_string(im, lang="chi_sim")
    print(result)
    # # 去除空白及换行
    result_str = result.replace(" ", "").replace("\n", "")
    # 将内容替换成网页的格式，准备去网页中进行替换
    print(code_list)
    html_code_list = [i.replace("uni", "&#x") + ";" for i in code_list]
    print(html_code_list)
    # print(len(html_code_list))
    # print(len(result_str))
    return dict(zip(html_code_list, list(result_str)))


if __name__ == '__main__':
    respones = getresponse('http://www.dianping.com/shop/15122272')
    html = respones.text
    # with open('替换之前.html','w',encoding='utf-8')as f:
    #     f.write(html)
    font_name = fonturl(html)
    print('sadsadsad')
    ab = font_convert(font_name)
    print(ab)
