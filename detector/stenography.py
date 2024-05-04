from PIL import Image


def hide_image(image_to_hide_path, cover_image_path, output_path):
    # Открываем изображения
    image_to_hide = Image.open(image_to_hide_path)
    cover_image = Image.open(cover_image_path)

    # Проверяем, что размеры изображений совпадают
    if image_to_hide.size[0] > cover_image.size[0] or image_to_hide.size[1] > cover_image.size[1]:
        print("Изображение для скрытия больше, чем обложка")
        return

    # Конвертируем изображения в режим RGB
    image_to_hide = image_to_hide.convert("RGB")
    cover_image = cover_image.convert("RGB")

    # Создаем новое изображение для скрытого изображения
    new_image = Image.new("RGB", cover_image.size)

    # Проходим через каждый пиксель и скрываем его
    for x in range(cover_image.width):
        for y in range(cover_image.height):
            # Получаем RGB-значения из пикселей обеих изображений
            pixel_cover = cover_image.getpixel((x, y))
            pixel_hide = image_to_hide.getpixel((x, y))

            # Создаем новый пиксель с использованием старшей части от обложки и младшей части от скрываемого изображения
            new_pixel = (pixel_cover[0], pixel_cover[1], pixel_hide[2])

            # Устанавливаем новый пиксель на новом изображении
            new_image.putpixel((x, y), new_pixel)

    # Сохраняем новое изображение
    new_image.save(output_path)


def reveal_image(hidden_image_path, output_path):
    # Открываем скрытое изображение
    hidden_image = Image.open(hidden_image_path)

    # Создаем новое изображение для извлеченного скрытого изображения
    extracted_image = Image.new("RGB", hidden_image.size)

    # Проходим через каждый пиксель скрытого изображения
    for x in range(hidden_image.width):
        for y in range(hidden_image.height):
            # Получаем RGB-значения из пикселей скрытого изображения
            pixel_hidden = hidden_image.getpixel((x, y))

            # Создаем новый пиксель с использованием младшей части от скрытого изображения
            new_pixel = (0, 0, pixel_hidden[2])

            # Устанавливаем новый пиксель на новом изображении
            extracted_image.putpixel((x, y), new_pixel)

    # Сохраняем извлеченное изображение
    extracted_image.save(output_path)
