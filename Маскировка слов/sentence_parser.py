import os
import re
import xml.etree.ElementTree as ET
from tqdm import tqdm

# Конфигурация
OUTPUT_FILE = "all_sentences.txt"
MIN_LENGTH = 15  # Минимальная длина предложения в символах

def get_sentences_from_xml(path):
    """Парсинг OpenCorpora XML"""
    print(f"Парсинг XML: {path}")
    try:
        # iterparse эффективен по памяти
        context = ET.iterparse(path, events=("end",))
        for event, elem in context:
            if elem.tag == 'source' and elem.text:
                text = elem.text.strip()
                if len(text) >= MIN_LENGTH:
                    yield text
                elem.clear()
    except Exception as e:
        print(f"Ошибка чтения XML {path}: {e}")

def get_sentences_from_txt(path):
    """Парсинг текстового файла с разбивкой на предложения"""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            # Простая разбивка по знакам препинания
            # (?<=[.!?]) - lookbehind, чтобы оставить знак препинания в предложении
            sentences = re.split(r'(?<=[.!?])\s+', text)
            for s in sentences:
                s = s.strip()
                # Убираем переносы строк внутри предложения
                s = s.replace('\n', ' ')
                if len(s) >= MIN_LENGTH:
                    yield s
    except Exception as e:
        print(f"Ошибка чтения TXT {path}: {e}")

def scan_directory(path):
    """Рекурсивный обход папки"""
    print(f"Сканирование папки: {path}")
    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.txt'):
                yield from get_sentences_from_txt(file_path)
            elif file.endswith('.xml'):
                yield from get_sentences_from_xml(file_path)

def main():
    # Список источников
    sources = [
        "Маскировка слов/RussianNovels-master/corpus",
        "Маскировка слов/annot.opcorpora.xml",
        "annot.opcorpora.xml",
        "Предобработка текста/История названия ТГУ.txt"
    ]

    print(f"Начинаем сбор предложений в файл {OUTPUT_FILE}...")
    
    count = 0
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        for source in sources:
            if not os.path.exists(source):
                continue
                
            generator = None
            if os.path.isdir(source):
                generator = scan_directory(source)
            elif source.endswith('.xml'):
                generator = get_sentences_from_xml(source)
            else:
                generator = get_sentences_from_txt(source)
            
            for sentence in generator:
                out.write(sentence + '\n')
                count += 1
                if count % 10000 == 0:
                    print(f"Обработано {count} предложений...", end='\r')

    print(f"\nГотово! Всего сохранено {count} предложений в '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()
