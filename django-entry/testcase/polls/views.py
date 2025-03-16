from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question

def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")

    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    #output = ', '.join([q.question_text for q in latest_question_list])
    #return HttpResponse(output)

    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    #template = loader.get_template('polls/index.html')
    #context = {
    #    'latest_question_list': latest_question_list,
    #}
    #return HttpResponse(template.render(context, request))
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)


def test(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/test1.html', context)
    #return HttpResponse("You're looking at question %s." % 0)

# Leave the rest of the views (detail, results, vote) unchanged
# Create your views here.
def detail(request, question_id):
    print("zz detail")
    return HttpResponse("You're looking at question %s." % question_id)

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

def test1(request):
    if request.method == "POST":
        print("POST")
        obj = ([{'value': 3, 'name': '未执行'}, {'value': 8, 'name': '已执行'}], ['未执行', '已执行'])
        bar = [120, 200, 150, 80, 70, 110, 130]
        return JsonResponse({"obj": obj, 'bar': bar})
    else:
        return render(request, 'test1.html', )

@csrf_exempt
def ajxtest(request):
    if request.method == "POST":
        print("ajxtest POST")
        obj = ([{'value': 3, 'name': '未执行'}, {'value': 8, 'name': '已执行'}], ['未执行', '已执行'])
        bar = [120, 200, 150, 80, 70, 110, 130]
        return JsonResponse({"obj": obj, 'bar': bar})
    else:
        print("ajxtest wget")
        return render(request, 'polls/index.html', )
