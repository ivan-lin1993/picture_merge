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
    return img

def draw_mask(img, scale):
    ori_width = img.size[0]
    ori_height = img.size[1]
    img2 = img.copy()
    for y in range(0, ori_height, scale):
        for x in range(0, ori_width, scale):
            img2 = draw_avg_color(img2,x,y,scale)
    
    return img2

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
    return (total[0]/ m_sum,total[1]/ m_sum,total[2]/ m_sum)


def resize_imgae(img, size):
    img = img.resize((size,size))
    return img


def list_all_img():

    return ['pic/total/'+f for f in os.listdir('pic/total/') if '.jpg' in f]



def main():
    all_images = list_all_img()
    length = int(math.pow(len(all_images), 0.5))
    print(length)
    
    size = 100
    print(length * size)
    img = Image.new('RGB',(length*size,length*size))
    for index,imgfile in enumerate(all_images):
        s_img = Image.open('{}'.format(imgfile),'r')
        # s_img = resize_imgae(s_img,size)
        s_img.thumbnail((size, size), Image.ANTIALIAS)
        print(s_img.size)
        w, h = s_img.size
        x = index * size % (size * length)
        y = (index // length) * size
        if w > h:
            img.paste(s_img,(x, y + int((w-h)/2), x+w , y+h + int((w-h)/2)))
        else:
            img.paste(s_img,(x + int((h-w)/2), y , x+w+ int((h-w)/2) , y+h))            
        print(x,y)
        
    # img = Image.open("pic/1.jpg",'r')
    # img2 = resize_imgae(img,30)
    # img2.save("pic/resize.jpg")
    # img = draw_mask(img, 25)
    img.save("pic/paste.jpg")
    
    
def test():
    print(list_all_img())
    pass

if __name__ == '__main__':
    starttime = time.time()
    main()
    # test()
    endtime = time.time()
    print(starttime,endtime)
    print(endtime-starttime)




