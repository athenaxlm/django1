import os
os.environ["DJANGO_SETTINGS_MODULE"] = "dailyfresh.settings"
# 放到celery服务器上时将注释打开
import django
django.setup()
from celery import Celery
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import render
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from df_goods.models import GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner


# 创建celery对象，通过broker指定存储队列的数据库(redis)
app = Celery('celery_tasks', broker='redis://127.0.0.1:6379/4')


# 将函数设置成celery的任务
@app.task
def send_active_mail(user_email, user_id):
    # 对用户编号进行加密
    user_dict = {'user_id': user_id}
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    str1 = serializer.dumps(user_dict).decode()
    # 发邮件
    mail_body = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % str1
    send_mail('用户激活', '', settings.EMAIL_FROM, [user_email], html_message=mail_body)

@app.task
def gen_index():
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

    response = render(None, 'index.html', context)

    # 响应体
    html_str = response.content.decode()
    #
    with open(os.path.join(settings.BASE_DIR, '/home/python/Desktop/django1/dailyfresh/static/index.html'), 'w') as html_index:
        html_index.write(html_str)


