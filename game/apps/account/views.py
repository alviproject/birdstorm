from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect
from rest_framework import viewsets, status
from game.apps.account import models
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response


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
    user = get_user_model().objects.create_user(username=str(count+1))
    user = authenticate(user=user)
    login(request, user)
    return redirect('/')