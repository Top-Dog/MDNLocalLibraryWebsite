# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-18 07:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_auto_20171118_1632'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='author',
            options={'ordering': ['last_name'], 'permissions': (('can_modify_author', 'Create, modify, or delete authors'),)},
        ),
    ]
