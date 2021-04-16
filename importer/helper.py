import csv
import os
import re
from django.core.files.storage import default_storage

ROOT_DIR = os.path.join(os.path.dirname(__file__), '../planilhas/')


def save_file(file, filename):
    default_storage.save(ROOT_DIR + filename, file)


def upload_file(file, filename):
    with open(ROOT_DIR + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return filename


def get_file(filename):
    return open(ROOT_DIR + filename, 'r', encoding='utf-8')


def remove_file(filename):
    if filename and filename != '':
        os.remove(ROOT_DIR + filename)


def create_file(filename):
    file = open(ROOT_DIR + filename, 'w')
    return file


def write_file(filename, rows):
    file = create_file(filename)
    writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
    for row in rows:
        writer.writerow(row)


def format_text_value(text):
    if text is None or text == '':
        return text
    text = text.lower()
    text = text.replace('ç', 'c')
    text = text.replace('ã', 'a')
    text = text.replace('õ', 'o')
    text = text.replace('á', 'a')
    text = text.replace('é', 'e')
    text = text.replace('í', 'i')
    text = text.replace('ó', 'o')
    text = text.replace('ú', 'u')
    text = text.replace('à', 'a')
    text = text.replace('â', 'a')
    text = text.replace('ê', 'e')
    text = text.replace('î', 'i')
    text = text.replace('ô', 'o')
    text = text.replace('û', 'u')
    text = text.replace('ü', 'u')
    return text


# Gera o "slug" a partir do título e código do pedido
def get_slug(title, codigo):
    if title is None:
        title = ''
    size = len(title) if len(title) <= 50 else 50
    slug = ''
    if size > 0:
        slug = title[:size]
        slug = format_text_value(slug)
        slug = slug.replace(' ', '-')
        slug = '{}-{}'.format(slug, codigo)
    else:
        slug = str(codigo)
    return slug


# Substitui as preposições de/do/da por 'd%' que pode ser qualquer uma delas. Isso é
# usado somente nas buscas e permite desconsiderar erros de gênero dessas preposições.
def add_placeholder(text):
    text = format_text_value(text)
    if re.search('\sd[a-z]\s', text):
        text = re.sub('\sd[a-z]\s', ' d% ', text)

    return text
