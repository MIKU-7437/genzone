# Generated by Django 4.2.7 on 2023-11-13 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, default='customer_photos/default-profile-picture.jpg', null=True, upload_to='customer_photos/'),
        ),
    ]
