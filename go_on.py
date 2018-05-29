import json
import main
from PIL import Image,ImageDraw
import time
import threading


half_img = Image.open('pic/stage/result_52.jpg','r')
mask_scale = 30
w,h = half_img.size
print(w,h)

# 51*50 + 100 = mask * len + mask_scale(30)
savefile = open('record','r').read()
rest_struct = json.loads(savefile)
result_stage = 53
rest_list = []
for rest_piece in rest_struct:
    rest_list.append(
        [tuple(rest_piece[0]),tuple(rest_piece[1])]
    )

t = threading.Thread(target = main.thread_crawl )
t.daemon = True
t.start()


while len(rest_list) > 0:
    if main.lqueue.qsize() == 0:
        print("wait crawl..")
        time.sleep(5)
    else:
        print(main.lqueue.qsize())
        limg_struct = main.lqueue.get()
        limg, l_color = limg_struct
        for m_piece in rest_list:
            m_point, m_color = m_piece
            
            if main.is_color_alike(m_color, l_color):
                half_img.paste(limg,(m_point[0], m_point[1], m_point[0] + mask_scale, m_point[1]+mask_scale))
                rest_list.remove(m_piece)
                k = open('left','w')
                k.write("{} left".format(len(rest_list)))
                print("{} left".format(len(rest_list)))
                
                
                if len(rest_list) % 50 == 0:
                    half_img.save("pic/stage/result_{}.jpg".format(str(result_stage)))
                    with open('record','w') as record:
                        record.write(json.dumps(rest_list))
                    result_stage += 1

                break