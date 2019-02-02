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
    phone = models.CharField(max_length=32)

    def __str__(self):
        return "{0}{1}".format(self.last_name,self.first_name)

    class Meta:
        verbose_name = '内部用户'
        verbose_name_plural = "内部用户"
