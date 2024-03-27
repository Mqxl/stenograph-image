import zipfile
from io import BytesIO
from random import randint
from re import findall

from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, ImageDraw
from random import randint
from io import BytesIO

# Create your views here.


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

        # Сохраняем ключи в текстовом файле
        keys_text = '\n'.join(map(str, keys))

        # Создаем архив
        output_zip = BytesIO()
        with zipfile.ZipFile(output_zip, 'w') as zip_file:
            # Добавляем изображение
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            zip_file.writestr('encrypted_image.png', img_bytes.getvalue())

            # Добавляем текстовый файл
            zip_file.writestr('keys.txt', keys_text)

        # Перематываем архив для отправки
        output_zip.seek(0)

        # Отправляем архив клиенту
        response = HttpResponse(output_zip, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="encrypted_data.zip"'

        return response
    else:
        # Возвращаем ошибку, если форма не была отправлена или данные некорректны
        return render(request, 'index.html')


def decrypt_text(request):
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

        # Возвращаем расшифрованный текст
        return HttpResponse(decrypted_text)
    else:
        return render(request, 'decrypt.html')


def decrypt_text_from_image(pix, keys):
    decrypted_text = []
    for key in keys:
        decrypted_text.append(pix[key][0])
    return ''.join([chr(elem) for elem in decrypted_text])


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')
