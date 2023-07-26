# Generated by Django 4.2.2 on 2023-07-17 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_remove_profile_blocked_user_profile_blocked_profile'),
        ('posts', '0003_alter_post_down_alter_post_up'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='seen_by',
            field=models.ManyToManyField(blank=True, related_name='seend', to='accounts.profile'),
        ),
    ]
