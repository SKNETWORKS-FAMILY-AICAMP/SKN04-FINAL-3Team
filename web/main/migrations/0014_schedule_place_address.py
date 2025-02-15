# Generated by Django 5.1.4 on 2025-01-16 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_alter_chatting_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('schedule_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('json_data', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'schedule',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='place',
            name='address',
            field=models.CharField(default='', max_length=40),
            preserve_default=False,
        ),
    ]
