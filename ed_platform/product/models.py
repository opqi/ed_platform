from django.db import models
from users.models import CustomUser

class Product(models.Model):
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_products')
    name = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    min_users_in_group = models.PositiveIntegerField()
    max_users_in_group = models.PositiveIntegerField()

    def has_user_access(self, user):
        return user == self.creator or \
               user.groups.filter(name=self).exists() or \
               user in self.groups.all()

    def is_active(self):
        return self.start_datetime > timezone.now()

    def __str__(self):
        return self.name

class Lesson(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='lessons')
    name = models.CharField(max_length=100)
    video_link = models.URLField()

    def __str__(self):
        return self.name

class Group(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='groups')
    students = models.ManyToManyField(CustomUser)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name