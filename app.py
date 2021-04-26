from flask import Flask,render_template,request,redirect,url_for
import base64
import re
from PIL import Image
from io import BytesIO
import numpy as np

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
            a.show()
            img = np.asarray(a) #640*480*4 png numpy.ndarry
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
            print(ID,'\t',name,'\t',Department,'\t',age)
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
