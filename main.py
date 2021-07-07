from PIL import Image
from searchSegment import preprocess, searchSeg
from getSegColor import getSegColor
from imgConverter import alpha_composite_with_color
from k_means import k_means
import time
import numpy as np
import os

# 线框图中允许的最小区域
AREA_THRESH = 50
# 是否保存不合格的图
ENABLE_SAVE_UNQUALIFIED = False


def distance(p1, p2):
    p1, p2 = np.array(p1), np.array(p2)
    return np.sum((p1 - p2) ** 2)**0.5


def flatImg(sketchFile, colorFile, k=10, nowhite=True):
    '''
    :param sketchFile: 输入的线框图
    :param colorFile: 输入的彩绘图
    :param k: 最终输出的纯色图的颜色数量
    :param nowhite: 是否不允许存在白色区域,如果True表示不允许存在白色区域
    :return:
    '''
    start_time = time.time()
    print("开始处理图像:{}".format(colorFile))

    im = Image.open(sketchFile)
    im = alpha_composite_with_color(im)
    gray = im.convert("L")
    mask, mat = preprocess(gray, 254)
    num, eqValues, _ = searchSeg(mat)
    img = gray.convert("RGB")
    result_img = getSegColor(colorFile, eqValues, mat, num, img, AREA_THRESH=AREA_THRESH, ENABLE_SAVE_UNQUALIFIED=ENABLE_SAVE_UNQUALIFIED)
    #colors = k_means(rgb_area, 10, white=True)
    colors = k_means(colorFile, k, white=nowhite)
    print(colors)

    # 生成纯色图
    old_newrgb = {}
    for w in range(img.width):
        for h in range(img.height):
            if mat[h][w]>255:
                old_rgb = result_img.getpixel((w,h))
                if old_rgb in old_newrgb.keys():
                    result_img.putpixel((w, h), old_newrgb[old_rgb])
                else:
                    minDis, new_rgb = 1e3, colors[0]
                    for rgb in colors:
                        dis = distance(old_rgb, rgb)
                        if dis < minDis:
                            minDis = dis
                            new_rgb = rgb
                    old_newrgb[old_rgb] = new_rgb
                    result_img.putpixel((w, h), new_rgb)

    # 保存结果图.文件名为同名文件，并加_flat后缀
    (filepath, filename) = os.path.split(colorFile)
    (shotname, extension) = os.path.splitext(filename)
    newfilename = filepath + "//" + shotname + "_flatted.png"
    result_img.show()
    result_img.save(newfilename)
    end_time = time.time()
    time1 = round(end_time - start_time)
    print("take", time1, "s")


if __name__ == "__main__":
    imgpath = os.getcwd() + "//testimg//"
    flatImg(imgpath+"3-3.png", imgpath+"3.jpeg", k=30, nowhite=True)