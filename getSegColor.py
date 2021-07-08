import os
from PIL import Image, ImageDraw

def getSegColor(colorImg, eqValues, mat, num, img, params):
    # 一些参数
    AREA_THRESH = params["area_thresh"]
    ENABLE_SAVE_UNQUALIFIED = params["save_colored_regions"]
    flag_showimg = params["show_process_img"]
    color_filename = params["color_filename"]

    colorImg = Image.open(colorImg)
    colorImg = colorImg.convert("RGB")

    num_color = []
    for i in range(num):
        num_color.append({})
    for w in range(colorImg.width):
        for h in range(colorImg.height):
            if mat[h][w] > 255:
                num = mat[h][w] - 256
                rgb = colorImg.getpixel((w, h))
                if rgb in num_color[num].keys():
                    num_color[num][rgb] += 1
                else:
                    num_color[num][rgb] = 1
    #print(num_color)

    num_root = {}
    for eqs in eqValues:
        eqs.sort()
        for i in range(1, len(eqs)):
            num_color[eqs[0]].update(num_color[eqs[i]])
            num_color[eqs[i]] = {}
            num_root[eqs[i]] = eqs[0]
    #print(num_root)
    #print(num_color)
    num_rgb = {}
    R, G, B = 0, 1, 2

    if ENABLE_SAVE_UNQUALIFIED:
        unqualified_nums = []
        for i, color in enumerate(num_color):
            if color == {}:
                continue
            area = sum(list(color.values()))
            if area <= AREA_THRESH:
                unqualified_nums.append(i)
                print("有小于等于", AREA_THRESH, "像素数的区域:", area)

    #rgb_area = {}
    for i, colors in enumerate(num_color):
        #print(i, colors)
        if colors == {}:
            num_rgb[i] = num_rgb[num_root[i]]
        else:
            colors = {k:v for k, v in sorted(colors.items(), key=lambda item:item[1], reverse=True)}
            #rgbs = list(colors.keys())
            area = sum(list(colors.values()))
            rgb = [0, 0, 0]
            for k, v in colors.items():
                rgb[R] += k[R]*(float(v)/area)
                rgb[G] += k[G]*(float(v)/area)
                rgb[B] += k[B]*(float(v)/area)
            rgb = (round(rgb[R]), round(rgb[G]), round(rgb[B]))
            num_rgb[i] = rgb

    #print(num_rgb)
    result = Image.new('RGB', colorImg.size)
    result_pixels = result.load()
    unqualified_pixels = []
    for w in range(colorImg.width):
        for h in range(colorImg.height):
            r, g, b = mat[h][w], mat[h][w], mat[h][w]
            if mat[h][w]>255:
                num = mat[h][w] - 256
                if ENABLE_SAVE_UNQUALIFIED and num in unqualified_nums:
                    unqualified_pixels.append((w,h))
                r, g, b = num_rgb[num]
            result_pixels[w,h] = (r, g, b)
    if flag_showimg:
        result.show("image after clustering")
        # result.save("test.png")
    if ENABLE_SAVE_UNQUALIFIED:
        draw = ImageDraw.Draw(img)
        draw.point(unqualified_pixels, fill = (255,0,0))
        # 保存小区域信息
        (filepath, filename) = os.path.split(color_filename)
        (shotname, extension) = os.path.splitext(filename)
        newfilename = filepath + "//" + shotname + "_small_reg.png"
        img.save(newfilename)
        if flag_showimg:
            img.show("small regions labeling")

    return result
