from django.shortcuts import render
from django_redis import get_redis_connection
from django.contrib.auth.decorators import login_required
from .models import GoodsSKU
# Create your views here.

@login_required
def index(request):
    skuid_list = request.GET.getlist('sku_id')

    key = 'cart%d'%request.user.id

    redis_client = get_redis_connection()

    sku_list = []

    for sku_id in skuid_list:
        sku = GoodsSKU.objects.get(pk=sku_id)
        count = redis_client.hget(key,sku_id)

        sku.count = count
        sku_list.append(sku)

    # 获取当前登录的用户
    user = request.user
    # 查找当前用户的所有收货地址
    addr_list = user.address_set.all()

    context={
        'sku_list':sku_list,
        'addr_list':addr_list
    }


    return render(request,'place_order.html',context)
