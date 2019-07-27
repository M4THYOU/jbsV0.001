from django.shortcuts import render, render_to_response, HttpResponse
from django.db.utils import DataError
from .models import EmailInterest


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip

# Create your views here.


def handler404(request, exception, template_name='general/404.html'):
    response = render_to_response('general/404.html')
    response.status_code = 404
    return response


def handler500(request, template_name='general/500.html'):
    response = render_to_response('general/500.html')
    response.status_code = 500
    return response


def temp_home(request):
    return render(request, 'original/coming_soon_base.html', {})


def home(request):
    return render(request, 'webapp/index.html', {})


def works(request):
    return render(request, 'webapp/work.html', {})


def works_grid(request):
    return render(request, 'webapp/work-grid.html', {})


def works_grid_no_text(request):
    return render(request, 'webapp/work-grid-without-text.html', {})


def about_hive(request):
    return render(request, 'webapp/about-hive.html', {})


def blog(request):
    return render(request, 'webapp/blog.html', {})


def about(request):
    return render(request, 'webapp/about.html', {})


def shop(request):
    return render(request, 'webapp/shop.html', {})


def contact(request):
    return render(request, 'webapp/contact.html', {})


def privacy(request):
    return render(request, 'webapp/privacy.html', {})


def ajax_submit_email(request):
    data = request.POST.dict()

    email = data['email']

    if request.method == 'POST':
        ip = get_client_ip(request)

        try:
            email_interest = EmailInterest.objects.create(email=email, ip_address=ip)
        except DataError as e:
            raise ValueError(e)

        email_interest.save()

        return HttpResponse('We will get back to you soon!')

