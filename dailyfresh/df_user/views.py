import re
from django.conf import settings
from django.core.mail import send_mail
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .models import User


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
    user_dict = {'user_id': user.id}
    serializer = Serializer(settings.SECRET_KEY, expires_in=300)
    str1 = serializer.dumps(user_dict).decode()

    mail_body = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % str1
    send_mail('用户激活', '', settings.EMAIL_FROM, [user.email], html_message=mail_body)
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
