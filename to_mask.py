from PIL import Image, ImageDraw, ImageFont
import sys
import time

starttime = time.time()


image_name = sys.argv[1]
image_file = Image.open(image_name)
# image_file = image_file.resize((width, height))  # 调整图片大小
width = image_file.size[0]
height = image_file.size[1]


granularity = int(sys.argv[2])  # 颗粒度
image = Image.new('RGB', (width, height), (255, 255, 255))
# 创建Draw对象:
draw = ImageDraw.Draw(image)

# image_name = raw_input('Entering Input ImageName:  ')



def to_mosaic(file_name):
    for x in range(0, width, granularity):
        for y in range(0, height, granularity):
            r, g, b = file_name.getpixel((x, y))
            draw.rectangle([(x, y), (x + granularity, y + granularity)], fill=(r, g, b), outline=None)  # None即是不加网格


to_mosaic(image_file)
image.save('pic/Mosaic.jpg', 'jpeg')




endtime = time.time()
print(starttime,endtime)
print(endtime-starttime)