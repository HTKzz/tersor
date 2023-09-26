from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Model, Input
from rpy2.robjects import pandas2ri
from rpy2.robjects import conversion, default_converter
from keras.preprocessing import image

import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import base64
import io
import os
os.environ['R_HOME'] = '/usr/lib/R'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import rpy2.robjects as ro
import tensorflow as tf

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
        
        imgdata = base64.b64decode(request.data.pop('img'))
        dataBytesIO = io.BytesIO(imgdata)
    
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

        #r모델
        ro.r.load('/home/init/test/tersor/templates/tensor/hi.RData')

        lms = ro.r('lms')

        pd_df = pd.DataFrame({'x': [z], 'x2': [z ** 2]})

        with ro.conversion.localconverter(ro.default_converter + ro.pandas2ri.converter):
            r_from_pd_df = ro.conversion.py2rpy(pd_df)

        y = ro.r.predict(lms, r_from_pd_df)
        y = np.asarray(y)

        return Response({'y':y[0],}, status=status.HTTP_200_OK)

# API 호출 함수
def send_api(path, method, value, img):
    if value == '':
        text = '숫자를 입력해주세요'
        return text

    API_HOST = "http://1.246.218.120:3300"
    url = API_HOST + path
    headers = {'Content-Type': 'application/json', 'charset': 'UTF-8', 'Accept': '*/*'}
    if img == "null":
        body = {
            "text": value,
        }
    else:
        body = {
            "text": value,
            "img": base64.b64encode(img).decode()
        }

    try:
        value = float(value)

        if method == 'GET':
            response = requests.get(url, headers=headers, data=json.dumps(body, ensure_ascii=False, indent="\t"))
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=json.dumps(body, ensure_ascii=False, indent="\t"))
        # print("response status %r" % response.status_code)
        # print("response text %r" % response.text)
        return response.json()

    except Exception as ex:
        text = '숫자가 아닙니다.'
        return text

# 모델 리스트를 출력
def tenList(request):
    model = list(Model.objects.all())
    model = enumerate(model)

    return render(request, 'tensor/model_list.html', {'models': model, })

# 모델을 새로 등록
def model_newPost(request):
    if request.method == "POST":
        model = Model()
        model.title = request.POST['title']
        model.apiName = request.POST['apiName'].lower()
        model.content = request.POST['content']
        try:
            model.save()
        except IntegrityError:
            return render(request, 'tensor/model_post.html', {'text': "api이름이 중복되었습니다."})

        inputValue = Input()
        inputValue.api_id = model
        inputValue.tag = request.POST['tagTotal']
        inputValue.value = request.POST['inputTotal']
        inputValue.save()
        return redirect('model_list')

    return render(request, 'tensor/model_post.html', {})

# 기존 모델을 수정
def model_update(request, pk):
    model = get_object_or_404(Model, apiName=pk)
    inputValue = Input.objects.filter(api_id=model.pk)[0]
    
    if request.method == "POST":
        model.title = request.POST['title']
        model.apiName = request.POST['apiName'].lower()
        model.content = request.POST['content']
        try:
            model.save()
        except IntegrityError:
            return render(request, 'tensor/model_update.html', {'model': model, 'inputValue': inputValue, 'text': "api이름이 중복되었습니다."})

        inputValue.tag = request.POST['tagTotal']
        inputValue.value = request.POST['inputTotal']
        inputValue.save()
        return redirect('model_list')

    return render(request, 'tensor/model_update.html', {'model': model, 'inputValue': inputValue, })

# 모델을 삭제
def model_delete(request, pk):
    model = get_object_or_404(Model, pk=pk)
    model.delete()
    return redirect('model_list')

# 모델의 상세정보를 출력
def model_detail(request, pk):
    model = get_object_or_404(Model, apiName=pk)
    allModel = list(Input.objects.all())
    inputValue = Input.objects.filter(api_id=model.pk)[0]
    value = inputValue.value.split(',')

    return render(request, 'tensor/model_detail.html', {'model': model, 'inputValue': inputValue, 'allModel': allModel, })

# 모델에 따라 결과물 출력
def tensorDetail(request, pk):
    model = get_object_or_404(Model, apiName=pk)
    allModel = list(Input.objects.all())
    inputValue = Input.objects.filter(api_id=model.pk)[0]
    tag = inputValue.tag.split(',')
    value = inputValue.value.split(',')

    if request.method == 'POST' or request.method == 'GET':
        if model.apiName == 'model1':
            url = "/ten/api/"
        elif model.apiName == 'model2':
            url = "/ten/api2/"
        elif model.apiName == 'model3':
            url = "/ten/api3/"

        method = request.method
        
        f = []
        for i in range(len(tag)):
            if method == 'GET':
                if value[i] == 'text':
                    x = request.GET.get(tag[i])

            if method == 'POST':
                if value[i] == 'text':
                    x = request.POST.get(tag[i])
                if value[i] == 'image':
                    img = request.FILES[tag[i]]
                    f.append(img)
    
        dictA = {'x': x, 'model': model, 'inputValue': inputValue}

        filecode = []
        for i in range(len(f)):
            fc = f[i].file.read()
            filecode.append(fc)
            globals()['encoded_{}'.format(i)] = base64.b64encode(filecode[i]).decode()
            dictA['encoded{}'.format(i)] = globals()['encoded_{}'.format(i)]
    
        if len(filecode) == 0:
            filecode.append("null")

        y = send_api(url, method, x, filecode[0])

        if model.apiName == "model2":
            dictA['y'] = y.get('result')
        elif type(y) is str:
            dictA['y'] = y.get('y')
        else:
            dictA['y'] = y.get('y')
            dictA['graph'] = y.get('imgCode')
    
        try:
            z = isinstance(float(y.get('y')), float)
        except Exception as e:
            z = False

        dictA['z'] = z
        dictA['imageAmount'] = value.count("image")
        dictA['allModel'] = allModel

        return render(request, 'tensor/result_form.html', dictA)