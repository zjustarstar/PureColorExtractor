from PIL import Image
from searchSegment import preprocess, searchSeg
from getSegColor import getSegColor
from imgConverter import alpha_composite_with_color
#from kmeans2 import k_means
from k_means import k_means
import time
import numpy as np

# 线框图中允许的最小区域
MIN_AREA = 49
# 是否保存不合格的图
ENABLE_SAVE_UNQUALIFIED = False

def distance(p1, p2):
    p1, p2 = np.array(p1), np.array(p2)
    return np.sum((p1 - p2) ** 2)**0.5

def flatImg(sketchFile, colorFile, k=10, white=True):
    start_time = time.time()
    im = Image.open(sketchFile)
    print(im.size)
    im = alpha_composite_with_color(im)
    gray = im.convert("L")
    mask, mat = preprocess(gray, 254)
    num, eqValues, _ = searchSeg(mat)
    img = gray.convert("RGB")
    rgb_area, result = getSegColor(colorFile, eqValues, mat, num, img)
    #colors = k_means(rgb_area, 10, white=True)
    colors = k_means(colorFile, k, white=white)
    print(colors)
    old_newrgb = {}
    for w in range(img.width):
        for h in range(img.height):
            if mat[h][w]>255:
                old_rgb = result.getpixel((w,h))
                if old_rgb in old_newrgb.keys():
                    result.putpixel((w, h), old_newrgb[old_rgb])
                else:
                    minDis, new_rgb = 1e3, colors[0]
                    for rgb in colors:
                        dis = distance(old_rgb, rgb)
                        if dis < minDis:
                            minDis = dis
                            new_rgb = rgb
                    old_newrgb[old_rgb] = new_rgb
                    result.putpixel((w, h), new_rgb)
    result.show()
    result.save("flatted.png")
    end_time = time.time()
    time1 = round(end_time - start_time)
    print("take", time1, "s")

if __name__ == "__main__":
    flatImg("1-1.png", "1.png", k=10, white=True)