from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question
import json
import trade_base

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

def trade_test(request):
    return render(request, 'polls/trade.html', )

@csrf_exempt
def line1_test(request):
    if request.method == "POST":
        print("ajxtest POST")
        obj = [['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'bb'], [150, 230, 224, 218, 135, 147, 260, 270]]
        bar = [150, 230, 224, 218, 135, 147, 260]
        return JsonResponse({"obj": obj, 'bar': bar})
    else:
        return render(request, 'polls/line1.html', )

@csrf_exempt
def tricker_test(request):
    if request.method == "POST":
        tricker_id=2
        tricker_id_dir="/home/zc/github/markket_project/stock_date/configuration/trade/comanpy_history/"
        with open(tricker_id_dir+str(tricker_id)+".json", 'r') as f:
            json_data = json.load(f)
        timestr_list=[]
        price_list=[]
        for key in json_data.keys():
            timestr_list.append(key)
            price_list.append(json_data[key]["close"])
        #obj = [['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'bb'], [150, 230, 224, 218, 135, 147, 260, 270]]
        obj = []
        obj.append(timestr_list)
        obj.append(price_list)
        bar = [150, 230, 224, 218, 135, 147, 260]
        return JsonResponse({"obj": obj, 'bar': bar})
    else:
        return render(request, 'polls/tricker_line_sample.html', )

@csrf_exempt
def tricker_test2(request):
    if request.method == "POST":
        #obj = [['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'bb'], [150, 230, 224, 218, 135, 147, 260, 270]]
        return JsonResponse({"obj": obj, 'bar': bar})
    else:
        return render(request, 'polls/candlestickConnect.html', )

@csrf_exempt
def candlestick_large(request):
    if request.method == "POST":
        #obj = [['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'bb'], [150, 230, 224, 218, 135, 147, 260, 270]]

        bar = [150, 230, 224, 218, 135, 147, 260]
        obj = [["2004-01-02",10452.74,10409.85,10367.41,10554.96,168890000],["2004-01-05",10411.85,10544.07,10411.85,10575.92,221290000],["2004-01-06",10543.85,10538.66,10454.37,10584.07,191460000],["2004-01-07",10535.46,10529.03,10432,10587.55,225490000]]
        return JsonResponse({"obj": obj, 'bar': bar})
    else:
        return render(request, 'polls/candlestick-large.html', )

@csrf_exempt
def candlestickConnect(request):
    if request.method == "POST":
        #obj = [['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'bb'], [150, 230, 224, 218, 135, 147, 260, 270]]

        bar = [150, 230, 224, 218, 135, 147, 260]
        obj = [["2004-01-02",10452.74,10409.85,10367.41,10554.96,168890000],["2004-01-05",10411.85,10544.07,10411.85,10575.92,221290000],["2004-01-06",10543.85,10538.66,10454.37,10584.07,191460000],["2004-01-07",10535.46,10529.03,10432,10587.55,225490000]]
        return JsonResponse({"obj": obj, 'bar': bar})
    else:
        return render(request, 'polls/candlestickConnect.html', )

@csrf_exempt
def tricker_pie(request):
    if request.method == "POST":
        with open("/home/zc/github/markket_project/stock_date/configuration/trade/day_mode/2025-03-19_wave_3.json",'r') as f:
            data = json.load(f)

        report_data = data["report_total"]
        obj=[]
        for key in report_data.keys():
            dict_item={}
            dict_item["value"] = report_data[key]
            dict_item["name"] = key
            obj.append(dict_item)

        #obj = [['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'bb'], [150, 230, 224, 218, 135, 147, 260, 270]]
        #obj = [["2004-01-02",10452.74,10409.85,10367.41,10554.96,168890000],["2004-01-05",10411.85,10544.07,10411.85,10575.92,221290000],["2004-01-06",10543.85,10538.66,10454.37,10584.07,191460000],["2004-01-07",10535.46,10529.03,10432,10587.55,225490000]]
        return JsonResponse({"obj": obj})
    else:
        return render(request, 'polls/tricker_pie.html', )


@csrf_exempt
def get_wave_comanpy_list(request):
    if request.method == "POST":
        with open("/home/zc/github/markket_project/stock_date/configuration/trade/day_mode/2025-03-19_wave_3.json",'r') as f:
            data = json.load(f)
        obj=[]
        report_data = data["tricker_list_dict"]["333"]
        company_day_price = data["tricker_price_dict"]
        for key in report_data:
            item1=[]
            item1.append(key)
            item1.append("333")
            val = ((company_day_price[key][3] - company_day_price[key][1])/company_day_price[key][1])*100
            print(company_day_price[key], val)

            item1.append("%0.2f"%val)
            obj.append(item1)
        return JsonResponse({"obj": obj})

@csrf_exempt
def mutline_tricker_price(request):
    if request.method == "POST":
        with open("/home/zc/github/markket_project/stock_date/configuration/trade/day_mode/2025-03-28_wave_3.json",'r') as f:
            data = json.load(f)
        tricker_id_list  = data["tricker_list_dict"]["333"]
        #date_list=trade_base.company_list_trade_load_to_line([2,30,31,32])
        #print(tricker_id_list)
        date_list=trade_base.company_list_trade_load_to_line(tricker_id_list)
        print(date_list)
        return JsonResponse({"obj": date_list})
    else:
        return render(request, 'polls/mutline_tricker_price.html', )

