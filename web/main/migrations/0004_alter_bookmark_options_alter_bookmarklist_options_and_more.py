# Generated by Django 5.1.3 on 2025-01-03 07:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_alter_country_options_bookmark_created_at_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="bookmark",
            options={"managed": True},
        ),
        migrations.AlterModelOptions(
            name="bookmarklist",
            options={"managed": True},
        ),
        migrations.AlterModelOptions(
            name="chatting",
            options={"managed": True},
        ),
        migrations.AlterModelOptions(
            name="settings",
            options={"managed": True},
        ),
        migrations.AlterModelTable(
            name="bookmark",
            table="bookmark",
        ),
        migrations.AlterModelTable(
            name="bookmarklist",
            table="bookmarklist",
        ),
        migrations.AlterModelTable(
            name="chatting",
            table="chatting",
        ),
        migrations.AlterModelTable(
            name="settings",
            table="settings",
        ),
    ]