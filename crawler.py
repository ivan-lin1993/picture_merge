import io
import random
import threading
import time

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SCROLL_PAUSE_TIME = 0.2
binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
driver = webdriver.Firefox(firefox_binary=binary, executable_path='geckodriver.exe')
url = "https://www.pexels.com/search/sea/"
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
    wait_count = 0
    while True:
        # Scroll down
        driver.execute_script("window.scrollBy(0, screen.height);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return window.scrollY")
        print(last_height,new_height)
        if new_height == last_height:
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "js-loading"))
                )
            finally:
                break
        #     wait_count += 1
        #     if wait_count > 10:
        #         break
        #     else:
        #         time.sleep(0.4)
        # else:
        #     wait_count = 0
        last_height = new_height
        imglistdiv = driver.find_elements_by_class_name("photo-item__img")
        if len(imglistdiv) > 80:
            driver.execute_script("var mlist = document.getElementsByClassName('photo-item__img'); for(var i=0;i<mlist.length;i+=1){mlist[i].className='done';}")
    time.sleep(5)
    # imglistdiv = driver.find_elements_by_class_name("photo-item__img")

    print(len(imglistdiv))
    
    
    # for img in imglistdiv:
    #     imgurl = img['src']
    #     # print(imgurl)
    #     threading._start_new_thread(download_img,(imgurl,))
        # download_img(imgurl)

def main():
    page = 1

    # while True:
    driver.get(url)
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
