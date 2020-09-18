from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    """
    用户信息
    """
    uid             = models.AutoField(primary_key=True)
    username        = models.CharField("姓名",max_length=30, unique=True)
    mobile          = models.CharField("电话",max_length=11, null=True, blank=True)
    email           = models.EmailField("邮箱",max_length=100, unique=True)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Productions(models.Model):
    puuid           = models.UUIDField(primary_key=True)
    pname           = models.CharField(max_length=50, verbose_name='作品名称')
    uname           = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    sb3file         = models.FileField(upload_to='sb3file/', blank=True, null=True)
    sb3snap         = models.FileField(upload_to='sb3snap/', blank=True, null=True)
    category        = models.CharField(max_length=100, verbose_name='作品类别', blank=True, null=True)
    describe        = models.TextField(max_length=500, verbose_name="描述", blank=True, null=True)
    is_public       = models.BooleanField(verbose_name='是否公开', default='False', blank=False)
    is_previewable  = models.BooleanField(verbose_name='是否可预览', default='False', blank=False)
    is_editable     = models.BooleanField(verbose_name='是否可编辑', default='False', blank=False)
    is_shareable    = models.BooleanField(verbose_name='是否可分享', default='False', blank=False)
    is_downloadable = models.BooleanField(verbose_name='是否可下载', default='False', blank=False)
    publish_time    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '作品信息'
        verbose_name_plural = verbose_name

        def __str__(self):
            return self.name


    class Meta:
        verbose_name = '作品信息'
        verbose_name_plural = verbose_name

        def __str__(self):
            return self.name



