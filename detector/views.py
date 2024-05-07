import mimetypes
import os
import tempfile
from re import findall

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import render
from PIL import Image, ImageDraw
from random import randint

from djangoProject import settings
from .stenography import hide_image, extract_hidden_image

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

@login_required(login_url="login")
def home(request):
    return render(request, 'home.html')

@login_required(login_url="login")
def encrypt_image(request):
    if request.method == 'POST':
        # Получаем изображение и текст из формы
        image_to_hide_path = request.FILES['image_to_hide']
        cover_image_path = request.FILES['cover_image']

        # Сохраняем загруженные файлы
        with open('media/image_to_hide.png', 'wb+') as destination:
            for chunk in image_to_hide_path.chunks():
                destination.write(chunk)

        with open('media/cover_image.png', 'wb+') as destination:
            for chunk in cover_image_path.chunks():
                destination.write(chunk)

        # Вызываем функцию hide_image
        hide_image('media/cover_image.png', 'media/image_to_hide.png', 'media/image_with_secret.png')

        # Формируем ссылки для скачивания файлов
        image_url = os.path.join('/media/', 'image_with_secret.png')

        # Определяем MIME-типы файлов
        image_mime_type, _ = mimetypes.guess_type(image_url)

        # Возвращаем ссылки на скачивание файлов с указанием MIME-типов
        return render(request, 'encrypt_result.html', {
            'image_url': image_url,
            'image_mime_type': image_mime_type,
        })
    else:
        # Возвращаем ошибку, если форма не была отправлена или данные некорректны
        return render(request, 'encrypt_image.html')


def decrypt_image(request):
    image_url = None
    if request.method == 'POST' and request.FILES.get('hidden_image'):
        # Получаем загруженное скрытое изображение
        hidden_image = request.FILES['hidden_image']

        # Сохраняем загруженный файл
        with open('media/hidden_image.png', 'wb+') as destination:
            for chunk in hidden_image.chunks():
                destination.write(chunk)

        # Вызываем функцию extract_hidden_image
        extract_hidden_image('media/hidden_image.png', 'media/extracted_image.png')

        # Формируем ссылку для скачивания файла
        image_url = os.path.join('/media/', 'extracted_image.png')

        # Определяем MIME-тип файла
        image_mime_type, _ = mimetypes.guess_type(image_url)

        # Отправляем раскрывшееся изображение пользователю
        return render(request, 'decrypt_image.html', {
            'decrypted_image': image_url,
            'image_mime_type': image_mime_type
        })

    return render(request, 'decrypt_image.html', {'decrypted_image': image_url})


class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'


class CustomLoginView(LoginView):
    success_url = reverse_lazy('home')
    next_page = reverse_lazy('home')
    template_name = 'registration/login.html'


class CustomLogoutView(LogoutView):
    success_url = reverse_lazy('home')
    template_name = 'registration/logout.html'
