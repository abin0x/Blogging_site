# Generated by Django 5.0.8 on 2025-01-16 17:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_comment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogReactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reaction_type', models.CharField(choices=[('like', 'Like'), ('dislike', 'Dislike')], max_length=10)),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reactions', to='blog.blog')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('blog', 'user')},
            },
        ),
        migrations.DeleteModel(
            name='BlogReaction',
        ),
    ]
