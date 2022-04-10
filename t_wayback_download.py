# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import re
import os
import urllib.request
import threading
import sys
import time


# 下载成功图片列表，每个线程下载后汇报到这个列表里
successDownloadImgList = []
# 下载失败图片列表，每个线程下载后汇报到这个列表里
failDownloadImgList = []
# 全部线程是否执行完成
isDone = False



class ImgMetaInfo:
    def __init__(self, imgUrl, imgName):
        self.imgUrl = imgUrl
        self.imgName = imgName

    def print(self):
        print(self.imgUrl + " " + self.imgName)


# 输入html文件地址，返回图片地址和下载后的图片文件名,包含多个文件时返回列表
def getImgUrl(htmlUrl):
    imgMetaInfoList = []
    # print("正在解析 " + htmlUrl + " 图片地址...")
    htmlFile = open(htmlUrl, "r")
    pattern = re.compile("(?<=data-image-url=\")(\S*)(?=\")")
    imgUrlMatches = pattern.findall(htmlFile.read())
    if imgUrlMatches is None:
        # print("图片地址为空")
        return
    else:
        imgSaveName = re.search("(?<=/)(\d*)(?=\.html)", htmlUrl).group()
        i = 0
        for imgUrl in imgUrlMatches:
            # print("图片地址为 " + imgUrl + " , 下载后图片文件名为 " + imgSaveName)
            if i == 0:
                imgMetaInfoList.append(ImgMetaInfo(imgUrl, imgSaveName + ".jpg"))
            else:
                imgMetaInfoList.append(ImgMetaInfo(imgUrl, imgSaveName + "_" + str(i) + ".jpg"))
            i = i + 1
        return imgMetaInfoList


# 单元测试getImgUrl
def getImgUrlTest():
    htmlUrl = "/Users/belber/Downloads/twayback/ilovegranville/1497272591815376898.html"
    imgMetaInfoList = getImgUrl(htmlUrl)
    for imgMetaInfo in imgMetaInfoList:
        imgMetaInfo.print()


# 输入html目录，返回所有html文件中的图片地址和下载后的图片文件名
def getImgMetaInfoList(htmlDir):
    file_list = os.listdir(htmlDir)
    imgMetaInfoList = []
    for FILE in file_list:
        if not FILE.endswith("html"):
            # print(FILE + "不是html文件略过")
            continue
        else:
            imgMetaInfos = getImgUrl(htmlDir + "/" + FILE)
            if imgMetaInfos is not None:
                for imgMetaInfo in imgMetaInfos:
                    imgMetaInfoList.append(imgMetaInfo)
    return imgMetaInfoList


# 单元测试getImgMetaList
def getImgMetaListTest():
    imgMetaInfoList = getImgMetaInfoList("/Users/belber/Downloads/twayback/Ilovesamuel_")
    for imgMetaInfo in imgMetaInfoList:
        imgMetaInfo.print()


# 输入图片地址和下载后的文件名，下载图片到指定文件名，下载失败时返回失败的图片地址
def downloadOneImg(imgUrl, saveImgFilePath):
    failImgUrl = None
    try:
        imgUrlResponse = urllib.request.urlopen(imgUrl)
        imgFile = open(saveImgFilePath, "wb")
        imgFile.write(imgUrlResponse.read())
        imgFile.close()
    except:
        print("下载图片失败:" + imgUrl)
        failImgUrl = imgUrl
    return failImgUrl


# 输入图片地址和图片保存文件名列表，下载所有图片到指定目录
def downloadAllImgs(imgMetaInfoList, saveDirPath, threadName, threadLock):
    global successDownloadImgList
    global failDownloadImgList
    i = 1
    for imgMetaInfo in imgMetaInfoList:
        print(threadName + "正在下载第" + str(i) + "张图片")
        failImgUrl = downloadOneImg(imgMetaInfo.imgUrl, saveDirPath + "/" + imgMetaInfo.imgName)
        # 线程下载每张图片成功后要汇报
        threadLock.acquire()
        if failImgUrl is None:
            successDownloadImgList.append(imgMetaInfo.imgUrl)
        else:
            failDownloadImgList.append(failImgUrl)
        threadLock.release()
        i = i + 1
    return


# 定时统计已经下载了多少图片
def countAlreadyDownloadNums(imgTotalNums, threadLock):
    global successDownloadImgList
    global failDownloadImgList
    global isDone
    while not isDone:
        time.sleep(10)
        threadLock.acquire()
        print("**********总共" + str(imgTotalNums) + ",成功" + str(len(successDownloadImgList)) +
              ",失败" + str(len(failDownloadImgList)) + "**********")
        threadLock.release()


# 输入图片地址和图片保存文件名列表，【多线程】下载所有图片到指定目录
def downloadAllImgsMultiProcess(imgUrlNameDictList, saveDirPath):
    # 一个线程承担多少张图片下载
    unitNum = 5
    # 总共多少张图片
    imgTotalNums = len(imgUrlNameDictList)
    # 一个线程最多承担unitNum张图片下载，计算需要创建多少线程
    processNums = 0
    if imgTotalNums < unitNum:
        processNums = 1
    else:
        processNums = int(imgTotalNums / unitNum)
        if processNums * unitNum < imgTotalNums:
            processNums = processNums + 1
    print("将创建" + str(processNums) + "个线程，每个线程至多下载" + str(unitNum) + "张图片")
    threadLock = threading.Lock()
    try:
        i = 0
        threads = []
        while i < processNums:
            # 将大列表按照unitNum张图片一组分成小列表，交给线程去下载
            partList = []
            beginIndex = i * unitNum
            endIndex = (i + 1) * unitNum
            if endIndex > imgTotalNums:
                endIndex = imgTotalNums
            while beginIndex < endIndex:
                partList.append(imgUrlNameDictList[beginIndex])
                beginIndex = beginIndex + 1
            # 创建线程启动下载
            thread = threading.Thread(target=downloadAllImgs, args=(partList, saveDirPath,"Thread-"+str(i+1),threadLock))
            threads.append(thread)
            i = i + 1
            thread.start()
    except Exception as err:
        print("创建线程失败", err)
        global isDone
    # 启动统计已下载图片数量线程
    threadCounting = threading.Thread(target=countAlreadyDownloadNums, args=(imgTotalNums, threadLock))
    threadCounting.start()
    # 等待所有线程执行完成
    for t in threads:
        t.join()
        isDone = True
    summaryFile = open(saveDirPath+"/summary.txt", "w")
    global successDownloadImgList
    global failDownloadImgList
    summaryFile.write(str(len(successDownloadImgList)) + "张下载成功" + "\n")
    for imgUrl in successDownloadImgList:
        summaryFile.write(imgUrl + "\n")
    summaryFile.write(str(len(failDownloadImgList)) + "张下载失败" + "\n")
    for imgUrl in failDownloadImgList:
        summaryFile.write(imgUrl + "\n")
    summaryFile.close()


# 单元测试downloadAllImgsMultiProcess
def downloadAllImgsMultiProcessTest():
    imgMetaInfo1 = ImgMetaInfo(
        "https://web.archive.org/web/20220121122924im_/https://pbs.twimg.com/media/FJmnqnFVIAMoYOr.jpg",
        "1484401914041102339.jpg")
    imgMetaInfo2 = ImgMetaInfo(
        "https://web.archive.org/web/20220323125655im_/https://pbs.twimg.com/media/FOdVtM-XoAco9bl.jpg",
        "1506615851012661254.jpg")
    imgUrlNameDictList = [imgMetaInfo1, imgMetaInfo2]
    downloadAllImgsMultiProcess(imgUrlNameDictList, "./test")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # 单元测试部分
    # getImgUrlTest()
    # getImgMetaListTest()
    # downloadAllImgsMultiProcessTest()

    # 主程序部分
    # 给定目标目录
    dir = "/Users/belber/Downloads/twayback/Ilovesamuel_"
    if len(sys.argv) == 2:
        dir = sys.argv[1]
    saveDir = dir + "/img";
    # 创建图片保存目录img
    if not os.path.exists(saveDir):
        os.mkdir(saveDir)
    # 解析出所有html到图片地址和下载后到文件名字典
    imgMetaInfoList = getImgMetaInfoList(dir)
    print("总共找到 " + str(len(imgMetaInfoList)) + " 张图片")
    # 下载所有图片到保存目录
    downloadAllImgsMultiProcess(imgMetaInfoList, saveDir)
    print("全部图片下载完成")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
