# Generated by Django 5.1.3 on 2025-01-03 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_alter_customuser_table"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bookmark",
            old_name="bookmark_id",
            new_name="bookmark",
        ),
        migrations.RenameField(
            model_name="bookmark",
            old_name="profile_id",
            new_name="profile",
        ),
        migrations.RenameField(
            model_name="bookmarklist",
            old_name="bookmark_id",
            new_name="bookmark",
        ),
        migrations.RenameField(
            model_name="bookmarklist",
            old_name="place_id",
            new_name="place",
        ),
        migrations.RenameField(
            model_name="settings",
            old_name="country_id",
            new_name="country",
        ),
        migrations.RenameField(
            model_name="settings",
            old_name="profile_id",
            new_name="profile",
        ),
    ]