# Generated by Django 5.0 on 2024-11-12 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_galleryimage_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='main_image',
            field=models.ImageField(blank=True, null=True, upload_to='blog_images/'),
        ),
    ]
