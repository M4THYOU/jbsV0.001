from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from serverauth.user_class import RegisteringUser
from serverauth.serializers import RegisteringUserSerializer
# Create your views here.

@csrf_exempt
def post_user(request):

    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = RegisteringUserSerializer(data=data)
        if serializer.is_valid():
            reguser = serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
