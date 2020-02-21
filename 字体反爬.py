import requests
import re
from fontTools.ttLib import TTFont


eng_to_num={'period':'.','nine':'9',  'seven':'7', 'eight':'8', 'four':'4','one':'1','zero':'0','five':'5','six':'5','three':'3','two':'2'}
# 1.下载html
def getresponse(url):
    head={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
    }

    response = requests.get(url,headers=head)
    return response
#得到下载字体的地方
def get_font(font_url):
    font_url = re.findall("format\('eot'\); src: url\('(.*?)'\) format\('woff'\)", response.text)[0]
    font_name = font_url.split('/')[-1]
    font_content = requests.get(font_url)
    with open(font_name,'wb')as f:
        f.write(font_content.content)
    return font_name
#将下载的字体进行映射
def get_map_url(font_name):
    base = TTFont(font_name)
    base.saveXML('font_xml')
    map_list = base.getBestCmap()
    #取出键，作为键取值，=映射后的值
    for key in map_list.keys():
        map_list[key]=eng_to_num[map_list[key]]
    return map_list


if __name__ == '__main__':
    url = 'https://book.qidian.com/info/1013919744'
    response = getresponse(url)
    #替换之前的代码
    old_html =response.text
    # with open('替换之前.html','w',encoding='utf-8')as f:
    #     f.write(old_html)
    name = get_font(response)

    map_list = get_map_url(name)
    print(map_list)
    # zhoutuijian = re.findall('<span class=.*?>(.*?)</span></em><cite>',response.text)
    for key,value in map_list.items():
        new_html = old_html.replace('$#'+str(key)+';',value)
        print(new_html)

