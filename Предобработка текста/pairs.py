import pymorphy3
import re


def find_agreeing_pairs(text):
    morph = pymorphy3.MorphAnalyzer()
    tokens = re.findall(r'[а-яА-ЯёЁ]+', text)
    result = []
    
    for i in range(len(tokens) - 1):
        parses1 = morph.parse(tokens[i])
        parses2 = morph.parse(tokens[i + 1])
        
        found_pair = None
        best_score = 0
        
        for p1 in parses1:
            for p2 in parses2:
                tag1, tag2 = str(p1.tag), str(p2.tag)
                
                # Пропускаем аббревиатуры + избавляемся от предлогов
                if 'Abbr' in tag1 or 'Abbr' in tag2:
                    continue
                
                is_adj_noun = 'ADJF' in tag1 and 'NOUN' in tag2
                is_noun_adj = 'NOUN' in tag1 and 'ADJF' in tag2
                if not (is_adj_noun or is_noun_adj):
                    continue
                
                # согласование по числу
                if 'sing' in tag1 and 'sing' not in tag2:
                    continue
                if 'plur' in tag1 and 'plur' not in tag2:
                    continue
                
                # согласование по роду
                if 'sing' in tag1: # только для ед числа
                    genders = ['masc', 'femn', 'neut']
                    gender_match = any(g in tag1 and g in tag2 for g in genders)
                    if not gender_match:
                        continue
                
                # согласование по падежу
                cases = ['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct']
                case_match = any(c in tag1 and c in tag2 for c in cases)
                if not case_match:
                    continue
                
                # Выбираем пару 
                score = p1.score + p2.score
                if score > best_score:
                    best_score = score
                    
                    # определяем тип слова 
                    if 'ADJF' in tag1:
                        adj_parse, noun_parse = p1, p2
                        adj_tag, noun_tag = tag1, tag2
                    else:
                        adj_parse, noun_parse = p2, p1
                        adj_tag, noun_tag = tag2, tag1
                    
                    # прилагательное к роду существительного
                    gender = next((g for g in ['masc', 'femn', 'neut'] if g in noun_tag), 'masc')
                    inflected = adj_parse.inflect({gender, 'sing', 'nomn'})
                    adj_lemma = inflected.word if inflected else adj_parse.normal_form
                    noun_lemma = noun_parse.normal_form
                    
                    # сохраним порядок
                    if 'ADJF' in tag1:
                        found_pair = (adj_lemma, noun_lemma)
                    else:
                        found_pair = (noun_lemma, adj_lemma)
        
        if found_pair:
            result.append(found_pair)
    
    return result


def main():
    with open('История названия ТГУ.txt', encoding='utf-8') as f:
        text = f.read()
    
    pairs = find_agreeing_pairs(text)
    
    print("Пары (прилагательное + существительное), согласованные по роду, числу и падежу:")
    print("-" * 5)
    for adj, noun in pairs:
        print(f"{adj} {noun}")


if __name__ == '__main__':
    main()

"""
Вывод: 
Пары (прилагательное + существительное), согласованные по роду, числу и падежу:
------------------------------------------------------------
государственный совет
российская империя
императорский университет
министерство народное
народное просвещение
томский университет
исполнительный комитет
томский университет
президиум верховный
верховный совет
государственный университет
трудовой красный
красное знамя
президиум верховный
верховный совет
государственный университет
октябрьская революция
большая заслуга
высококвалифицированный специалист
народное хозяйство
российская федерация
государственный университет
государственный свод
ценный объект
культурное наследие
российская федерация
государственный университет
государственный реестр
образовательное учреждение
профессиональное образование
государственный университет
российская федерация
образовательное учреждение
профессиональное образование
государственный университет
исследовательский институт
прикладная математика
исследовательский институт
экономическая проблема
исследовательский институт
сибирский физико
физико технический
технический институт
российская федерация
образовательное учреждение
учреждение высочайшее
профессиональное образование
государственный университет
исследовательский университет
наука российская
российская федерация
образовательное учреждение
профессиональное образование
государственный университет
образовательное учреждение
профессиональное образование
государственный университет
наука российская
российская федерация
тип существующий
образовательное учреждение
учреждение высочайшее
профессиональное образование
государственный университет
образовательное учреждение
высочайшее образование
государственный университет
"""