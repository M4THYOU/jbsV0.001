from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from serverauth.user_class import RegisteringUser
from serverauth.serializers import RegisteringUserSerializer
# Create your views here.

@csrf_exempt
def post_user(request):

    if request.method == 'GET':
        raise Http404('No page found')
    elif request.method == 'POST':

