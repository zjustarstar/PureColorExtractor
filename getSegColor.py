from PIL import Image, ImageDraw

AREA_THRESH = 50

def getSegColor(colorImg, eqValues, mat, num, img):
    colorImg = Image.open(colorImg)
    colorImg = colorImg.convert("RGB")
    print(colorImg.size)
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
    unqualified_nums = []
    for i, color in enumerate(num_color):
        if color == {}:
            continue
        area = sum(list(color.values()))
        if area <= AREA_THRESH:
            unqualified_nums.append(i)
            print("有小于等于", AREA_THRESH, "像素数的区域:", area)
    rgb_area = {}
    for i, colors in enumerate(num_color):
        #print(i, colors)
        if colors == {}:
            num_rgb[i] = num_rgb[num_root[i]]
        else:
            colors = {k:v for k, v in sorted(colors.items(), key=lambda item:item[1], reverse=True)}
            rgbs = list(colors.keys())
            if len(rgbs) == 1:               
                rgb = list(colors.keys())[0]
                area = list(colors.values())[0]
            elif len(rgbs) <= 40:
                area = sum(list(colors.values()))
                rgb = [0, 0, 0]
                for k, v in colors.items():
                    rgb[R] += k[R]*(float(v)/area)
                    rgb[G] += k[G]*(float(v)/area)
                    rgb[B] += k[B]*(float(v)/area)
                rgb = (round(rgb[R]), round(rgb[G]), round(rgb[B]))
            else:
                cnt = sum(list(colors.values())[:40])
                area = sum(list(colors.values()))
                rgb = [0, 0, 0]
                for j, (k, v) in enumerate(colors.items()):
                    if j == 40:
                        break
                    rgb[R] += k[R]*(float(v)/cnt)
                    rgb[G] += k[G]*(float(v)/cnt)
                    rgb[B] += k[B]*(float(v)/cnt)
                rgb = (round(rgb[R]), round(rgb[G]), round(rgb[B]))
            num_rgb[i] = rgb
            if rgb not in rgb_area.keys():
                rgb_area[rgb] = area
            else:
                rgb_area[rgb] += area
    #print(num_rgb)
    result = Image.new('RGB', colorImg.size)
    result_pixels = result.load()
    unqualified_pixels = []
    '''unqualified_pixels = {}
    for num in unqualified_nums:
        #unqualified_pixels[num] = [[], []]
        unqualified_pixels[num] = []'''
    for w in range(colorImg.width):
        for h in range(colorImg.height):
            r, g, b = mat[h][w], mat[h][w], mat[h][w]
            if mat[h][w]>255:
                num = mat[h][w] - 256
                if num in unqualified_nums:
                    #unqualified_pixels[num][0].append(h)
                    #unqualified_pixels[num][1].append(w)
                    unqualified_pixels.append((w,h))
                r, g, b = num_rgb[num]
            result_pixels[w,h] = (r, g, b)
    result.show()
    result.save("test.png") 
    draw = ImageDraw.Draw(img)
    draw.point(unqualified_pixels, fill = (255,0,0))
    img.show()
    img.save("unqualified.png")
    return rgb_area, result
    '''for num, pixels in unqualified_pixels.items():
        pixels[0].sort()
        pixels[1].sort()
        center = (max(pixels[0])-min(pixels[0])/2, (max(pixels[1])-min(pixels[1]))/2)
        height, width = max(pixels[0])-min(pixels[0]), max(pixels[1])-min(pixels[1])
        upLeft = [center[0] - height, center[1] - width]
        if upLeft[0] < 0:
            upLeft[0] = 0
        if upLeft[1] < 0:
            upLeft[1] = 0
        draw.rectangle((upLeft[1], upLeft[0], width, height), outline=(255,255,255))
    result.show()
    result.save("unqualified.png")'''
