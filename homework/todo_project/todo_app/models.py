from django.db import models

# Create your models here.


class TodoItem(models.Model):
    title = models.CharField(max_length=200, null=False)
    details = models.TextField(null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title
