import json

from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render
from django_redis import get_redis_connection
from haystack.generic_views import SearchView

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

    # 计算购物车总数量
    context['total_count'] = get_cart_total(request)

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

    # 最近浏览,判断用户是否登录
    if request.user.is_authenticated():
        browser_key = 'browser%d' % request.user.id
        # 创建redis服务器的连接，默认使用settings-->caches中的配置
        redis_client = get_redis_connection()
        # 如果当前商品编号已经存在了，则删除
        redis_client.lrem(browser_key, 0, sku_id)
        # 记录商品的编号
        redis_client.lpush(browser_key, sku_id)
        # 如果总个数超过5个，则删除最右侧的一个
        if redis_client.llen(browser_key) > 5:
            redis_client.rpop(browser_key)

    sku_list = sku.goods.goodssku_set.all()

    context = {
        'title': '商品介绍',
        'sku': sku,
        'category_list': category_list,
        'sku_list': sku_list,
        'prom_list': prom_list
    }

    # 计算购物车总数量
    context['total_count'] = get_cart_total(request)

    return render(request, 'detail.html', context)


def good_list(request, category_id):
    try:
        category = GoodsCategory.objects.get(pk=category_id)
    except:
        return Http404()

    category_list = GoodsCategory.objects.filter(isDelete=False)

    new_list = GoodsSKU.objects.filter(category_id=category_id).order_by('-id')[0:2]

    # 接收排序规则
    sort_str = '-id'  # 默认根据编号降序，最新
    sort = request.GET.get('sort', '1')
    if sort == '2':
        sort_str = 'price'  # 最便宜
    elif sort == '4':
        sort_str = '-price'  # 最贵
    elif sort == '3':
        sort_str = '-sales'  # 根据人气降序，最火
    else:
        sort = '1'

    sku_list = GoodsSKU.objects.filter(category_id=category_id).order_by(sort_str)

    # 对商品列表进行分页
    paginator = Paginator(sku_list, 1)
    # 获取总页码数
    num_pages = paginator.num_pages
    # 接收分页的页码
    pindex = request.GET.get('pindex', '1')
    # 验证页码的有效性
    try:
        pindex = int(pindex)
    except:
        pindex = 1
    if pindex <= 1:
        pindex = 1
    if pindex >= num_pages:
        pindex = num_pages

    # 获取第n页的数据
    page = paginator.page(pindex)
    plist = get_page_list(num_pages, pindex)

    context = {
        'title': '分类商品列表',
        'category': category,
        'category_list': category_list,
        'new_list': new_list,
        'sort': sort,
        'pindex': pindex,
        'page': page,
        'plist': plist,
    }

    # 计算购物车总数量
    context['total_count'] = get_cart_total(request)

    return render(request, 'list.html', context)


class MySearchView(SearchView):
    """My custom search view."""

    # 自定义向模板中传递的上下文
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # 运行完视图，会向模板中传递分页对象、当前页对象
        paginator = context['paginator']
        page = context['page_obj']
        context['plist'] = get_page_list(paginator.num_pages, page.number)

        # 向模板中传递分类信息
        context['category_list'] = GoodsCategory.objects.filter(isDelete=False)

        # 计算购物车总数量
        context['total_count'] = get_cart_total(self.request)

        return context


def get_page_list(num_pages, pindex):
    if num_pages <= 5:  # 如果当前总页数不足5个，则显示所有页码
        plist = range(1, num_pages + 1)  # [)
    elif pindex <= 2:  # 如果当前页码为1或2，不满足公式，固定输出
        plist = range(1, 6)
    elif pindex >= num_pages - 1:  # 共10页，则最后输出为6 7 8 9 10,不满足公式，固定输出
        plist = range(num_pages - 4, num_pages + 1)
    else:
        plist = range(pindex - 2, pindex + 3)
    return plist


def get_cart_total(request):
    '''查询购物车中的数据'''
    total_count = 0
    # 判断用户是否登录
    if request.user.is_authenticated():
        # 如果登录则从redis中读取数据
        # 连接redis
        redis_client = get_redis_connection()
        # 构造键
        key = 'cart%d' % request.user.id
        # 获取所有数量
        count_list = redis_client.hvals(key)  # []
        # 遍历相加
        if count_list:
            for count in count_list:
                total_count += int(count)
    else:
        # 如果未登录则从cookie中读取数据
        # 读取cookie
        cart_str = request.COOKIES.get('cart')
        if cart_str is not None:
            # 将字符串转换字典
            cart_dict = json.loads(cart_str)
            # 遍历相加
            for k, v in cart_dict.items():
                total_count += v

    return total_count
