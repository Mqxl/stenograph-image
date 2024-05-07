import cv2
import numpy as np
from scipy.stats import chisquare

# def hide_image(image_to_hide_path, cover_image_path, output_path, alpha=0.04):
#     # Открываем изображения
#     image_to_hide = Image.open(image_to_hide_path)
#     cover_image = Image.open(cover_image_path)
#
#     # Проверяем, что размеры изображений совпадают
#     if image_to_hide.size != cover_image.size:
#         # Если размеры не совпадают, изменяем размер изображения для скрытия до размеров обложки
#         image_to_hide = image_to_hide.resize(cover_image.size)
#
#     # Конвертируем изображения в режим RGBA
#     image_to_hide = image_to_hide.convert("RGBA")
#     cover_image = cover_image.convert("RGBA")
#
#     # Создаем новое изображение для скрытого изображения
#     new_image = Image.new("RGBA", cover_image.size)
#
#     # Проходим через каждый пиксель и скрываем его
#     for x in range(cover_image.width):
#         for y in range(cover_image.height):
#             # Получаем RGBA-значения из пикселей скрываемого и основного изображения
#             pixel_hide = image_to_hide.getpixel((x, y))
#             pixel_cover = cover_image.getpixel((x, y))
#
#             # Создаем новый пиксель с использованием альфа-канала
#             new_pixel = (
#                 int(pixel_cover[0] * (1 - alpha) + pixel_hide[0] * alpha),
#                 int(pixel_cover[1] * (1 - alpha) + pixel_hide[1] * alpha),
#                 int(pixel_cover[2] * (1 - alpha) + pixel_hide[2] * alpha),
#                 pixel_cover[3]  # используем альфа-канал из cover_image
#             )
#
#             # Устанавливаем новый пиксель на новом изображении
#             new_image.putpixel((x, y), new_pixel)
#
#     # Сохраняем новое изображение
#     new_image.save(output_path, format="PNG")


# def reveal_image(hidden_image):
#     # Открываем скрытое изображение
#     hidden_image = Image.open(hidden_image)
#
#     # Создаем оригинальное изображение (белое)
#     original_image = Image.new("RGB", hidden_image.size, color="white")
#
#     # Создаем новое изображение для извлеченного скрытого изображения
#     extracted_image = Image.new("RGB", hidden_image.size)
#
#     # Проходим по каждому пикселю
#     for x in range(hidden_image.width):
#         for y in range(hidden_image.height):
#             # Получаем RGB-значения для пикселей скрытого и оригинального изображений
#             pixel_hidden = hidden_image.getpixel((x, y))
#             pixel_original = original_image.getpixel((x, y))
#
#             # Проверяем младшие биты RGB компонентов
#             if (pixel_hidden[0] & 1) != (pixel_original[0] & 1) or \
#                     (pixel_hidden[1] & 1) != (pixel_original[1] & 1) or \
#                     (pixel_hidden[2] & 1) != (pixel_original[2] & 1):
#                 # Если есть различия, считаем пиксель скрытым
#                 extracted_image.putpixel((x, y), (0, 0, 0))
#             else:
#                 # Иначе считаем пиксель оригинальным
#                 extracted_image.putpixel((x, y), (255, 255, 255))
#
#     return extracted_image

def hide_image(container_image_path, secret_image_path, output_image_path):
    # Load container and secret images
    container_image = cv2.imread(container_image_path)
    secret_image = cv2.imread(secret_image_path, cv2.IMREAD_GRAYSCALE)

    # Resize secret image to fit container
    secret_image = cv2.resize(secret_image, (container_image.shape[1], container_image.shape[0]))

    # Convert secret image to binary
    _, secret_image_binary = cv2.threshold(secret_image, 128, 255, cv2.THRESH_BINARY)

    # Hide secret image in container
    for i in range(container_image.shape[0]):
        for j in range(container_image.shape[1]):
            for k in range(3):  # For each color channel
                if i < secret_image.shape[0] and j < secret_image.shape[1]:
                    container_image[i][j][k] = container_image[i][j][k] & 0xFE | secret_image_binary[i][j] >> 7

    # Save the resulting image
    cv2.imwrite(output_image_path, container_image)


def extract_hidden_image(container_image_path, output_image_path):
    # Load container image
    container_image = cv2.imread(container_image_path)

    # Initialize an empty image to extract the hidden image
    extracted_image = np.zeros((container_image.shape[0], container_image.shape[1]), dtype=np.uint8)

    # Extract the hidden image from the container
    for i in range(container_image.shape[0]):
        for j in range(container_image.shape[1]):
            for k in range(3):  # For each color channel
                extracted_image[i][j] = extracted_image[i][j] | ((container_image[i][j][k] & 1) << 7)

    # Save the extracted image
    cv2.imwrite(output_image_path, extracted_image)
