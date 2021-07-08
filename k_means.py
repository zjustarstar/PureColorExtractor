from PIL import Image
from random import sample
import math
import numpy as np
import itertools

#Lab
BLACK = (10, 128, 128)
WHITE = (255, 255, 255)

THRESH_SIZE = 500

def distance(p1, p2):
    p1, p2 = np.array(p1), np.array(p2)
    return np.sum((p1 - p2) ** 2)**0.5

def toBins(pixel_cnt, bins_num=16):
    bin_range = 256//bins_num
    tmp = {}
    for x in itertools.product(range(bins_num), repeat=3):
        tmp[x] = {'v':np.array([0,0,0]), 'n':0}
    for pixel, cnt in pixel_cnt.items():
        i = tuple([c//bin_range for c in pixel])
        tmp[i]['v'] += np.array(pixel)*cnt
        tmp[i]['n'] += cnt
    bins = {}
    for bin_item in tmp.values():
        if bin_item['n'] != 0:
            bins[tuple(bin_item['v']/bin_item['n'])] = bin_item['n']
    return bins


def init_means(bins, k):
    def factor(color,last_mean):
        return 1 - math.exp(((distance(color, last_mean) / 80) ** 2) * -1)
    means = []
    for _ in range(k):
        for color in bins.keys():
            if color not in means:
                means.append(color)
                break
        bins = {k:v*factor(k, means[-1]) for k, v in sorted(bins.items(), key=lambda item:item[1], reverse=True)}
        bins =  {k: v for k, v in sorted(bins.items(), key=lambda item: item[1], reverse=True)}
    return means


def k_means(sourceImg, k, init_mean=True, black=False, white=False):
    img = Image.open(sourceImg)
    if img.mode != "RGB":
        img = img.convert("RGB")
    # print(sourceImg, img.format, img.size, img.mode)
    maxlen = max(img.size)
    if maxlen > THRESH_SIZE:
        if img.width == maxlen:
            img = img.resize((THRESH_SIZE, int(img.height*500/maxlen)))
        else:
            img = img.resize((int(img.width*500/maxlen), THRESH_SIZE))
    colors = img.getcolors(img.width * img.height)
    pixel_cnt = {}
    for count, pixel in colors:
        pixel_cnt[pixel] = count
    '''if len(pixel_cnt) > 10*k and 10*k <= 128:
        bins = toBins(pixel_cnt, bins_num = k*10)
    if len(pixel_cnt) > 5*k and 5*k <= 128:
        bins = toBins(pixel_cnt, bins_num = k*5)
    if len(pixel_cnt) > 3*k and 3*k <= 128:
        bins = toBins(pixel_cnt, bins_num = k*3)
    elif len(pixel_cnt) > 2*k and 2*k <= 128:
        bins = toBins(pixel_cnt, bins_num = k*2)
    else:
        bins = pixel_cnt'''
    bins = toBins(pixel_cnt)
    # print("length of bins:", len(bins))
    bins = {k: v for k, v in sorted(bins.items(), key=lambda item: item[1], reverse=True)}
    if len(bins) <= k:
        bins = list(bins.keys())
        x = [bins[-1]]*(k-len(bins))
        bins.extend(x)
        return bins
    colors = list(bins.keys()) 
    if init_mean:
        means = init_means(bins, k)
    else:
        means = sample(colors, k)
    if black: means.append(BLACK)
    if white: means.append(WHITE)
    means = np.array(means)
    mean_cnt = means.shape[0]
    max_iter = 1000   
    cluster_cnt = 0
    for i in range(max_iter):
        cluster_cnt = np.zeros(mean_cnt)
        cluster_sum = [np.array([0,0,0],dtype=float) for i in range(mean_cnt)]
        for color, cnt in bins.items():
            dists = [distance(color,mean) for mean in means]
            cluster_i = dists.index(min(dists))
            cluster_sum[cluster_i] += np.array(color) * cnt
            cluster_cnt[cluster_i] += cnt
        new_means = [cluster_sum[i] / cluster_cnt[i] if cluster_cnt[i] > 0 else [0,0,0] for i in range(k)]
        if black: new_means.append(BLACK)
        if white: new_means.append(WHITE)
        new_means = np.array(new_means)
        if (new_means == means).all():
            print("已收敛") 
            break
        else:
            means = new_means

    colors = new_means.tolist()[:k]
    for i, color in enumerate(colors):
        colors[i] = (round(color[0]), round(color[1]), round(color[2]))

    return colors
