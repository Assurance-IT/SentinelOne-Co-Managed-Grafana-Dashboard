from tortoise import fields
from tortoise.models import Model

class Integration(Model):
    name = fields.CharField(max_length=50)
    status = fields.CharField(max_length=50)

class Threat(Model):
    created_at = fields.CharField(max_length=50)
    name = fields.CharField(max_length=50)
    verdict = fields.CharField(max_length=50)
    user = fields.CharField(max_length=50)
    sha1 = fields.CharField(max_length=50)
    virustotal = fields.CharField(max_length=200)