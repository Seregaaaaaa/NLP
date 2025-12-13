import torch, sys, os, re, xml.etree.ElementTree as ET
from transformers import BertTokenizer, BertForMaskedLM

"""
Я скачал корпуса текстов из https://github.com/JoannaBy/RussianNovels и https://opencorpora.org/?page=downloads, распарсил их и получил почти 600 000 предложений.
Для каждого из двух заданных слов, я ищу данное слово в тексте, ставлю на его место в предложении маску и проверяю попадет ли первое и второе заданное слово в топ 10.
"""

def get_predictions(text, tokenizer, model, k=10):
    inputs = tokenizer(text, return_tensors='pt')
    mask_idx = torch.where(inputs.input_ids == tokenizer.mask_token_id)[1]
    if len(mask_idx) == 0: return []
    
    logits = model(**inputs).logits[0, mask_idx, :]
    top_ids = torch.topk(logits, k, dim=1).indices[0].tolist()
    return [tokenizer.decode([i]).strip() for i in top_ids]

def get_sentences(path):
    print(f"Чтение подготовленного корпуса: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.strip()

def search_context(w1, w2, corpus_path):
    print("Загрузка модели...")
    tokenizer = BertTokenizer.from_pretrained('DeepPavlov/rubert-base-cased')
    model = BertForMaskedLM.from_pretrained('DeepPavlov/rubert-base-cased')
    

    with open(corpus_path, 'r', encoding='utf-8') as f:
        total_sentences = sum(1 for _ in f)

    print(f"Всего предложений: {total_sentences}")

    for target, probe in [(w1, w2), (w2, w1)]:
        print(f"\n--- Ищем '{target}', маскируем, ждем '{probe}' ---")
        pattern = re.compile(r'\b' + re.escape(target) + r'\b', re.IGNORECASE)
        
        found_count = 0
        # Пересоздаем генератор для каждого прохода, так как файл читается потоково
        sentences = get_sentences(corpus_path)
        
        for i, sent in enumerate(sentences):
            if i % 5000 == 0 and total_sentences > 0:
                print(f"Прогресс: {i/total_sentences*100:.1f}%", end='\r')
                
            if pattern.search(sent):
                found_count += 1
                masked = pattern.sub('[MASK]', sent, count=1)
                preds = get_predictions(masked, tokenizer, model)
                
                if probe in preds and target in preds:
                    print(f"\nНАЙДЕНО: {sent}\nМАСКА: {masked}\nТОП: {preds}")
                    return
        
        print(f"\nЗавершено. Слово '{target}' встретилось {found_count} раз, но контекст не подошел")

if __name__ == "__main__":
    w1, w2 = (sys.argv[1:3] if len(sys.argv) > 2 else ("дом", "здание"))
    
    corpus = "Маскировка слов/all_sentences.txt"
    search_context(w1, w2, corpus)

"""
Примеры работы:

%python "mask.py" мяч камень
Загрузка модели...
Всего предложений: 598863

--- Ищем 'мяч', маскируем, ждем 'камень' ---
Чтение подготовленного корпуса: all_sentences.txt
Прогресс: 10.0%
НАЙДЕНО: Любая попытка вернуть его неизменно выставляла противника забавным мазилой, потому что ни подцепить низко несущийся мяч, ни тем более толком ударить по нему было невозможно.
МАСКА: Любая попытка вернуть его неизменно выставляла противника забавным мазилой, потому что ни подцепить низко несущийся [MASK], ни тем более толком ударить по нему было невозможно.
ТОП: ['камень', 'мяч', 'меч', 'снаряд', 'предмет', 'груз', 'объект', 'конь', 'шар', 'корабль']

---------------------------

%python "mask.py" остался идёт
Загрузка модели...
Всего предложений: 598863

--- Ищем 'остался', маскируем, ждем 'идёт' ---
Чтение подготовленного корпуса: all_sentences.txt
Прогресс: 79.3%
НАЙДЕНО: Роман Иванович остался обедать.
МАСКА: Роман Иванович [MASK] обедать.
ТОП: ['продолжает', 'уходит', 'отправился', 'отправляется', 'отказывается', 'идёт', 'начинает', 'пришёл', 'остался', 'начал']


"""