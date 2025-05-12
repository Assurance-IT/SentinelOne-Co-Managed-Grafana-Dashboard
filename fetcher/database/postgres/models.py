from tortoise import fields
from tortoise.models import Model

class Integration(Model):
    name = fields.CharField(max_length=50)
    status = fields.BooleanField()