import re

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from utils import celery_tasks
from .models import User, Address, AreaInfo


# Create your views here.
class RegisterView(View):
    """类视图：处理注册"""

    def get(self, request):
        """处理GET请求，返回注册页面"""
        return render(request, 'register.html')

    def post(self, request):
        """处理POST请求，实现注册逻辑"""
        # return HttpResponse('这里实现注册逻辑')
        user_name = request.POST.get('user_name')
        password = request.POST.get('pwd')
        cpassword = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        if not all([user_name, password, cpassword, email]):
            return render(request, 'register.html')

        if not re.match(r"^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            return render(request, 'register.html')

        if allow != 'on':
            return render(request, 'register.html')

        if password != cpassword:
            return render(request, 'register.html')

        # 用户名是否存在
        if User.objects.filter(username=user_name).count() >= 1:
            return render(request, 'register.html')

        # 4.保存用户对象
        try:
            user = User.objects.create_user(user_name, email, password)
        except IntegrityError:
            return render(request, 'register.html')

        # 4.1默认用户创建后是激活状态，此处逻辑为需要用户手动激活，则设置为非激活
        user.is_active = False
        user.save()
        send_active_mail(request)
        # 5.提示
        return HttpResponse('请到邮箱中激活')


def username(request):
    uname = request.GET.get('uname')
    result = User.objects.filter(username=uname).count()
    return JsonResponse({'result': result})


def send_active_mail(request):
    user = User.objects.get(pk=1)
    # user_dict = {'user_id': user.id}
    # serializer = Serializer(settings.SECRET_KEY, expires_in=300)
    # str1 = serializer.dumps(user_dict).decode()
    #
    # mail_body = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % str1
    # send_mail('用户激活', '', settings.EMAIL_FROM, [user.email], html_message=mail_body)
    celery_tasks.send_active_mail.delay(user.email, user.id)
    return HttpResponse('请到邮箱中激活')


def user_active(request, user_str):
    # 1.从地址中接收用户编号(见url配置)

    # 加逻辑：解密
    serializer = Serializer(settings.SECRET_KEY)
    # 如果时间超过规定的时间则会抛异常
    try:
        user_dict = serializer.loads(user_str)
        user_id = user_dict.get('user_id')
        print('----------------%s' % user_id)
    except:
        return HttpResponse('地址无效')

    # 2.根据编号查询用户对象
    user = User.objects.get(pk=user_id)
    # 3.修改is_active属性为True
    user.is_active = True
    user.save()
    # 4.提示：转到登录页
    return redirect('/user/login')


# 1.将代码定义到函数中
# 2.为函数添加装饰器@app.task
# 3.在视图中调用：函数.delay(参数)
# 4.复制项目代码一份
# 5.在复制出来的代码中修改任务文件，加载django的配置
# 6.在复制出来的代码下，开启新进程


class loginView(View):
    def get(self, request):
        username = request.COOKIES.get('username', '')
        context = {
            'username': username
        }
        return render(request, 'login.html', context)

    def post(self, request):
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        remember = request.POST.get('remember')
        # 2.验证完整性:可以不传递remember
        if not all([username, pwd]):
            return render(request, 'login.html')

        # 3.验证正确性：查询用户名与密码对应的用户是否存在
        # 如果用户名与密码正确，则返回user对象，如果错误，则返回None
        user = authenticate(username=username, password=pwd)
        # 判断是否正确
        if user is None:
            return render(request, 'login.html', {'msg': '用户名或密码错误'})

        # ---加逻辑1：状态保持
        login(request, user)
        # 获取response对象
        # ---加逻辑3：如果有来源页面，则转到那个页面，如果没有，则转到登录页面
        login_url = request.GET.get('next', '/user')
        response = redirect(login_url)

        # ---加逻辑2：记住用户名，存储到cookie中
        if remember is None:
            response.delete_cookie('username')
        else:
            response.set_cookie('username', username, expires=60 * 60 * 24 * 7)

        # 如果用户正确则返回首页
        return response


def logout_view(request):
    logout(request)
    return redirect('/user/login')


@login_required()
def info(request):
    context = {}
    return render(request, 'user_center_info.html', context)


@login_required
def order(request):
    context = {}
    return render(request, 'user_center_order.html', context)


class SiteView(View):
    def get(self, request):
        # 获取当前登录的用户
        user = request.user
        # 查找当前用户的所有收货地址
        addr_list = user.address_set.all()
        print(addr_list)
        context = {
            'addr_list': addr_list,
            'title': '收货地址'
        }
        return render(request, 'user_center_site.html', context)

    def post(self, request):
        dict1 = request.POST
        receiver_name = dict1.get('receiver_name')
        province_id = dict1.get('province')
        city_id = dict1.get('city')
        district_id = dict1.get('district')
        detail_addr = dict1.get('detail_addr')
        zip_code = dict1.get('zip_code')
        receiver_mobile = dict1.get('receiver_mobile')
        # 3.创建对象
        addr = Address()
        addr.receiver_name = receiver_name
        addr.province_id = province_id
        addr.city_id = city_id
        addr.district_id = district_id
        addr.detail_addr = detail_addr
        addr.zip_code = zip_code
        addr.receiver_mobile = receiver_mobile
        addr.user_id = request.user.id
        # 4.保存
        addr.save()
        return redirect('/user/site')


def area(request):
    pid = request.GET.get('pid')
    if pid is None:
        area_list = AreaInfo.objects.filter(aParent__isnull=True)
    else:
        area_list = AreaInfo.objects.filter(aParent_id=pid)
    list1 = []
    for i in area_list:
        list1.append({'id': i.id, 'title': i.atitle})
    context = {
        'list': list1
    }
    return JsonResponse(context)
