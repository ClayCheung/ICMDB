from django.db import models
from django.contrib.auth import models as auth_models


# Create your models here.



class Role(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'role'
        verbose_name_plural = "roles"

class UserInfo(auth_models.AbstractUser):
    role = models.ManyToManyField(
        Role,
        blank=True,
    )
    telephone = models.CharField(max_length=20, verbose_name="电话")
    department = models.CharField(null=True, blank=True, max_length=20, verbose_name="部门")
    position = models.CharField(null=True, blank=True, max_length=64, verbose_name="职位")
    description = models.TextField(null=True, blank=True, verbose_name="描述")

    # phone = models.CharField(max_length=20)

    def __str__(self):
        return "{0}{1}".format(self.last_name,self.first_name)

    class Meta:
        verbose_name = '内部用户'
        verbose_name_plural = "内部用户"
