from django.shortcuts import render
from .models import GoodsCategory,IndexGoodsBanner,IndexPromotionBanner,IndexCategoryGoodsBanner

# Create your views here.
def index(request):

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
        category.title_list = IndexCategoryGoodsBanner.objects.filter(category=category,display_type='0').order_by('index')
        category.image_list = IndexCategoryGoodsBanner.objects.filter(category=category,display_type='1').order_by('index')

    context = {
        'category_list':category_list,
        'banner_list':banner_list,
        'promotion_list':promotion_list,
    }
    return render(request,'index.html',context)