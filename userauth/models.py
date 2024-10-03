from djongo import models
from django.utils import timezone
class UserDetails(models.Model):
    userID = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    category = models.CharField(max_length=100,default="")
    expiry_date = models.DateField()
    status = models.CharField(max_length=50)
    register_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.userID
class UserLogin(models.Model):
    email = models.EmailField(unique=True)
    token = models.JSONField()

    @classmethod
    def save_or_update(cls, email, token_data):
        """
        Creates a new UserLogin object or updates the existing one with the same email.
        
        :param email: The email address of the user
        :param token_data: The JSON data to store in the token field
        :return: The created or updated UserLogin object
        """
        user_login, created = cls.objects.update_or_create(
            email=email,
            defaults={'token': token_data}
        )
        return user_login
    def __str__(self):
        return self.email
    
class UserActivity(models.Model):
    user = models.OneToOneField(UserDetails, on_delete=models.CASCADE)  # Updated to use your own UserDetails model
    last_activity = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.email} last active at {self.last_activity}'
    


