from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('<int:question_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:question_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('test/', views.test, name='test'),
    path('test2/', views.test, name='test1'),
    path('ajxtest/', views.ajxtest, name='ajxtest'),
    path('trade/', views.trade_test, name='trade_test'),
    path('line1/', views.line1_test, name='line1_test'),
    path('tricker_line_sample/', views.tricker_test, name='tricker_test'),
    path('tricker_line_2/', views.tricker_test2, name='tricker_test2'),
    path('candlestick-large/', views.candlestick_large, name='candlestick_large'),
    path('candlestickConnect/', views.candlestickConnect, name='candlestickConnect'),
    path('tricker_pie/', views.tricker_pie_noargs, name='tricker_pie_noargs'),
    path('tricker_pie/<str:tricker_id>', views.tricker_pie, name='tricker_pie'),
    path('mutline_tricker_price/', views.mutline_tricker_price, name='mutline_tricker_price'),
    #股票形态的公司列表ajax接口
    path('get_wave_comanpy_list/', views.get_wave_comanpy_list, name='get_wave_comanpy_list'),
    #公司涨跌个数
    path('line_shows/', views.line_shows, name='line_shows'),
    path('wave_list', views.wave_list_noargs, name='wave_list_noargs'),
    path('wave_list/<str:wave_type>', views.wave_list, name='wave_list'),
    path('wave_list_all/', views.test, name='wave_list_all'),
]
