from django.shortcuts import render

# Create your views here.

def testview(request):
    test_para = "This is some \"dynamic\" text from the view."

    return render(request, 'test_page.html', {'test_p':test_para})
