# Generated by Django 4.2.5 on 2023-09-29 18:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='uantity',
            new_name='qantity',
        ),
    ]
