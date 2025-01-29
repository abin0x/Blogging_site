# Generated by Django 5.0.8 on 2025-01-29 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_blogsubmission'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('youtube_url', models.URLField()),
                ('thumbnail', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('media_type', models.CharField(choices=[('audio', 'Audio'), ('video', 'Video')], max_length=10)),
            ],
        ),
    ]
