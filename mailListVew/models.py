from django.db import models


class spider_user(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    passwd = models.TextField()

    class Meta:
        db_table='spider_user'

class super_user(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    passwd = models.TextField()
    user_grade = models.IntegerField()
    class Meta:
        db_table='super_user'

