# Generated by Django 5.0.6 on 2024-07-01 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0003_alter_comments_options_alter_customuser_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalrecord',
            name='report_img',
            field=models.ImageField(blank=True, upload_to='media/'),
        ),
    ]
