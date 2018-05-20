from bs4 import BeautifulSoup
from selenium import webdriver
from PIL import Image,ImageDraw
from PIL import ImageFilter
import time
import os
import io
import math
import queue
import threading
import requests


mask_scale = 50

SCROLL_PAUSE_TIME = 0.2
driver = webdriver.Firefox()
url = "https://pixabay.com/zh/photos/?cat=nature&pagi="
page = 0
mqueue = queue.Queue()
lqueue = queue.Queue()
pro_que = queue.Queue()


def to_gray(mlist):
    total = 0.0
    for i in mlist:
        total += i
    return tuple([int(total/3)] * 3)


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

def draw_mask(img, scale):
    ori_width, ori_height = img.size
    print(ori_width, ori_height)
    total = (ori_height/scale) ** 2
    img_arr=[]
    img2 = img.copy()
    print(total)
    print()
    for y in range(0, ori_height, scale):
        for x in range(0, ori_width, scale):
            img2, avg_color = draw_avg_color(img2,x,y,scale)
            mqueue.put((x,y),avg_color)
            img_arr.append([(x,y),avg_color])
            print("{}%".format(round(float(len(img_arr)/total)*100,2)), end = "\r")
    print
    print("done")
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


def mother_pic_init():
    print("init mother pic")
    ## get mother pic 
    # mother_pic = Image.open('./pic/P_20180401_152147_vHDR_Auto_HP.jpg')
    mother_pic = Image.open('./pic/P_20180401_152147_vHDR_Auto_HP.jpg')
    w, h = mother_pic.size
    if w > h:
        mother_pic=resize_imgae(mother_pic, w)
        length = w
    else:
        mother_pic=resize_imgae(mother_pic, h)
        length = h
    
    ## analize the color 要拿到打馬後的整張顏色結構 list 存
    print("start analize....")
    mother_pic, mother_pic_struct = draw_mask(mother_pic, mask_scale)
    mother_pic.save('ori_blur.jpg')

    return mother_pic_struct, length


def img_process():
    while True:
        if pro_que.empty():
            pass
        else:
            try:
                imgurl = pro_que.get()
                img = requests.get(imgurl)
                img = Image.open(io.BytesIO(img.content))
                img = resize_imgae(img, mask_scale)
                avg_color = calc_color_avg(img)
                lqueue.put((img, avg_color))
                print("pro_queue size: {}, lqueue size: {}".format(pro_que.qsize(),lqueue.qsize()))
            except:
                pass
        


def crawl(page, threads):
    print("Page:",page)
    driver.get(url+ str(page))
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
    for img in imglistdiv:
        imgurl = img.find('img')['src']
        pro_que.put(imgurl)
    
    

    


def thread_crawl():
    global page
    worker = 20
    threads = []
    for i in range(worker):
        t2 = threading.Thread(target=img_process)
        t2.daemon = True
        threads.append(t2)
    print("thread start")
    for t in threads:
        t.start()
    while True:
        if lqueue.qsize() > 1000:
            print("crawl rest...")
            time.sleep(5)
        page += 1
        crawl(page,threads)

        while pro_que.qsize() > 30:
            time.sleep(10)
        
    

def main():
    ## initial result img
    mother_pic_struct, length = mother_pic_init()
    ## init result img   
    result_img = Image.new('RGB',(length,length))
    
  
    ## start threading crawling

    t = threading.Thread(target = thread_crawl )
    t.daemon = True
    t.start()


    ## start merging
    result_stage = 1

    while len(mother_pic_struct) > 0:
        if lqueue.qsize() == 0:
            print("wait crawl..")
            time.sleep(10)
        else:
            limg_struct = lqueue.get()
            limg, l_color = limg_struct
            for m_piece in mother_pic_struct:
                m_point, m_color = m_piece
                
                if is_color_alike(m_color, l_color):
                    result_img.paste(limg,(m_point[0], m_point[1], m_point[0] + mask_scale, m_point[1]+mask_scale))
                    mother_pic_struct.remove(m_piece)
                    print("{} left".format(len(mother_pic_struct)))
                    
                    if len(mother_pic_struct) % 50 == 0:
                        result_img.save("pic/stage/result_{}.jpg".format(str(result_stage)))
                        result_stage += 1

                    break
    print("Done")
    driver.close()


    ## for each matiral calc the avg color
        ## and mapping to the mother pic
    # mlist = list_all_img('./pic/total/')
    # print("0% complete",end = "\r")
    # for i,m_mask in enumerate(mother_pic_struct):
    #     point, color = m_mask
    #     is_match = False
    #     for imgdir in mlist:
    #         # limg = Image.open(imgdir,'r')
    #         # limg = resize_imgae(limg, mask_scale)
    #         try:
    #             # avg_color = calc_color_avg(limg)
    #             avg_color = get_color(imgdir)
    #         except:
    #             print("ERROR",imgdir)
    #             continue
    #         if is_color_alike(avg_color, color):
    #             try:
    #                 limg = Image.open(imgdir,'r')
    #                 result_img.paste(limg,(point[0], point[1], point[0] + mask_scale, point[1]+mask_scale))
    #                 # mlist.remove(imgdir)
    #                 print("{}% complete".format(float(i/len(mother_pic_struct))), end="\r")
    #                 is_match = True
    #                 # result_img.show('test')
    #                 break
    #             except:
    #                 mlist.remove(imgdir)
    #                 pass
    #     if is_match == False:
    #         result_img.show('title')
    #         result_img.save("pic/result.jpg")
    #         raise('Not match')
        
    result_img.save("pic/result.jpg")
    
    
    # all_images = list_all_img('pic/total/')
    # length = int(math.pow(len(all_images), 0.5))
    # print(length)
    
    # size = 100
    # print(length * size)
    # img = Image.new('RGB',(length*size,length*size))
    # for index,imgfile in enumerate(all_images):
    #     s_img = Image.open('{}'.format(imgfile),'r')
    #     # s_img = resize_imgae(s_img,size)
    #     s_img.thumbnail((size, size), Image.ANTIALIAS)
    #     print(s_img.size)
    #     w, h = s_img.size
    #     x = index * size % (size * length)
    #     y = (index // length) * size
    #     if w > h:
    #         img.paste(s_img,(x, y + int((w-h)/2), x+w , y+h + int((w-h)/2)))
    #     else:
    #         img.paste(s_img,(x + int((h-w)/2), y , x+w+ int((h-w)/2) , y+h))            
    #     print(x,y)
        
    # # img = Image.open("pic/1.jpg",'r')
    # # img2 = resize_imgae(img,30)
    # # img2.save("pic/resize.jpg")
    # # img = draw_mask(img, 25)
    # img.save("pic/paste.jpg")
    
    
def test():
    imgdir = './pic/total/63,62,60-9775.jpg'
    get_color(imgdir)
    

if __name__ == '__main__':
    starttime = time.time()
    main()
    # test()
    endtime = time.time()
    print(starttime,endtime)
    print(endtime-starttime)




