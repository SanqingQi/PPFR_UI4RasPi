from flask import Flask,render_template,request,redirect,url_for
import base64
import re
from PIL import Image
from io import BytesIO
import numpy as np
import face_recognition
from util import *
import time
from threading import Thread
import socket
import pickle
import datetime

backIPaddress="127.0.0.1"
backport=9090
middleIPaddress1="127.0.0.1"
middleport1=9090
middleIPaddress2="127.0.0.1"
middleport2=9090


# socket_1
tcp1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp1_socket.connect((middleIPaddress1, middleport1))

# socket_2
tcp2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp2_socket.connect((middleIPaddress2, middleport2))

# back_socket
back_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
back_socket.connect((backIPaddress, backport))


def send_wait(info, mode='auth'):
    assert mode=='auth' or mode=='register'
    if mode=='auth':
        assert len(info) == 2
        array=info[1]
        share1, share2 = share(array)
        ans=decode(share1,share2)
        print(array)
        print(ans-array)
        tcp1_socket.sendall(pickle.dumps([0, share1]))
        tcp2_socket.sendall(pickle.dumps([0, share2]))
    else:
        ID = int(info[0])
        assert len(info) == 5 and isinstance(ID, int)
        array = info[1]
        Name = info[2]
        Department = info[3]
        Age = int(info[4])
        share1, share2 = share(array)
        print(share1)
        print(share2)
        tcp1_socket.sendall(pickle.dumps([int(ID), share1]))
        tcp2_socket.sendall(pickle.dumps([int(ID), share2]))
        back_socket.sendall(pickle.dumps([int(ID), Name, Department, Age]))
    back_info = back_socket.recv(1024)
    back_info = pickle.load(back_info)
    print(back_info)
    return back_info


def decode_image(src):
    """
    解码图片
    :param src: 图片编码
        eg:
            src="data:image/gif;base64,R0lGODlhMwAxAIAAAAAAAP///
                yH5BAAAAAAALAAAAAAzADEAAAK8jI+pBr0PowytzotTtbm/DTqQ6C3hGX
                ElcraA9jIr66ozVpM3nseUvYP1UEHF0FUUHkNJxhLZfEJNvol06tzwrgd
                LbXsFZYmSMPnHLB+zNJFbq15+SOf50+6rG7lKOjwV1ibGdhHYRVYVJ9Wn
                k2HWtLdIWMSH9lfyODZoZTb4xdnpxQSEF9oyOWIqp6gaI9pI1Qo7BijbF
                ZkoaAtEeiiLeKn72xM7vMZofJy8zJys2UxsCT3kO229LH1tXAAAOw=="

    :return: class 'PIL.PngImagePlugin.PngImageFile'
    """
    # 1、信息提取
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", src, re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")

    else:
        raise Exception("Do not parse!")

    # 2、base64解码
    img = base64.urlsafe_b64decode(data)
    bytes_stream = BytesIO(img)
    roiimg = Image.open(bytes_stream)
    return roiimg

app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method=='POST':
        #认证：
        if request.form.get('action')=='auth':
            img_data = request.form.get('imgData')
            a=decode_image(img_data)
            img = np.asarray(a) #640*480*4 png numpy.ndarry
            im=Image.fromarray(img)
            im.save("out.png")
            im = face_recognition.load_image_file("out.png")
            array_list = face_recognition.api.face_encodings(im)
            if (len(array_list) > 0):
                array = array_list[0]
                info = send_wait([-1,array], mode='auth')
            else:
                info='未识别出人脸，请重新操作'
        #注册：
        else:
            ID=request.form.get('ID')
            name=request.form.get('Name')
            Department=request.form.get('Department')
            age=request.form.get('Age')
            img_data = request.form.get('imgData')
            a = decode_image(img_data)
            a.show()
            img = np.asarray(a)  # 640*480*4 png numpy.ndarry
            im = Image.fromarray(img)
            im.save("out.png")
            array_list = face_recognition.api.face_encodings("out.png")
            if len(array_list) > 0 and int(ID)!=0:
                array = array_list[0]
                print(ID, '\t', name, '\t', Department, '\t', age)
                info = send_wait([int(ID), array, name, Department, age], mode='register')
            else:
                info = '未识别出人脸，请重新操作'
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
