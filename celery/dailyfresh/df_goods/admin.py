from django.contrib import admin
from django.core.cache import cache
from utils import gen_html, celery_tasks
from .models import GoodsCategory, Goods, IndexGoodsBanner, IndexCategoryGoodsBanner, IndexPromotionBanner


class BaseAdmin(admin.ModelAdmin):
    """商品活动信息的管理类,运营人员在后台发布内容时，异步生成静态页面"""

    def save_model(self, request, obj, form, change):
        """后台保存对象数据时使用"""

        # obj表示要保存的对象，调用save(),将对象保存到数据库中
        obj.save()
        # 调用celery异步生成静态文件方法，操作完表单后删除静态文件
        celery_tasks.gen_index.delay()
        # 修改了数据库数据就需要删除缓存
        cache.delete('index_page_data')
        gen_html.gen_index()

    def delete_model(self, request, obj):
        """后台保存对象数据时使用"""
        obj.delete()
        celery_tasks.gen_index.delay()
        cache.delete('index_page_data')
        gen_html.gen_index()


class IndexGoodsBannerAdmin(BaseAdmin):
    def save_model(self, request, obj, form, change):
        """后台保存对象数据时使用"""

        # obj表示要保存的对象，调用save(),将对象保存到数据库中
        obj.save()
        # 调用celery异步生成静态文件方法，操作完表单后删除静态文件
        celery_tasks.gen_index.delay()
        # 修改了数据库数据就需要删除缓存
        cache.delete('index_page_data')
        gen_html.gen_index()

    def delete_model(self, request, obj):
        """后台保存对象数据时使用"""
        obj.delete()
        celery_tasks.gen_index.delay()
        cache.delete('index_page_data')
        gen_html.gen_index()


class GoodsCategoryAdmin(BaseAdmin):
    def save_model(self, request, obj, form, change):
        """后台保存对象数据时使用"""

        # obj表示要保存的对象，调用save(),将对象保存到数据库中
        obj.save()
        # 调用celery异步生成静态文件方法，操作完表单后删除静态文件
        celery_tasks.gen_index.delay()
        # 修改了数据库数据就需要删除缓存
        cache.delete('index_page_data')
        gen_html.gen_index()

    def delete_model(self, request, obj):
        """后台保存对象数据时使用"""
        obj.delete()
        celery_tasks.gen_index.delay()
        cache.delete('index_page_data')
        gen_html.gen_index()


class IndexCategoryGoodsBannerAdmin(BaseAdmin):
    def save_model(self, request, obj, form, change):
        """后台保存对象数据时使用"""

        # obj表示要保存的对象，调用save(),将对象保存到数据库中
        obj.save()
        # 调用celery异步生成静态文件方法，操作完表单后删除静态文件
        celery_tasks.gen_index.delay()
        # 修改了数据库数据就需要删除缓存
        cache.delete('index_page_data')
        gen_html.gen_index()

    def delete_model(self, request, obj):
        """后台保存对象数据时使用"""
        obj.delete()
        celery_tasks.gen_index.delay()
        cache.delete('index_page_data')
        gen_html.gen_index()


class IndexPromotionBannerAdmin(BaseAdmin):
    def save_model(self, request, obj, form, change):
        """后台保存对象数据时使用"""

        # obj表示要保存的对象，调用save(),将对象保存到数据库中
        obj.save()
        # 调用celery异步生成静态文件方法，操作完表单后删除静态文件
        celery_tasks.gen_index.delay()
        # 修改了数据库数据就需要删除缓存
        cache.delete('index_page_data')
        gen_html.gen_index()

    def delete_model(self, request, obj):
        """后台保存对象数据时使用"""
        obj.delete()
        celery_tasks.gen_index.delay()
        cache.delete('index_page_data')
        gen_html.gen_index()


# Register your models here.
admin.site.register(GoodsCategory, GoodsCategoryAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexCategoryGoodsBanner, IndexCategoryGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(Goods)
