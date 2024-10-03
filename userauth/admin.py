from django.contrib import admin
from .models import UserDetails,UserLogin
from django.utils import timezone
# Register your models here.
@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('userID', 'email', 'expiry_date', 'status', 'register_date')
    search_fields = ('userID', 'email')
    list_filter = ('status', 'expiry_date')

@admin.register(UserLogin)
class UserLoginAdmin(admin.ModelAdmin):
    list_display=('email','token')
