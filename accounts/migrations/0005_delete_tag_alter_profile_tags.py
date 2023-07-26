# Generated by Django 4.2.2 on 2023-07-01 17:43

import accounts.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        ('accounts', '0004_alter_profile_tags'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Tag',
        ),
        migrations.AlterField(
            model_name='profile',
            name='tags',
            field=accounts.models.TaggedProfileManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
