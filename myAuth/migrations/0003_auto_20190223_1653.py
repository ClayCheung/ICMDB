# Generated by Django 2.1.4 on 2019-02-23 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myAuth', '0002_auto_20190223_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='department',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='部门'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='position',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='职位'),
        ),
    ]
