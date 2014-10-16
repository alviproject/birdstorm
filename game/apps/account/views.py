import django.contrib.auth
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect
from rest_framework import viewsets, status
from game.apps.account import models
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST


class Users(viewsets.ReadOnlyModelViewSet):
    model = User
    serializer_class = models.UserSerializer


class Account(RetrieveAPIView):
    serializer_class = models.AccountSerializer

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        serializer = models.AccountSerializer(user, context=dict(request=request))
        return Response(serializer.data)


#TODO could be done as part of Account class
@api_view(['POST'])
def register(request):
    #if request.user.is_authenticated():
    #    raise RuntimeError("user already authenticated")
    count = User.objects.count()
    user = django.contrib.auth.get_user_model().objects.create_user(username=str(count+1))
    user = django.contrib.auth.authenticate(user=user)
    django.contrib.auth.login(request, user)
    return redirect('/')


#TODO could be done as part of Account class
@api_view(['POST'])
def login(request):
    username = request.DATA['username']
    password = request.DATA['password']
    user = django.contrib.auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        django.contrib.auth.login(request, user)
        return redirect('/')
    return Response(status=HTTP_400_BAD_REQUEST)