from django.db import models

class Model(models.Model):
    title = models.CharField(max_length=50)
    apiName = models.CharField(max_length=50, null=True, unique=True)
    content = models.CharField(max_length=500, null=True)

class Input(models.Model):
    api_id = models.ForeignKey(Model, related_name="model", on_delete=models.CASCADE, db_column="api_id", null=True)
    tag = models.CharField(max_length=50, null=False)
    value = models.TextField(blank=False)