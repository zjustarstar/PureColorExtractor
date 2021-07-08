from PIL import Image
from searchSegment import preprocess, searchSeg
from getSegColor import getSegColor
from imgConverter import alpha_composite_with_color
from k_means import k_means
import time
import numpy as np
import os


def distance(p1, p2):
    p1, p2 = np.array(p1), np.array(p2)
    return np.sum((p1 - p2) ** 2)**0.5


def flatImg(sketchFile, colorFile, params):
    '''
    :param sketchFile: 输入的线框图
    :param colorFile: 输入的彩绘图
    :param params: 各种参数的集合体
    :return: 返回k种颜色
    '''
    k = params["k"]
    flag_nowhite = params["no_white_color"]
    flag_showimg = params["show_process_img"]
    print("开始处理图像:{}".format(colorFile))

    im = Image.open(sketchFile)
    print("图像尺寸:{}".format(im.size))

    im = alpha_composite_with_color(im)
    gray = im.convert("L")
    mask, mat = preprocess(gray, 200)
    num, eqValues, _ = searchSeg(mat)
    img = gray.convert("RGB")
    result_img = getSegColor(colorFile, eqValues, mat, num, img, params)
    colors = k_means(colorFile, k, flag_nowhite)

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
    if flag_showimg:
        result_img.show("final flatted image")
    result_img.save(newfilename)
    print("对应纯色图像保存为:{}".format(newfilename))

    return colors


if __name__ == "__main__":

    imgpath = os.getcwd() + "//testimg//"
    start_time = time.time()

    # 处理过程中可能用到的参数
    params = {}
    # 最终生成k种颜色
    params["k"] = 40
    # 最终生成的纯色图中不包含白色，默认为True
    params["no_white_color"] = True
    # 最小的区域;小于该值的，会被红色标记
    params["area_thresh"] = 10
    # 是否保存标记了红色的小区域图像
    params["save_colored_regions"] = False
    # 是否显示一些过程图像, 一般用于调试时, 默认为False
    params["show_process_img"] = True

    # 目前是单张处理，但是如果线框图和彩绘图的文件名是有规律的，可以做成批量处理
    # 彩绘图像. 生成新的文件时,需要用到彩绘图像名称
    params["color_filename"] = imgpath+"4.jpeg"
    kcolors = flatImg(imgpath+"4-4.png", imgpath+"4.jpeg", params)
    print("{}种颜色:{}".format(params["k"], kcolors))

    end_time = time.time()
    time1 = round(end_time - start_time)
    print("process take", time1, "s")
