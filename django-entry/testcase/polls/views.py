from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question
import json
import trade_base
import os
from datetime import date, timedelta
from datetime import datetime, timedelta

index_list= [
["每日股票涨跌个数", "line_shows/"],
["每日股票形态", "wave_list/333"],
["股票K线图", "tricker_pie/000002"],
["股票形态统计", "wave_list_all/"],
["底价反转", "price_min_report/"]
]

wavedata_list= [
"333",
"133",
"233",
"222",
"221",
"331",
"332",
"223",
"111",
"112",
"113",
"121",
"122",
"123",
"131",
"132",
"211",
"212",
"213",
"231",
"232",
"311",
"312",
"313",
"321",
"322",
"323"
]

def _get_wave_data(timestr, wave_type):
    filename="/home/zc/github/markket_project/stock_date/configuration/trade/day_mode/"+timestr+"_wave_3.json"
    if not os.path.exists(filename):
        return []

    with open(filename,'r') as f:
        data = json.load(f)
    tricker_id_list  = data["tricker_list_dict"][wave_type]

    date_list=trade_base.company_list_trade_load_to_line(tricker_id_list)
    return date_list

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    context = {'index_list': index_list}
    return render(request, 'polls/index.html', context)


def test(request):
    categories = ['衬衫', '羊毛衫', '雪纺衫', '裤子', '高跟鞋', '袜子']
    sales_data = [120, 200, 150, 80, 70, 110]
    file=os.path.join(trade_base.home_path(), "configuration/trade/report/price_min.json")
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    #context = {'line_index': json.dumps(list(data.keys()), ensure_ascii=False), 'line_values': json.dumps(list(data.values()), ensure_ascii=False)}
    context = {'line_index': json.dumps(categories, ensure_ascii=False), 'line_values': json.dumps(sales_data, ensure_ascii=False)}

    print(list(data.keys()))
    print(list(data.values()))
    return render(request, 'polls/test.html', context)

def price_min_report(request):
    file=os.path.join(trade_base.home_path(), "configuration/trade/report/price_min.json")
    with open(file, 'r', encoding='utf-8') as f:
        min_data = json.load(f)
    file=os.path.join(trade_base.home_path(), "configuration/trade/report/price_max.json")
    with open(file, 'r', encoding='utf-8') as f:
        max_data = json.load(f)

    file=os.path.join(trade_base.home_path(), "configuration/trade/report/price_history.json")
    with open(file, 'r', encoding='utf-8') as f:
        min_max_history_data = json.load(f)

    context = {
            'line_min_index': json.dumps(list(min_data.keys()), ensure_ascii=False),
            'line_min_values': json.dumps(list(min_data.values()), ensure_ascii=False),
            'line_max_index': json.dumps(list(max_data.keys()), ensure_ascii=False),
            'line_max_values': json.dumps(list(max_data.values()), ensure_ascii=False),
            'line_history_min_index': json.dumps(list(min_max_history_data["min"].keys()), ensure_ascii=False),
            'line_history_min_values': json.dumps(list(min_max_history_data["min"].values()), ensure_ascii=False),
            'line_history_max_index': json.dumps(list(min_max_history_data["max"].keys()), ensure_ascii=False),
            'line_history_max_values': json.dumps(list(min_max_history_data["max"].values()), ensure_ascii=False),
            }

    return render(request, 'polls/price_min_report.html', context)

def wave_list_all(request):
    wavelist=[]
    timestr=trade_base.get_last_workdate()
    filename="/home/zc/github/markket_project/stock_date/configuration/trade/day_mode/"+timestr+"_wave_3.json"
    with open(filename,'r') as f:
        data = json.load(f)
    for item in data["tricker_list_dict"].keys():
        wavelist.append([item, len(data["tricker_list_dict"][item]), data["tricker_list_dict"][item]])

    tricker_id_list  = data["tricker_list_dict"]["333"]

    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    context = {'tricker_id_list': tricker_id_list, 'wavelist': wavelist}
    #context = {}
    print(tricker_id_list)
    return render(request, 'polls/wave_list_all.html', context)

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
def tricker_pie_noargs(request):
    if request.method == "POST":
        tricker_id = request.POST.get("tricker_id")
        report_data=[]
        tricker_data = trade_base.company_trade_load(tricker_id)
        for key in tricker_data.keys():
            item=[key, tricker_data[key]["open"], tricker_data[key]["close"], "%0.2f"%(tricker_data[key]["close"] - tricker_data[key]["open"]), "%0.4f"%((tricker_data[key]["close"] - tricker_data[key]["open"])/tricker_data[key]["open"]), tricker_data[key]["low"], tricker_data[key]["high"], tricker_data[key]["volume"] * tricker_data[key]["close"] , tricker_data[key]["volume"],"-"]
            report_data.append(item)
        with open("/home/zc/github/markket_project/stock_date/configuration/trade/day_mode/2025-03-19_wave_3.json",'r') as f:
            data = json.load(f)
        print(report_data)
        return JsonResponse({"obj": report_data})
    else:
        return render(request, 'polls/tricker_pie.html', )

@csrf_exempt
def tricker_pie(request, tricker_id):
    report_data=[]
    tricker_data = trade_base.company_trade_load(tricker_id)
    for key in tricker_data.keys():
        item=[key, tricker_data[key]["open"], tricker_data[key]["close"], "%0.2f"%(tricker_data[key]["close"] - tricker_data[key]["open"]), "%0.4f"%((tricker_data[key]["close"] - tricker_data[key]["open"])/tricker_data[key]["open"]), tricker_data[key]["low"], tricker_data[key]["high"], tricker_data[key]["volume"] * tricker_data[key]["close"] , tricker_data[key]["volume"],"-"]
        report_data.append(item)

    data={'items':report_data}
    context = {'report_data': json.dumps(data)}
    print(report_data)
    return render(request, 'polls/tricker_pie.html', context)

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
        timestr=trade_base.get_last_workdate()
        #with open("/home/zc/github/markket_project/stock_date/configuration/trade/day_mode/2025-04-17_wave_3.json",'r') as f:
        with open("/home/zc/github/markket_project/stock_date/configuration/trade/day_mode/"+timestr+"_wave_3.json",'r') as f:
            data = json.load(f)
        tricker_id_list  = data["tricker_list_dict"]["333"]
        #date_list=trade_base.company_list_trade_load_to_line([2,30,31,32])
        #print(tricker_id_list)
        date_list=trade_base.company_list_trade_load_to_line(tricker_id_list)
        print(date_list)
        return JsonResponse({"obj": date_list})
    else:
        return render(request, 'polls/mutline_tricker_price.html', )

@csrf_exempt
def line_shows(request):
    if request.method == "POST":
        report_data=[]
        number_list=[]
        number_list_0=[]
        number_list_1=[]
        number_list_2=[]
        with open("/home/zc/github/markket_project/stock_date/configuration/trade/day_mode/day_du.json",'r') as f:
            data = json.load(f)
        #report_data.append(["平", "跌", "涨"])
        report_data.append(["涨"])
        for item in data.values():
            print(item)
            if item[0] == 0 and len(number_list_0) != 0:
                number_list_0.append(number_list_0[-1])
                number_list_1.append(number_list_1[-1])
                number_list_2.append(number_list_2[-1])
            else:
                number_list_0.append(item[0])
                number_list_1.append(item[1])
                number_list_2.append(item[2])
        report_data.append(list(data.keys()))
        #number_list.append(number_list_0)
        #number_list.append(number_list_1)
        number_list.append(number_list_2)
        report_data.append(number_list)
        print(report_data)
        return JsonResponse({"obj": report_data})
    else:
        return render(request, 'polls/line_shows.html', )

@csrf_exempt
def wave_list(request, wave_type):
    if request.method == "POST":
        wave_type = request.POST.get("wave")
        timestr = request.POST.get("timestr")
        date_list=_get_wave_data(timestr, wave_type)
        return JsonResponse({"obj": date_list})
    else:
        context = {'wave_type': wave_type}
        return render(request, 'polls/wave_list.html', context)

@csrf_exempt
def wave_list_noargs(request):
    if request.method == "POST":
        report_data=[]
        return JsonResponse({"obj": report_data})
    else:
        return render(request, 'polls/wave_list.html', )

