import io
import json
import math
import os
import queue
import threading
import time
import sys
import getopt

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFilter

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


SCROLL_PAUSE_TIME = 0.2
binary = FirefoxBinary(r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe')
driver = webdriver.Firefox(firefox_binary=binary, executable_path='geckodriver.exe')
url = "https://pixabay.com/zh/photos/?q=nature&hp=&image_type=&order=&cat=&min_width=&min_height=&pagi="
# url = "https://www.pexels.com/search/nature/"
page = 0
mqueue = queue.Queue()
lqueue = queue.Queue()
pro_que = queue.Queue()

class Merge_Pic():
    def __init__(self, origin_path, halfwork_path= None, record_path=None):
        self.origin_path = origin_path
        self.halfwork_path = halfwork_path
        self.record_path = record_path
        
        if origin_path is not None:
            self.is_half_work = False
            self.pic_name = self.origin_path.split('/')[-1].split('.')[0]
            print(origin_path)
            print(self.pic_name)
        else:
            self.is_half_work = True
            self.pic_name = self.halfwork_path.split('/')[-1].split('.')[0]
        try:
            config = open('config.json','r')
            content = config.read()
            obj = json.loads(content)
            self.nscale = obj['nscale']
            self.mask_scale = obj['mask_scale']
            self.past_size = obj['past_size']
        except:
            print("Not Exists Config")
            print("Creating default config...")
            config = open('config.json','w')
            obj = {
                "nscale" : 120,
                "mask_scale" : 20,
                "past_size" : 10
            }
            self.nscale = 120
            self.mask_scale = 20
            self.past_size = 10
            config.write(json.dumps(obj))
        config.close()


    def mother_pic_init(self):
        print("init mother pic")
        if self.is_half_work is True:
            half_img = Image.open(self.halfwork_path,'r')
            w,h = half_img.size
            savefile = open(self.record_path,'r').read()
            rest_struct = json.loads(savefile)
            mother_pic_struct = []
            for rest_piece in rest_struct:
                mother_pic_struct.append(
                    [tuple(rest_piece[0]),tuple(rest_piece[1])]
                )
            result_img = half_img
        else:
            ## get mother pic 
            mother_pic = Image.open(self.origin_path)
            w, h = mother_pic.size
            # if w > h:
            #     mother_pic=resize_imgae(mother_pic, w)
            #     length = w
            # else:
            #     mother_pic=resize_imgae(mother_pic, h)
            #     length = h
            
            ## analize the color 要拿到打馬後的整張顏色結構 list 存
            print("start analize....")
            mother_pic, mother_pic_struct = draw_mask(mother_pic, self.mask_scale , self.nscale)
            
            mother_pic.save('ori_blur.jpg')
            w_len = int((w / mp.mask_scale) * mp.nscale)
            h_len = int((h / mp.mask_scale) * mp.nscale)
            result_img = Image.new('RGB',(w_len,h_len))


        return result_img, mother_pic_struct


def to_gray(mlist):
    total = 0.0
    for i in mlist:
        total += i
    return tuple([int(total/3)] * 3)


def draw_avg_color2(srcimg,resimg,X,Y,scale,nscale):
    total = (0,0,0)
    point_list=[]
    for y in range(Y,Y+scale):
        if y >= srcimg.size[1]:
            pass
        else:
            for x in range(X,X+scale):
                if x >= srcimg.size[0]:
                    pass
                else:
                    pixel = srcimg.getpixel((x,y))
                    total = (
                        total[0]+pixel[0],
                        total[1]+pixel[1],
                        total[2]+pixel[2],
                    )
                    point_list.append((x,y))
    m_sum = scale * scale
    avg_color = ( int(total[0]/ m_sum),int(total[1]/ m_sum),int(total[2]/ m_sum))
    fill_img = Image.new("RGB",(nscale,nscale),avg_color)
    # resimg.putpixel((int(X/scale),int(Y/scale)), avg_color)
    X = int((X/scale)) * nscale
    Y = int((Y/scale)) * nscale
    resimg.paste(fill_img,(X,Y,X+nscale,Y+nscale))
    return resimg, avg_color


def draw_avg_color(img,X,Y,scale):
    total = (0,0,0)
    point_list=[]
    for y in range(Y,Y+scale):
        if y >= img.size[1]:
            pass
        else:
            for x in range(X,X+scale):
                if x >= img.size[0]:
                    pass
                else:
                    pixel = img.getpixel((x,y))
                    total = (
                        total[0]+pixel[0],
                        total[1]+pixel[1],
                        total[2]+pixel[2],
                    )
                    point_list.append((x,y))
    m_sum = scale * scale
    avg_color = ( int(total[0]/ m_sum),int(total[1]/ m_sum),int(total[2]/ m_sum))
    for point in point_list:
        img.putpixel(point, avg_color)
    return img, avg_color

def draw_mask(img, scale, nscale):
    ori_width, ori_height = img.size
    total = (ori_height/scale) ** 2
    img_arr=[]
    img2 = Image.new('RGB',(int(ori_width/scale) * nscale, int(ori_height/scale) * nscale))
    # for y in range(0, ori_height, scale):
    #     for x in range(0, ori_width, scale):
    #         img2, avg_color = draw_avg_color(img2,x,y,scale)
    #         mqueue.put((x,y),avg_color)
    #         img_arr.append([(x,y),avg_color])
    #         print("{}%".format(round(float(len(img_arr)/total)*100,2)), end = "\r")
    for y in range(0, ori_height, scale):
        for x in range(0, ori_width, scale):
            img2, avg_color = draw_avg_color2(img,img2,x,y,scale,nscale)
            # mqueue.put((x,y),avg_color)
            img_arr.append([(int(x/scale),int(y/scale)),avg_color])
            print("{}%".format(round(float(len(img_arr)/total)*100,2)), end = "\r")
    print
    print("done")
    with open('record','w') as record:
        record.write(json.dumps(img_arr))
    return img2,img_arr

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
    return ( int(total[0]/ m_sum),int(total[1]/ m_sum),int(total[2]/ m_sum))


def resize_imgae(img, size):
    img = img.resize((size,size))
    return img


def list_all_img(mdir):
    return [mdir+f for f in os.listdir(mdir) if '.jpg' in f]


def pretty_paste(result_img,mat_imgfile,size,index,length):
    s_img = Image.open('{}'.format(mat_imgfile),'r')
    # s_img = resize_imgae(s_img,size)
    s_img.thumbnail((size, size), Image.ANTIALIAS)
    print(s_img.size)
    w, h = s_img.size
    x = index * size % (size * length)
    y = (index // length) * size
    if w > h:
        result_img.paste(s_img,(x, y + int((w-h)/2), x+w , y+h + int((w-h)/2)))
    else:
        result_img.paste(s_img,(x + int((h-w)/2), y , x+w+ int((h-w)/2) , y+h))
    return result_img 


def is_color_alike(clr1,clr2):
    arg = 20
    r1,g1,b1 = clr1
    r2,g2,b2 = clr2
    # print(abs(r1-r2),abs(g1-g2),abs(b1-b2),end='\r')
    # print(abs(g1-g2) < arg)
    return (abs(r1-r2) < arg and abs(g1-g2) < arg and abs(b1-b2) <  arg)

def get_color(imgdir):
    k=imgdir.split('/')[-1].split('-')[0].split(',')
    return tuple([int(i) for i in k])





def img_process(nscale):
    while True:
        if pro_que.empty():
            pass
        else:
            try:
                imgurl = pro_que.get()
                img = requests.get(imgurl)
                img = Image.open(io.BytesIO(img.content))
                img = resize_imgae(img, nscale)
                # speed up calculation
                imgtemp = resize_imgae(img, 50)
                avg_color = calc_color_avg(imgtemp)
                lqueue.put((img, avg_color))
                # print("pro_queue size: {}, lqueue size: {}".format(pro_que.qsize(),lqueue.qsize()))
            except:
                pass
        


def crawl(page, threads):
    print("Page:",page)
    driver.get(url+ str(page))
    last_height = driver.execute_script("return window.scrollY")
    # print("load page")
    while True:
        # Scroll down
        driver.execute_script("window.scrollBy(0, screen.height);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return window.scrollY")
        # print(last_height,new_height)
        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source
    soup = BeautifulSoup(html, 'html5lib')
    imglistdiv = soup.findAll("div", {"class": "item"})
    for img in imglistdiv:
        imgurl = img.find('img')['src']
        pro_que.put(imgurl)
    
    
def crawl2():
    driver.get(url)
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
                pass
        last_height = new_height
        imglistdiv = driver.find_elements_by_class_name("photo-item__img")
        
        for imgdiv in imglistdiv:
            imgurl = imgdiv.get_attribute('src')
            pro_que.put(imgurl)
        driver.execute_script("var mlist = document.getElementsByClassName('photo-item__img'); for(var i=0;i<mlist.length;i+=1){mlist[i].className='done';}")
    # imglistdiv = driver.find_elements_by_class_name("photo-item__img")

def thread_crawl(nscale):
    global page
    worker = 20
    threads = []
    for i in range(worker):
        t2 = threading.Thread(target=img_process, args=(nscale,))
        t2.daemon = True
        threads.append(t2)
    print("thread start")
    for t in threads:
        t.start()
    while True:
        if lqueue.qsize() > 1000 or pro_que.qsize() > 200:
            print("crawl rest...")
            time.sleep(5)
        page += 1
        if page > 3300:
            page = 1
        crawl(page,threads)

        # while pro_que.qsize() > 30:
        #     time.sleep(10)


def init_env():
    os.system('mkdir pic/')
    os.system('mkdir pic/stage/')


def main(mp: Merge_Pic):
    # open driver
    

    ## initial env
    init_env()

    ## initial result img
    result_img, mother_pic_struct = mp.mother_pic_init()
    ## init result img   
    
  
    ## start threading crawling

    t = threading.Thread(target = thread_crawl, args=(mp.nscale,) )
    t.daemon = True
    t.start()


    ## start merging
    result_stage = 1

    while len(mother_pic_struct) > 0:
        print("lqueue: {}".format(str(lqueue.qsize())))
        if lqueue.qsize() == 0:
            print("wait crawl..")
            time.sleep(5)
        else:
            limg_struct = lqueue.get()
            limg, l_color = limg_struct
            for m_piece in mother_pic_struct:
                m_point, m_color = m_piece
                
                if is_color_alike(m_color, l_color):
                    result_img.paste(limg,(m_point[0]* mp.nscale, m_point[1] * mp.nscale, m_point[0]* mp.nscale + mp.nscale, m_point[1]* mp.nscale + mp.nscale))
                    mother_pic_struct.remove(m_piece)
                    print("{} left".format(len(mother_pic_struct)))
                    
                    
                    if len(mother_pic_struct) % 100 == 0:
                        result_img.save("pic/stage/{}_{}.jpg".format(mp.pic_name,str(result_stage)))
                        with open('record','w') as record:
                            record.write(json.dumps(mother_pic_struct))
                        result_stage += 1

                    break
    
    print("Done")
    result_img.save("pic/result.jpg")
    
    


def print_help():
    print("""Input args

option 1. A fresh start

    -I <original image>


option 2. continue from half work

    -o <half work image>  
    -r <record file>
    """)


if __name__ == '__main__':
    starttime = time.time()
    origin_path = None
    halfwork_path = None
    record_path = None
    argv = sys.argv[1:]
    try:
      opts, args = getopt.getopt(argv,"hI:o:r:")
    except getopt.GetoptError as e:
        print('')
        sys.exit(2)
    
    for opt, arg in opts:
        print(opt,arg)
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-I"):
            print("Input Origin Image:", arg)
            origin_path = arg
        elif opt in ("-o"):
            halfwork_path = arg
        elif opt in ("-r"):
            record_path = arg
        else:
            print_help()
            sys.exit()
    if origin_path is None and halfwork_path is not None and record_path is not None:
        mp = Merge_Pic(origin_path=None, halfwork_path=halfwork_path, record_path = record_path)
        main(mp)
    elif origin_path is not None:
        mp = Merge_Pic(origin_path = origin_path)
        main(mp)
    else:
        print_help()
    endtime = time.time()
    # print(starttime,endtime)
    driver.close()
    print("finish:",endtime-starttime)
