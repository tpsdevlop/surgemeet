from djongo import models



class UserToken(models.Model):
    userEmail = models.EmailField(max_length=254,primary_key=True)
    token = models.JSONField()

    def __str__(self) -> str:
        return self.userEmail
