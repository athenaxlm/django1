from django.core.cache import cache
from django.http import Http404
from django.shortcuts import render

from .models import GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner, GoodsSKU


# Create your views here.
def index(request):
    context = cache.get('index_page_data')

    if context is None:
        # 1.查询所有的分类
        category_list = GoodsCategory.objects.filter(isDelete=False)
        # print(category_list)

        # 2.查询首页推荐商品
        banner_list = IndexGoodsBanner.objects.all().order_by('index')

        # 3.查询首页广告
        promotion_list = IndexPromotionBanner.objects.all().order_by('index')
        # 4.遍历分类，查询每个分类的标题推荐、图片推荐
        for category in category_list:
            # print(category)
            category.title_list = IndexCategoryGoodsBanner.objects.filter(category=category, display_type='0').order_by(
                'index')
            category.image_list = IndexCategoryGoodsBanner.objects.filter(category=category, display_type='1').order_by(
                'index')

        context = {
            'category_list': category_list,
            'banner_list': banner_list,
            'promotion_list': promotion_list,
        }
        cache.set('index_page_data', context, 3600)

    response = render(request, 'index.html', context)

    # # 响应体
    # html_str =response.content.decode()
    #
    # with open(os.path.join(settings.BASE_DIR,'static/index.html'),'w') as html_index:
    #     html_index.write(html_str)

    return response


def detail(request, sku_id):
    try:
        sku = GoodsSKU.objects.get(pk=sku_id)
    except:
        return Http404()

    category_list = GoodsCategory.objects.all()

    prom_list = sku.category.goodssku_set.all().order_by('-id')[0:2]

    sku_list = sku.goods.goodssku_set.all()

    context = {
        'title': '商品介绍',
        'sku': sku,
        'category_list': category_list,
        'sku_list': sku_list,
        'prom_list': prom_list
    }

    return render(request, 'detail.html', context)


def list(request, category_id):
    category = GoodsCategory.objects.get(pk=category_id)

    new_list = GoodsSKU.objects.filter(category_id=category_id).order_by('-id')[0:2]
    new_list1 = GoodsSKU.objects.filter(category=category).order_by('-id')[0:2]

    context = {

    }
    return render(request, 'list.html', context)
