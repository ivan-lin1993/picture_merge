from PIL import Image,ImageDraw
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time
import threading
import io
import random


SCROLL_PAUSE_TIME = 0.2
driver = webdriver.Firefox()
url = "https://pixabay.com/zh/photos/?cat=nature&pagi="
size = 25

def calc_color_avg(img):
    total = (0,0,0)
    
    ori_width = img.size[0]
    ori_height = img.size[1]
    for y in range(ori_height):
        for x in range(ori_width):
            pixel = img.getpixel((x,y))
            total = (
                total[0]+pixel[0],
                total[1]+pixel[1],
                total[2]+pixel[2],
            )
    m_sum = ori_height * ori_width
    return [int(total[0]/ m_sum),int(total[1]/ m_sum),int(total[2]/ m_sum)]



def download_img(imgurl):
    print(imgurl)
    try:
        res = requests.get(imgurl)
        img = Image.open(io.BytesIO(res.content))
        img = img.resize((size,size))
        color = calc_color_avg(img)
        filename = ",".join([str(i) for i in color])
        img.save("pic/total/{}-{}.jpg".format(filename,str(int(random.random()*10000))))
    except Exception as e:
        print(e)
        pass

def load_page(page):
    last_height = driver.execute_script("return window.scrollY")
    print("load page")
    while True:
        # Scroll down
        driver.execute_script("window.scrollBy(0, screen.height);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return window.scrollY")
        print(last_height,new_height)
        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source
    soup = BeautifulSoup(html, 'html5lib')
    imglistdiv = soup.findAll("div", {"class": "item"})
    print(len(imglistdiv))

    for img in imglistdiv:
        imgurl = img.find('img')['src']
        # print(imgurl)
        threading._start_new_thread(download_img,(imgurl,))
        # download_img(imgurl)

def main():
    page = 1

    while True:
        driver.get(url+ str(page))
        load_page(page)
        page += 1
        time.sleep(1)

def test():
    res = requests.get('https://cdn.pixabay.com/photo/2018/05/13/01/39/fantasy-3395135__340.jpg')
    img = Image.open(io.BytesIO(res.content))
    color = calc_color_avg(img)
    print(color)
    filename = " ,".join(color)
    print(filename)
    

if __name__ == '__main__':
    main()
    # test()
    