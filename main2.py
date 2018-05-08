import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

img = mpimg.imread('1.jpg')     
print(type(img))
# gray = rgb2gray(img)    
# print(img)
# plt.imshow(gray, cmap = plt.get_cmap('gray'))
# plt.show()



print(3 << 3) # shift to left by 5 bits
print(64 >> 5) # shift to right by 5 bits
# print(obj >> "Hello world") # redirect the output to obj, 