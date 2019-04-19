from django.shortcuts import render, render_to_response

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


def services(request):
    return render(request, 'webapp/services.html', {})


def blog(request):
    return render(request, 'webapp/blog.html', {})


def about(request):
    return render(request, 'webapp/about.html', {})


def shop(request):
    return render(request, 'webapp/shop.html', {})


def contact(request):
    return render(request, 'webapp/contact.html', {})
