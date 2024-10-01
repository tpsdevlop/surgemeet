from django.db import models

class Branch(models.Model):
    id = models.AutoField(primary_key=True)
    branchname = models.CharField(max_length=100)

    def __str__(self):
        return self.branchname
