from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'is_teacher', 'is_student')

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
