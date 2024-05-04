import mimetypes
import os
from re import findall

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from PIL import Image, ImageDraw
from random import randint
from django.core.files.storage import FileSystemStorage

from djangoProject import settings
from .stenography import hide_image, reveal_image

from django.urls import reverse_lazy
from django.views.generic import CreateView


# Create your views here.

@login_required(login_url="login")
def encrypt_text(request):
    if request.method == 'POST' and request.FILES.get('image') and request.POST.get('text'):
        # Получаем изображение и текст из формы
        image_file = request.FILES['image']
        text = request.POST['text']
        # Создаем объект изображения из полученного файла
        img = Image.open(image_file)
        draw = ImageDraw.Draw(img)
        width = img.size[0]
        height = img.size[1]
        pix = img.load()

        keys = []  # Список для хранения ключей

        # Шифруем текст в изображение
        for elem in ([ord(elem) for elem in text]):
            key = (randint(1, width - 10), randint(1, height - 10))
            g, b = pix[key][1:3]
            draw.point(key, (elem, g, b))
            keys.append(key)

        # Сохраняем зашифрованное изображение
        encrypted_image_path = os.path.join('media', 'encrypted_image.png')
        img.save(encrypted_image_path)

        # Сохраняем ключи в текстовом файле
        keys_file_path = os.path.join('media', 'keys.txt')
        with open(keys_file_path, 'w') as keys_file:
            keys_file.write('\n'.join(map(str, keys)))

        # Формируем ссылки для скачивания файлов
        image_url = os.path.join('/media/', 'encrypted_image.png')
        keys_url = os.path.join('/media/', 'keys.txt')

        # Определяем MIME-типы файлов
        image_mime_type, _ = mimetypes.guess_type(image_url)
        keys_mime_type, _ = mimetypes.guess_type(keys_url)

        # Возвращаем ссылки на скачивание файлов с указанием MIME-типов
        return render(request, 'encrypted_success.html', {
            'image_url': image_url,
            'keys_url': keys_url,
            'image_mime_type': image_mime_type,
            'keys_mime_type': keys_mime_type,
        })
    else:
        # Возвращаем ошибку, если форма не была отправлена или данные некорректны
        return render(request, 'index.html')


@login_required(login_url="login")
def decrypt_text(request):
    decrypted_text = None

    if request.method == 'POST' and request.FILES.get('image') and request.FILES.get('key'):
        # Получаем изображение и ключ из формы
        image_file = request.FILES['image']
        key_file = request.FILES['key']

        # Открываем изображение
        img = Image.open(image_file)
        pix = img.load()

        # Читаем ключ из файла
        keys_content = key_file.read().decode('utf-8')

        # Извлекаем координаты из ключа
        keys = [(int(match[0]), int(match[1])) for match in findall(r'\((\d+), (\d+)\)', keys_content)]

        # Расшифровываем текст из изображения
        decrypted_text = decrypt_text_from_image(pix, keys)

    return render(request, 'decrypt.html', {'decrypted_text': decrypted_text})


def decrypt_text_from_image(pix, keys):
    decrypted_text = []
    for key in keys:
        decrypted_text.append(pix[key][0])
    return ''.join([chr(elem) for elem in decrypted_text])


@login_required(login_url="login")
def about(request):
    return render(request, 'about.html')


@login_required(login_url="login")
def contact(request):
    return render(request, 'contact.html')


@login_required(login_url="login")
def profile(request):
    return render(request, 'profile.html')


class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login') # После успешной регистрации перенаправить на страницу входа
    template_name = 'registration/signup.html'


class CustomLoginView(LoginView):
    success_url = reverse_lazy('encrypt_text')
    next_page = reverse_lazy('encrypt_text')
    template_name = 'registration/login.html'


class CustomLogoutView(LogoutView):
    success_url = reverse_lazy('encrypt_text')
    template_name = 'registration/logout.html'


def encrypt_image(request):
    if request.method == 'POST' and request.FILES['image_to_hide'] and request.FILES['cover_image']:
        # Получаем загруженные файлы
        image_to_hide = request.FILES['image_to_hide']
        cover_image = request.FILES['cover_image']

        # Сохраняем файлы на сервере
        fs = FileSystemStorage()
        image_to_hide_path = fs.save(image_to_hide.name, image_to_hide)
        cover_image_path = fs.save(cover_image.name, cover_image)

        # Путь для сохранения скрытого изображения
        output_path = settings.MEDIA_ROOT + '/hidden_image.jpg'

        # Скрыть изображение
        hide_image(settings.MEDIA_ROOT + '/' + image_to_hide_path,
                   settings.MEDIA_ROOT + '/' + cover_image_path,
                   output_path)

        # Отправляем скрытое изображение пользователю
        return render(request, 'encrypt_result.html', {'encrypted_image': output_path})

    return render(request, 'encrypt_image.html')

def decrypt_image(request):
    decrypted_image = None

    if request.method == 'POST' and request.FILES['hidden_image']:
        # Получаем загруженное скрытое изображение
        hidden_image = request.FILES['hidden_image']

        # Сохраняем файл на сервере
        fs = FileSystemStorage()
        hidden_image_path = fs.save(hidden_image.name, hidden_image)

        # Путь для сохранения расшифрованного изображения
        output_path = settings.MEDIA_ROOT + '/revealed_image.jpg'

        # Раскрыть скрытое изображение
        reveal_image(settings.MEDIA_ROOT + '/' + hidden_image_path, output_path)

        # Отправляем раскрытое изображение пользователю
        decrypted_image = output_path

    return render(request, 'decrypt_image.html', {'decrypted_image': decrypted_image})