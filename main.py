from PIL import Image,ImageDraw
from PIL import ImageFilter
import time
import os
import math

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
    ori_width = img.size[0]
    ori_height = img.size[1]
    img_arr=[]
    img2 = img.copy()
    for y in range(0, ori_height, scale):
        for x in range(0, ori_width, scale):
            img2, avg_color = draw_avg_color(img2,x,y,scale)
            img_arr.append([(x,y),avg_color])
    
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


def main():
    mask_scale = 25
    
    ## get mother pic 
    mother_pic = Image.open('./pic/total/P_20160116_193613_BF.jpg')
    w, h = mother_pic.size
    if w > h:
        mother_pic=resize_imgae(mother_pic, w)
        length = w
    else:
        mother_pic=resize_imgae(mother_pic, h)
        length = h
    
    ## analize the color 要拿到打馬後的整張顏色結構 list 存
    mother_pic, mother_pic_struct = draw_mask(mother_pic, mask_scale)
    print(len(mother_pic_struct))
    mother_pic.show('test')
    # print(mother_pic_struct)
    ## initial result img
    result_img = Image.new('RGB',(length,length))

    
    

    
    
    ## for each matiral calc the avg color
        ## and mapping to the mother pic
    mlist = list_all_img('../pic_crawler/pic/')
    print("0% complete",end = "\r")
    for i,m_mask in enumerate(mother_pic_struct):
        point, color = m_mask
        is_match = False
        for imgdir in mlist:
            limg = Image.open(imgdir,'r')
            limg = resize_imgae(limg, mask_scale)
            try:
                avg_color = calc_color_avg(limg)
            except:
                print("ERROR",imgdir)
                continue
            if is_color_alike(avg_color, color):
                result_img.paste(limg,(point[0], point[1], point[0] + mask_scale, point[1]+mask_scale))
                # mlist.remove(imgdir)
                print("{}% complete".format(float(i/len(mother_pic_struct))), end="\r")
                is_match = True
                # result_img.show('test')
                break
        if is_match == False:
            result_img.show('title')
            raise('Not match')
        
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
    mask_scale = 25
    # print(is_color_alike((20,50,60),(15,48,61)))
    imgdir = '../pic_crawler/pic/moon-3232487__340.jpg'
    limg = Image.open(imgdir,'r')
    limg = resize_imgae(limg, mask_scale)
    avg_color = calc_color_avg(limg)
    

if __name__ == '__main__':
    starttime = time.time()
    main()
    # test()
    endtime = time.time()
    print(starttime,endtime)
    print(endtime-starttime)




