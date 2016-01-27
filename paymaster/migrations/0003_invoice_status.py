# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paymaster', '0002_refund'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='status',
            field=models.CharField(default=b'NEW', max_length=25, verbose_name='\u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435 \u043f\u043b\u0430\u0442\u0435\u0436\u0430', choices=[(b'NEW', '\u043f\u043b\u0430\u0442\u0435\u0436 \u0441\u043e\u0437\u0434\u0430\u043d'), (b'INITIATED', '\u043f\u043b\u0430\u0442\u0435\u0436 \u043d\u0430\u0447\u0430\u0442'), (b'PROCESSING', '\u043f\u043b\u0430\u0442\u0435\u0436 \u043f\u0440\u043e\u0432\u043e\u0434\u0438\u0442\u0441\u044f'), (b'COMPLETE', '\u043f\u043b\u0430\u0442\u0435\u0436 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d \u0443\u0441\u043f\u0435\u0448\u043d\u043e'), (b'CANCELLED', '\u043f\u043b\u0430\u0442\u0435\u0436 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d \u043d\u0435\u0443\u0441\u043f\u0435\u0448\u043d\u043e')]),
        ),
    ]
