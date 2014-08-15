from django.contrib.auth import authenticate, login
from django.http.response import HttpResponse
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from game.apps.account import models
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response


#TODO use DRF functionality
def register(request):
    count = User.objects.count()
    user = User.objects.create_user(username=str(count+1))
    user = authenticate(user=user)
    login(request, user)
    return HttpResponse()


class Users(viewsets.ReadOnlyModelViewSet):
    model = User
    serializer_class = models.UserSerializer


class Account(RetrieveAPIView):
    serializer_class = models.AccountSerializer

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        serializer = models.AccountSerializer(user, context=dict(request=request))
        return Response(serializer.data)
