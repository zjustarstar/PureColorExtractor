#from time import time

def getareaList(mat, num, eqValues):
    areaList = [0]*num
    height, width = len(mat), len(mat[0])
    for i in range(height):
        for j in range(width):
            v = mat[i][j] - 256
            if v >= 0:
                areaList[v] += 1
    for eqValue in eqValues:
        areaSum = 0
        for v in eqValue:
            areaSum += areaList[v]
            areaList[v] = -1
        areaList[eqValue[0]] = areaSum
    return areaList

def getxyinfo(mat, num, eqValues):
    xysumList = []
    for i in range(num):
        xysumList.append([])
    height, width = len(mat), len(mat[0])
    for i in range(height):
        for j in range(width):
            v = mat[i][j] - 256
            if v >= 0:
                xysumList[v].append((i,j))
    for eqValue in eqValues:
        xys = []
        for v in eqValue:
            for xy in xysumList[v]:
                xys.append(xy)
            xysumList[v] = -1
        xysumList[eqValue[0]] = xys
    return xysumList

def unionSeg(eqList, mat, i1, j1, i2, j2):
    height, width = len(mat), len(mat[0])
    if j2 < width and i2< height and j2 > 0 and i2 > 0 and mat[i2][j2] != mat[i1][j1] and mat[i2][j2] >255 and mat[i1][j1] > 255:
        if mat[i1][j1] > mat[i2][j2] and (mat[i2][j2], mat[i1][j1]) not in eqList:
            eqList.append((mat[i2][j2], mat[i1][j1]))
        elif mat[i1][j1] < mat[i2][j2] and (mat[i1][j1], mat[i2][j2]) not in eqList:
            eqList.append((mat[i1][j1], mat[i2][j2]))

def preprocess(im, v):
    #将图中像素值大于v的视为背景，其余视为前景线图
    mask = im.point(lambda i: i > v and 255)
    mat = []
    width, height = im.size
    for h in range(height):
        m = []
        for w in range(width):
            m.append(mask.getpixel((w,h)))
        mat.append(m)
    return mask, mat


def eqList2eqValues(eqList, num):
    eqValues = list()
    valueMat = []
    for i in range(num):
        valueMat.append([False]*num)
    for tu in eqList:
        valueMat[tu[0]-256][tu[1]-256] = True
        valueMat[tu[1]-256][tu[0]-256] = True
    tulength = len(eqList)
    labelList = [False]*num
    for i in range(tulength):
        e1 = eqList[i][0] - 256
        e2 = eqList[i][1] - 256
        if labelList[e1] and labelList[e2]:
            continue
        temp = []
        if labelList[e1] == False:
            labelList[e1] = True
            temp.append(e1)
        if labelList[e2] == False:
            labelList[e2] = True
            temp.append(e2)
        for k in temp:
            for j in range(num):
                if j == k or labelList[j]:
                    continue
                if valueMat[k][j]:
                    temp.append(j)
                    labelList[j] = True
        eqValues.append(temp)
    return eqValues

def searchSeg(mat):
    '''
        功能：寻找图中颜色分块区域
        返回：分块数，分块中合并为一块的分块标号（从0开始标号）'''
    #starttime = time()
    colornum = 255
    eqList = list()
    height, width = len(mat), len(mat[0])
    for i in range(height):
        for j in range(width):
            if mat[i][j] == 255:
                if i-1>=0 and mat[i-1][j] > 255:
                    mat[i][j] = mat[i-1][j]
                elif j-1>=0 and mat[i][j-1] >255:
                    mat[i][j] = mat[i][j-1]
        for j in range(width-1, -1, -1):
            if mat[i][j] == 255:
                if j+1 < width and mat[i][j+1] > 255:
                    mat[i][j] = mat[i][j+1]
                else:
                    colornum = colornum+1
                    mat[i][j] = colornum
            unionSeg(eqList, mat, i, j, i-1, j)
            unionSeg(eqList, mat, i, j, i, j-1)
            unionSeg(eqList, mat, i, j, i-1, j+1)
            unionSeg(eqList, mat, i, j, i-1, j-1)
    #searchtime = time()
    #print(eqList)
    num = colornum-255
    eqValues = eqList2eqValues(eqList, num)
    '''values = []
    for i, v in enumerate(eqValues):
        t = []
        for j, vi in enumerate(v):
            t.append(vi + 256)
        values.append(t)'''
    return num, eqValues, eqList

def getSegs(mat, num, eqValues):
    xysumList = getxyinfo(mat, num, eqValues)
    segs = []
    height, width = len(mat)+2, len(mat[0])+2
    for xys in xysumList:
        if xys == -1:
            segs.append(-1)
            continue
        seg = []
        for i in range(height):
            seg.append([0]*width)
        for (x,y) in xys:
            seg[x+1][y+1] = 255
        segs.append(seg)
    return segs
