from django.db import models
from django.contrib.auth.models import User  # для создания привязки списка задач к конкретным пользователям

class Todo(models.Model):
    title = models.CharField(max_length=100)  # в заголовках небольше 200символов
    memo = models.TextField(blank=True)  # описание, blank=True - заполнение поля необязательное
    created = models.DateTimeField(auto_now=True)  # отображается не только дата, но и время
    # auto_now=True - атрибут присваивается автоматически

    datecompleted = models.DateTimeField(null=True, blank=True)
    # blank - поле для текста, null - поле для цифр

    important = models.BooleanField(default=False)  # важность задачи, по умолчанию не важная задача

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # модель внешний ключ между записью и пользователем, который ее создал

    #image = models.ImageField(upload_to="blog/images/")
    #url = models.URLField(blank=True)  # открываем страницу (сылку) на новой вкладке браузера
    def __str__(self):  # функция в отображении панели админа возращает не номера проектов, а заголовок проекта
        return self.title

