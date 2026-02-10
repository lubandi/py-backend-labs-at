from django.db import migrations


def create_default_tags(apps, schema_editor):
    Tag = apps.get_model("shortener", "Tag")
    default_tags = ["Marketing", "Social", "Newsletter", "Personal", "Work"]

    for tag_name in default_tags:
        Tag.objects.get_or_create(name=tag_name)


class Migration(migrations.Migration):
    dependencies = [
        (
            "shortener",
            "0002_tag_url_click_count_url_custom_alias_url_description_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(create_default_tags),
    ]
