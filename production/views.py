import os
import json
import uuid
import base64
import requests
from datetime import datetime

from django.core.files.base import ContentFile
from django.http import StreamingHttpResponse, HttpResponse

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin

from aiscratch.logger import logger
from production.models import UserProfile, Productions
from production.serializers import UserProfileSerializers, UserDetailSerializers, ProductionsSerializers


class RegistrationViewSet(CreateModelMixin, viewsets.GenericViewSet):

    serializer_class = UserProfileSerializers
    queryset = UserProfile.objects.all()
    logger.info("Entering create user")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            data = {"code": True, "message": "Create successful"}
            return Response(data=data)

        data = {"code": False, "message": "Create failed"}
        return Response(data=data)

    def perform_create(self, serializer):
        return serializer.save()


class UserDetailViewSet(RetrieveModelMixin, UpdateModelMixin, viewsets.GenericViewSet):

    serializer_class = UserDetailSerializers
    queryset = UserProfile.objects.all()
    logger.info("Entering list userdetail")

    def retrieve(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        logger.info("Token: %s" %token)

        if not token:
            data = {"code": False, "message": "Please login"}
            return Response(data)

        tokenobj = Token.objects.filter(key=token).first()
        user_id = tokenobj.user_id
        user = UserProfile.objects.filter(uid=user_id).first()
        serializer = self.get_serializer(user)
        logger.info("Data: %s" % serializer.data)
        data = {"code": True, "message": serializer.data}
        return Response(data)

    def update(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        logger.info("Token: %s" % token)

        if not token:
            data = {"code": False, "message": "Please login"}
            return Response(data)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        logger.info("Data: %s" % serializer.data)
        if not serializer.is_valid():
            data = {"code": True, "message": "Update failed!"}
            return Response(data=data)

        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        data = {"code": True, "message": "Update successful"}
        return Response(data=data)


class ProductionViewSet(viewsets.ModelViewSet):
    queryset = Productions.objects.all()
    serializer_class = ProductionsSerializers

    authentication_classes = [TokenAuthentication,]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        for i in serializer.data:
            i['sb3snap'] = 'https://api.aiscratch.online/sb3snap/' + i['puuid']
            i['sb3file'] = 'https://api.aiscratch.online/sb3file/' + i['puuid']
        data = {'code': True, 'message': serializer.data}
        return Response(data)

    def create(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')

        if not token:
            data = {"code": False, "message": "Please login"}
            return Response(data)

        tokenobj = Token.objects.filter(key=token).first()
        user_id = tokenobj.user_id
        try:
            format, imgstr = request.data.get('sb3snap').split(';base64,')
            puuid = uuid.uuid4().hex
            sb3snap = ContentFile(base64.b64decode(imgstr), name=puuid + '.png')
            sb3file = request.data.get('sb3file')
            sb3file.name = puuid + '.sb3'
            data = {
                "puuid": puuid,
                "pname": request.data.get('pname'),
                "uname": user_id,
                "sb3file": sb3file,
                "sb3snap": sb3snap,
                "category": request.data.get('category'),
                'describe': request.data.get('describe'),
                "is_public": False,
                "is_previewable": False,
                "is_editable": False,
                "is_shareable": False,
                "is_downloadable": False,
                "publish_time": datetime.now()
            }
            serializer = self.get_serializer(data=data)

            if not serializer.is_valid(raise_exception=True):
                data = {"code": False, "message": "Create failed"}
                return Response(data)

            production = self.perform_create(serializer)
            data = {"code": True, "message": "Create successful"}
            return Response(data)

        except Exception as e:
            logger.error(str(e))
            data = {"code": False, "message": "Create failed"}
            return Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            data = {"code": False, "message": "Request failed"}
            return Response(data)

        serializer = self.get_serializer(instance)
        serializer_data  = json.loads(json.dumps(serializer.data))
        production_retrieve = {
            'sb3snap': 'https://api.aiscratch.online/sb3snap/' + serializer.data['puuid'],
            'sb3file': 'https://api.aiscratch.online/sb3file/' + serializer.data['puuid']
        }
        serializer_data.update(production_retrieve)
        data = {"code": True, "message": serializer_data}
        return Response(data)

    def perform_create(self, serializer):
        return serializer.save()

    def destroy(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')

        if not token:
            data = {"code": False, "message": "Please login"}
            return Response(data)

        instance = self.get_object()
        self.perform_destroy(instance)
        data = {"code": True, "message": "Delete successful"}
        return Response(data)


class Sb3Path(APIView):
    def get(self, request, puuid):
        logger.info("Entering Sb3Path(get)...")
        logger.info(puuid)
        product = Productions.objects.filter(puuid=puuid).first()
        if not product:
            data = {"code": False, "message": "Product not found"}
            return Response(data)

        filepath = 'media/' + str(product.sb3file)
        if not os.path.isfile(filepath):
            data = {"code": False, "message": "File not found"}
            return Response(data)

        logger.info(filepath)
        try:
            ufile = open(filepath, 'rb')
            stream = ufile.readlines()
            ufile.close()
            response = StreamingHttpResponse(stream)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename=%s'%product.pname
            #response['Access-Control-Allow-Origin'] = '*'
            logger.info('Done!')
            return response
        except Exception as e:
            logger.info(str(e))
            data = {"code": False, "message": "Exception occured"}
            return Response(data)


class Sb3Snap(APIView):
    def get(self, request, puuid):
        logger.info("Entering Sb3Snap(get)...")
        logger.info(puuid)
        product = Productions.objects.filter(puuid=puuid).first()
        if not product:
            data = {"code": False, "message": "Product not found"}
            return Response(data)

        filepath = 'media/' + str(product.sb3snap)
        if not os.path.isfile(filepath):
            data = {"code": False, "message": "File not found"}
            return Response(data)

        logger.info(filepath)
        try:
            ufile = open(filepath, 'rb')
            idata = ufile.read()
            ufile.close()
            logger.info('Done!')
            return HttpResponse(idata, content_type='image/png')
        except Exception as e:
            logger.info(str(e))
            data = {"code": False, "message": "Exception occured"}
            return Response(data)


class DownModelFile(APIView):
    def get(self, request, modelfile):
        modelpath = os.path.join('static/model', modelfile)
        modelfile = open(modelpath, 'rb')
        response = HttpResponse(modelfile)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="models.py"'
        return response


################################################################
#
# 语音聊天
#
################################################################
# 百度语音聊天

def get_token():
    url = "https://openapi.baidu.com/oauth/2.0/token"
    api_key = "HpCNfUms2pzAxbTESq2GAZsb"            # 自己申请的应用
    secret_key = "nCzDAqVLHpfPxKsbuGLIf5MV9WA1097W" # 自己申请的应用
    data = {'grant_type': 'client_credentials', 'client_id': api_key, 'client_secret': secret_key}
    r = requests.post(url, data=data)
    token = json.loads(r.text).get("access_token")
    return token

def recognize(_format, speech, rate, token, speech_length, channel, cuid):
    BAIDU_URL = "http://vop.baidu.com/server_api"
    data = {
        "format": _format,
        "lan": "zh",
        "token": token,
        "len": speech_length,
        "rate": rate,
        "speech": speech,
        "cuid": cuid,
        "channel": channel,
    }
    data_length = len(json.dumps(data).encode("utf-8"))
    headers = {"Content-Type": "application/json", "Content-Length": str(data_length)}
    r = requests.post(BAIDU_URL, data=json.dumps(data), headers=headers)
    return r.text


class AudioRecognaztion(APIView):

    def get(self, request, *args, **kwargs):
        data = {"code": True, "message": "Done"}
        return Response(data)

    def post(self, request, *args, **kwargs):
        data = request.data
        # 'format', 'rate', 'dev_pid', 'channel', 'token', 'cuid', 'len', 'speech'
        token = get_token()
        response = recognize(data['format'], data['speech'], data['rate'], token, data['len'], data['channel'], data['cuid'])
        return Response(response)


#图灵语音聊天
def chat(text):
    TULING_URL = 'http://www.tuling123.com/openapi/api'
    TULING_KEY = '906e872c1cd24acea9738c805a3a4796'
    data = {
        "key": TULING_KEY,
        "info": text,
        "userid": 'wechat-robot',
    }
    data_length = len(json.dumps(data).encode("utf-8"))
    headers = {"Content-Type": "application/json", "Content-Length": str(data_length)}
    r = requests.post(TULING_URL, data=json.dumps(data), headers=headers)
    return r.text

class ChatRobot(APIView):

    def get(self, request, *args, **kwargs):
        data = {"code": True, "message": "Done"}
        return Response(data)

    def post(self, request, *args, **kwargs):
        data = request.data
        response = chat(data['text'])
        return Response(response)
