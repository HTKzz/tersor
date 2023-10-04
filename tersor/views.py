from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from .models import Model, Input

import requests
import json
import base64
import os

os.environ['R_HOME'] = '/usr/lib/R'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

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

    # html에서 index를 사용하려고 list를 enumerate형태로 변환
    model = enumerate(model)

    return render(request, 'tensor/model_list.html', {'models': model, })

# 모델을 새로 등록
def model_newPost(request):
    if request.method == "POST":
        model = Model()
        model.title = request.POST['title']
        # apiName이 영어로 대소문자 구분이 안되어 소문자로 저장
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
    # 왼쪽에 모델 목록을 불러오기
    allModel = list(Input.objects.all())
    inputValue = Input.objects.filter(api_id=model.pk)[0]
    value = inputValue.value.split(',')

    return render(request, 'tensor/model_detail.html', {'model': model, 'inputValue': inputValue, 'allModel': allModel, })

# 모델에 따라 결과물 출력
def tensorDetail(request, pk):
    model = get_object_or_404(Model, apiName=pk)
    allModel = list(Input.objects.all())
    inputValue = Input.objects.filter(api_id=model.pk)[0]
    # ,를 기준으로 잘라서 리스트로 만듬
    tag = inputValue.tag.split(',')
    value = inputValue.value.split(',')

    if request.method == 'POST' or request.method == 'GET':
        # 모델에 따른 정해진 api주소 호출
        if model.apiName == 'model1':
            url = "/ten/api/"
        elif model.apiName == 'model2':
            url = "/ten/api2/"
        elif model.apiName == 'model3':
            url = "/ten/api3/"
        
        # 파일을 열때마다 list에 넣어줌
        f = []
        for i in range(len(tag)):
            if request.method == 'GET':
                if value[i] == 'text':
                    x = request.GET.get(tag[i])

            if request.method == 'POST':
                if value[i] == 'text':
                    x = request.POST.get(tag[i])
                if value[i] == 'image':
                    img = request.FILES[tag[i]]
                    f.append(img)
    
        dictA = {'x': x, 'model': model, 'inputValue': inputValue}

        # file.read()를 하면 다시 사용이 불가능해서 filecode안에 파일정보 담아둠
        filecode = []
        for i in range(len(f)):
            fc = f[i].file.read()
            filecode.append(fc)
            # for문 안에서 변수선언하는 유동변수 선언
            globals()['encoded_{}'.format(i)] = base64.b64encode(filecode[i]).decode()
            dictA['encoded{}'.format(i)] = globals()['encoded_{}'.format(i)]

        # 파일이 없을경우 filecode에 "null"대입
        if len(filecode) == 0:
            filecode.append("null")

        # API호출 (현재는 api에 이미지 코드가 들어가는건 model2에 이미지 한개밖에 없음 따라서 0번째 주소밖에
        # 없음)
        y = send_api(url, method, x, filecode[0])

        # y라는 키에 model에 따른 api호출된 결과정보를 담아줌
        if model.apiName == "model2":
            dictA['y'] = y.get('result')
        elif type(y) is str:
            dictA['y'] = y.get('y')
        else:
            dictA['y'] = y.get('y')
            dictA['graph'] = y.get('imgCode')

        # z값이 실수형 형식으로 들어오는지 확인후 다른형식이면 false반환
        try:
            z = isinstance(float(y.get('y')), float)
        except Exception as e:
            z = False

        dictA['z'] = z

        # 이미지의 개수를 html에서 hidden값으로 사용하기위해 넣어줌
        dictA['imageAmount'] = value.count("image")

        # 현재 model3엔 모든모델의 정보를 테이블 형태로 뿌려주게 되어있음
        dictA['allModel'] = allModel

        return render(request, 'tensor/result_form.html', dictA)