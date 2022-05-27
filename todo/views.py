from django.shortcuts import render, redirect, get_object_or_404
# redirect - для перенаправления зарегистрированного пользователя, get_object_or_404 - для нахождения записи по ключу
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm  # импорт шаблонов форм для регистрации юзеров,
# AuthenticationForm - для login входа по созданному аккаунту
from django.contrib.auth.models import User  # модель пользователя
from django.db import IntegrityError  # импортируем ошибку для ее отладки
from  django.contrib.auth import login, logout, authenticate  # после того как юзер зашел в сой кабинет, то перенаправляем его на свою страницу
# logout - для выхода из аккаунта, authenticate - проверка логина и пароля при входе пользователя
from .forms import TodoForm  # импортируем нашу форму для страницы создания задач пользователя createtodo
from .models import Todo  # импортируем модель туду
from django.utils import timezone  # для подстановки времени завершения задачи
from django.contrib.auth.decorators import login_required  # только зарегистрированные пользователи имеют доступ к определенным страницам

def home(request):
    return render(request, 'todo/home.html')

def signupuser(request):
    # готовые шаблоны
    # метод Get отображается в сылке -->
    # метод POST скрывает данные и использует на текущей странице
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            # Create a new user (create_user() - всстроенная функция джанго)
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')  # перенаправление на url currenttodos
            except IntegrityError:
                return render(request, 'todo/signupuser.html',
                              {'form': UserCreationForm(), 'error': 'That username has already been taken. Please choose a new username'})
        else:
            # Сообщить пользователю о несоответствии пароля
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Passwords did not match'})

def loginuser(request):
    # готовые шаблоны
    # метод Get отображается в сылке -->
    # метод POST скрывает данные и использует на текущей странице
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:  # если данный пользователь не зарегистрирован, или пароль не подходит, то пользователь не существует
            # возвращаем повторно на страницу входа
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': 'Username and password did not match'})
        else:  # если удалось зайти в аккаунт
            login(request, user)
            return redirect('currenttodos')  # перенаправление на url currenttodos

@login_required
def logoutuser(request):
    # что бы автоматически не выполнялся выход из аккаунта (многие браузеры прогружают все сылки на странице)
    # выполняем проверку на принадлежность к POST
    if request.method == "POST":
        logout(request)
        return redirect('home')

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': TodoForm()})
    else:
        try:
            # выполняется если пользователь внес какую-то информацию в окно и нажал кнопку Create (Создать)
            form =TodoForm(request.POST)  # соединить внесенную информацию с нашей формой
            newtodo = form.save(commit=False)  # даная форму сохраняет информацию в базу данных
            # делаем привязку созданной записи к конкрутному пользователю
            newtodo.user = request.user
            newtodo.save()  # сохранит привязку в БД
            return redirect('currenttodos')  # перенаправить пользователя на список записей
        except ValueError:
            # если вводимое название задачи "title" больше 100 символов, то возникает ошибка и мы ее обрабатываем
            return render(request, 'todo/createtodo.html', {'form': TodoForm(), 'error': 'Bad data passed in. Try again'})
            # переданы неверные данные. попробуйте еще раз

# функция отображения всех созданых пользователем дел или задач
@login_required
def currenttodos(request):
    #todos =Todo000.objects.all()  # пользователь видит все записи созданные всеми пользователями
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    # проверка соответствия записи к конкретному пользователю
    # datecompleted__isnull=True - проверка поля, что оно пустое

    return render(request, 'todo/currenttodos.html', {'todos': todos})

@login_required
def completedtodos(request):
    #todos =Todo000.objects.all()  # пользователь видит все записи созданные всеми пользователями
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('datecompleted')
    # проверка соответствия записи к конкретному пользователю
    # datecompleted__isnull=True - проверка поля, что оно пустое или не пустое
    # order_by('-datecompleted') - сортировка по дате выполнения (- переде dateco... обознач-т обратный хронолог-й порядок)
    return render(request, 'todo/completedtodos.html', {'todos': todos})

@login_required
def viewtodo(request, todo_pk):
    # условие по которому находить будем нужную нам запись по ее ключу
    # user=request.user система сверяет автора,
    # если запись будет пренадлежать не текущему пользователю, то выскочить ошибка 404
    todo =get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'GET':
        #для редактирования уже имеющийся заметки, записи
        form = TodoForm(instance=todo)  # instance=1todo - уточняем, что изменяем уже существующий объект
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else: # для сохранения отредактированой записи (заметки)
        try:
            form = TodoForm(request.POST, instance=todo)
            # соединить внесенную информацию с нашей формой, instance=1todo - уточняем, что изменяем уже существующий объект
            form.save()
            return redirect('currenttodos')  # перенаправить пользователя на список записей
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form, 'error': 'Bad info'})

@login_required
def completetodo(request, todo_pk):  # завершать задачу может только тот пользователь, к-ый создавал ее
    todo =get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        # присвоем текущее время, а если в этом поле появляется время, то значит задача становится выполненой

        todo.save()
        return redirect('currenttodos')  # перенаправить пользователя на список записей

@login_required
def deletetodo(request, todo_pk):  # удалить задачу может только тот пользователь, к-ый создавал ее
    todo =get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')  # перенаправить пользователя на список записей
