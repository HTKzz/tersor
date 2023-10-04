from rest_framework.views import APIView
from rpy2.robjects import pandas2ri
from rpy2.robjects import conversion, default_converter
from .models import Model, Input
from rest_framework import status
from rest_framework.response import Response
from keras.preprocessing import image
# from django.core.files.storage import FileSystemStorage

import matplotlib.pyplot as plt
import rpy2.robjects as ro
import io
import tensorflow as tf
import numpy as np
import pandas as pd
import base64

path = '/home/init/test/tersor/templates/tensor/my_model.h5'
path2 = '/home/init/test/tersor/templates/tensor/my_model2.h5'
path3 = '/home/init/test/tersor/templates/tensor/my_model3.h5'
path4 = '/home/init/test/tersor/templates/tensor/my_model4.h5'

# 파일 저장 (파일을 저장할수도 있음)
# f = request.FILES.get('imgfile')
# fs = FileSystemStorage(location='/home/init/test/tersor/static/')
# filename = fs.save(f.name, f)

class Model1(APIView):
    def post(self, request):
        model = tf.keras.models.load_model(path, compile=True)

        p = request.data.pop('text')
        z = float(p)
        x = np.arange(z-10, z+7, 1)

        # 그래프 그리기 (그래프로 그리는 방법을 사용할수도 있음)
        # plt.grid(color = "gray", alpha=.5, linestyle='--')

        # plt.plot(x, model.get_weights()[0][0][0]*x+model.get_weights()[1][0], label='')
        # plt.vlines(z, model.predict([z-10]), model.predict([z]), color="green")
        # plt.hlines(model.predict([z]), z-10, z, color="red")

        # plt.text(z, model.predict([z-10]) - 2, '%.1f' %z, ha='center', va='bottom', size = 12)
        # plt.text(z-8, model.predict([z]), '%.5f' %model.predict([z]), ha='center', va='bottom', size = 12)

        # my_stringIObytes = io.BytesIO()
        # plt.savefig(my_stringIObytes, format='jpg')
        # my_stringIObytes.seek(0)
        # my_base64_jpgData = base64.b64encode(my_stringIObytes.read()).decode()
        # plt.clf()

        y = model.predict([z])

        return Response({'y':y[0][0], }, status=status.HTTP_200_OK)

class Model2(APIView):
    def post(self, request):
        model = tf.keras.models.load_model(path4, compile=True)

        p = request.data.pop('text')
        z = float(p)
        
        # decode된 이미지파일을 base64로 다시변환
        imgdata = base64.b64decode(request.data.pop('img'))
        dataBytesIO = io.BytesIO(imgdata)

        # keras모델에 입력가능하게 이미지 변환
        img = image.load_img(dataBytesIO, target_size=(150, 150))
        x = np.expand_dims(img, axis=0)
        images = np.vstack([x])

        y = model.predict(images, batch_size=10)

        if y[0] > 0:
            result = "강아지 입니다"
        else:
            result = "고양이 입니다"

        return Response({'y':z, 'result': result}, status=status.HTTP_200_OK)

class Model3(APIView):
    def get(self, request):
        p = request.data.pop('text')
        z = float(p)

        # r파일 불러오기
        ro.r.load('/home/init/test/tersor/templates/tensor/hi.RData')

        # lms라는 모델에 접근
        lms = ro.r('lms')

        pd_df = pd.DataFrame({'x': [z], 'x2': [z ** 2]})

        # r파일에서 원하는 데이터프레임 형태로 바꾸기
        with ro.conversion.localconverter(ro.default_converter + ro.pandas2ri.converter):
            r_from_pd_df = ro.conversion.py2rpy(pd_df)

        y = ro.r.predict(lms, r_from_pd_df)
        y = np.asarray(y)

        return Response({'y':y[0],}, status=status.HTTP_200_OK)