from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from django.core.mail import send_mail
#引入Celery类
from celery import Celery
#创建celery对象，通过broker指定存储队列的数据库(redis)
app = Celery('celery_tasks', broker='redis://127.0.0.1:6379/4')

#将函数设置成celery的任务
@app.task
def send_active_mail(user_email,user_id):
    # 对用户编号进行加密
    user_dict = {'user_id': user_id}
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    str1 = serializer.dumps(user_dict).decode()
    #发邮件
    mail_body = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % str1
    send_mail('用户激活', '', settings.EMAIL_FROM, [user_email], html_message=mail_body)