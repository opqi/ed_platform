from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from .models import Product, Group, Lesson
from users.models import CustomUser
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated  
from .serializers import ProductSerializer, LessonSerializer


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny] 

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        return render(request, 'products.html', {'data': data})


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        product_id = self.kwargs['product_id']
        product = get_object_or_404(Product, id=product_id)
        if product.has_user_access(request.user):
            lessons = Lesson.objects.filter(product_id=product_id)
            return render(request, 'lessons.html', {'lessons': lessons})
        else:
            return render(request, 'lessons.html', {'lessons': []})


def distribute_users_to_groups(product):
    # Получаем список всех активных учеников
    students = CustomUser.objects.filter(is_student=True, is_active=True)
    total_students = students.count()
    
    # Получаем количество групп и минимальное/максимальное количество участников в каждой группе
    num_groups = product.groups.count()
    min_users_in_group = product.min_users_in_group
    max_users_in_group = product.max_users_in_group
    
    # Распределяем участников по группам с учетом минимальных и максимальных значений
    group_index = 0
    for i, student in enumerate(students):
        # Определяем текущую группу для участника
        group = product.groups.all()[group_index]
        
        # Добавляем участника в текущую группу
        group.students.add(student)
        
        # Проверяем, не превышено ли максимальное количество участников в текущей группе
        if group.students.count() >= max_users_in_group:
            # Переходим к следующей группе
            group_index = (group_index + 1) % num_groups
        
        # Если еще есть участники и текущая группа заполнена на максимум,
        # и количество участников в текущей и следующей группах отличается больше, чем на 1,
        # то перераспределяем участника
        while i < total_students - 1 and group.students.count() == max_users_in_group \
                and abs(group.students.count() - product.groups.all()[(group_index + 1) % num_groups].students.count()) > 1:
            # Удаляем участника из текущей группы
            group.students.remove(student)
            
            # Переходим к следующей группе
            group_index = (group_index + 1) % num_groups
            group = product.groups.all()[group_index]
            
            # Добавляем участника в следующую группу
            group.students.add(student)


def access_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    if not request.user.is_authenticated or not product.has_access(request.user):
        return redirect('login')  # Перенаправление на страницу входа для не аутентифицированных пользователей или пользователей без доступа к продукту
    
    # Проверяем, начался ли продукт
    if product.start_datetime > timezone.now():
        # Продукт еще не начался
        # Перераспределение участников по группам
        distribute_users_to_groups(product)
    else:
        # Продукт уже начался
        # Создание группы для пользователя
        create_group_for_user(product, request.user)
    
    return render(request, 'access_product.html', {'product': product})


def create_group_for_user(product, user):
    # Создаем новую группу для пользователя и добавляем его в нее
    group = Group.objects.create(product=product, name=f"Group for {user.username}")
    group.students.add(user)
