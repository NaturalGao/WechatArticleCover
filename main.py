# coding: utf-8
import requests
from tkinter import *
import tkinter.messagebox as MessageBox
import threading
import os

from urllib.request import urlretrieve
from tkinter import filedialog


# 远程文件下载
def download(url, save_path_dirname, save_path_filename, file_exe):
    global loading
    """
    download file from internet
    :param url: path to download from
    :param savepath: path to save files
    :return: None
    """

    def reporthook(a, b, c):
        """
        显示下载进度
        :param a: 已经下载的数据块
        :param b: 数据块的大小
        :param c: 远程文件大小
        :return: None
        """
        print("\rdownloading: %5.1f%%" % (a * b * 100.0 / c), end="")

    # print(filename)
    # 判断文件是否存在，如果不存在则下载
    if not os.path.isfile(os.path.join(save_path_dirname, save_path_filename)):
        print('Downloading data from %s' % url)
        urlretrieve(url, os.path.join(save_path_dirname, save_path_filename), reporthook=reporthook)
        print('\nDownload finished!')
    else:
        os.remove(save_path_dirname + '/' + save_path_filename)
        urlretrieve(url, os.path.join(save_path_dirname, save_path_filename), reporthook=reporthook)
        print('File already exsits!')
    # 获取文件大小
    filesize = os.path.getsize(os.path.join(save_path_dirname, save_path_filename))
    # 文件大小默认以Bytes计， 转换为Mb
    print('File size = %.2f Mb' % (filesize / 1024 / 1024))
    loading = False
    T1.delete("0.0", "end")
    MessageBox.showinfo("温馨提示", "下载成功！")


# 发起post请求
def sendRequest(url, data):
    r = requests.post(url, headers=commonHeaders, data=data)
    return r.json()


# 选择保存文件路径
def selectSavePath(download_url):
    global loading
    url_arr = download_url.split('=')
    file_exe = url_arr[1].strip()

    filetypes = [(file_exe + "文件图片", "*." + file_exe), ('所有文件', '*.*')]
    filename = filedialog.asksaveasfilename(title='保存文件',
                                            initialfile="time",
                                             filetypes=filetypes,
                                             initialdir='./'  # 打开当前程序工作目录
                                             )

    if len(filename) == 0:
        loading = False
        return False

    filename_arr = str(filename).split('.')
    print(filename_arr)

    if len(filename_arr) == 1:
        filename += '.' + file_exe

    save_path_dirname = os.path.dirname(filename)
    save_path_filename = os.path.basename(filename)

    download(download_url, save_path_dirname, save_path_filename, file_exe)
    return True


# 开始
def startCallBack():
    global loading

    if loading == True:
        MessageBox.showinfo("温馨提示", "已经在运行!")
        return True
    # 改变状态
    loading = True

    url = T1.get("0.0", "end")
    if len(url) == 1:
        MessageBox.showinfo("温馨提示", "URL地址不能为空!")
        loading = False
        return True

    url = str(url).replace('\n', ' ')
    data = {
        'url': url
    }

    response = sendRequest('http://www.toolzl.com/Tools/Api/getWxArticleImages.html', data)
    response_url = response['data']['url']
    if len(response_url) == 0:
        MessageBox.showinfo("温馨提示", "URL地址有误!")
        loading = False
        return True

    url_arr = str(response_url).split('\n')
    download_url = url_arr[0]
    selectSavePath(download_url)


def thread_it(func, *args):
    '''将函数打包进线程'''
    # 创建
    t = threading.Thread(target=func, args=args)
    # 守护 !!!
    t.setDaemon(True)
    # 启动
    t.start()


if __name__ == '__main__':
    # 状态
    loading = False

    base_host = "http://www.toolzl.com/Tools/Api/getWxArticleImages.html"
    commonHeaders = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    }

    window = Tk()
    # 第2步，给窗口的可视化起名字
    window.title('公众号文章封面助手')
    window.iconbitmap("favicon.ico")

    width, height = 1024, 768  # 窗口大小
    x, y = (window.winfo_screenwidth() - width) / 2, (window.winfo_screenheight() - height) / 2
    window.geometry('%dx%d+%d+%d' % (width, height, x, y))  # 窗口位置居中

    m1 = PanedWindow(orient=VERTICAL)  # 默认是左右分布的
    m1.pack(fill=BOTH, expand=1)

    m2 = PanedWindow(m1)  # 默认是左右分布的
    m1.add(m2)

    L1 = Label(m2, text='公众号文章地址', width=20)
    m2.add(L1)

    T1 = Text(m1, height=5)
    m2.add(T1)

    m3 = PanedWindow(m1)  # 默认是左右分布的
    m1.add(m3)

    hi_there = Button(m3, text="获取封面", command=lambda: thread_it(startCallBack))
    m3.add(hi_there)

    m5 = PanedWindow(m1)  # 默认是左右分布的
    m1.add(m5)

    # 进入消息循环
    window.mainloop()
