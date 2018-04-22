# coding=utf-8
from fdfs_client.client import Fdfs_client
from django.conf import settings

#根据配置文件，创建fdfs的客户端，通过这个对象上传文件到fdfs
client=Fdfs_client(conf_path='/etc/fdfs/client.conf')
#调用方法上传文件
result=client.upload_by_file('/home/python/Pictures/Wallpapers/16060120276381.jpg')
print(result)