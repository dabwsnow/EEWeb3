import requests
from bs4 import BeautifulSoup
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app import models
from tqdm import tqdm
import time

# URL для каждого профиля
PRACTICE_URLS = {
    'inf02': 'https://ee-informatyk.pl/ee08-inf02/praktyka/',
    'inf03': 'https://ee-informatyk.pl/inf03-ee09/praktyka/',
    'inf04': 'https://ee-informatyk.pl/inf04/praktyka/',
}

# Маппинг профилей на модели
PRACTICE_MODELS = {
    'inf02': models.PracticeINF02,
    'inf03': models.PracticeINF03,
    'inf04': models.PracticeINF04,
}

def download_file(url, save_path):
    """Скачивает файл"""
    try:
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"      ✅ Скачано: {save_path}")
        return True
    except Exception as e:
        print(f"      ❌ Ошибка: {e}")
        return False

def parse_practice_page(base_url, profile_key):
    """Парсит страницу с практическими экзаменами"""
    print(f"\n🔍 Парсинг: {base_url}")
    
    try:
        response = requests.get(base_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Находим все года
        year_select = soup.find('select', {'name': 'rok'})
        if not year_select:
            print("  ❌ Не найден селектор года")
            return []
        
        years = [opt['value'] for opt in year_select.find_all('option') if opt['value'] != 'all']
        print(f"  📅 Найдено лет: {len(years)}")
        
        all_practices = []
        
        for year in years:
            print(f"\n  📅 Парсинг года: {year}")
            
            # Запрос с фильтром по году
            year_url = f"{base_url}?rok={year}"
            year_response = requests.get(year_url, timeout=15)
            year_soup = BeautifulSoup(year_response.text, "html.parser")
            
            # Находим все практические задания
            practice_items = year_soup.find_all('div', class_='practice-list--one')
            print(f"    📝 Найдено заданий: {len(practice_items)}")
            
            for item in practice_items:
                try:
                    # Дата (например "2025 - Styczeń")
                    date_elem = item.find('div', class_='practice-list--one--date')
                    date = date_elem.find('h3').text.strip() if date_elem else None
                    
                    # Код (например "INF.03-12-25.01-SG")
                    code_elem = item.find('div', class_='practice-list--one--id')
                    code = code_elem.find('h3').text.strip() if code_elem else None
                    
                    if not date or not code:
                        continue
                    
                    # ИСПРАВЛЕНО: Извлекаем год из кода
                    # INF.03-12-25.01-SG → берем "25" → 2025
                    # INF.04-03-23.06-SG → берем "23" → 2023
                    try:
                        parts = code.split('-')
                        if len(parts) >= 3:
                            # Берем третью часть и первые 2 символа
                            year_part = parts[2].split('.')[0]  # "25" или "23"
                            parsed_year = int(year_part)
                            
                            # Преобразуем в полный год (14-99 → 2014-2099)
                            if parsed_year >= 14:
                                parsed_year = 2000 + parsed_year
                            else:
                                # Если меньше 14, это 2000-2013 (вряд ли будет)
                                parsed_year = 2000 + parsed_year
                        else:
                            parsed_year = int(year)  # fallback
                    except Exception as e:
                        print(f"      ⚠️  Ошибка парсинга года из кода: {e}")
                        parsed_year = int(year)  # fallback
                    
                    print(f"\n    📋 {code} ({date}) - Год: {parsed_year}")
                    
                    # Находим ссылки
                    links = item.find('ul', class_='practice-list--one--links')
                    if not links:
                        continue
                    
                    arkusz_url = None
                    pliki_url = None
                    rozwiazanie_url = None
                    
                    for link in links.find_all('a'):
                        href = link.get('href', '')
                        text = link.text.strip()
                        
                        if 'Arkusz' in text and 'Rozwiązanie' not in text:
                            # Ссылка на страницу с аркушем
                            arkusz_page_url = f"https://ee-informatyk.pl{href}"
                            
                            # Заходим на страницу аркуша и ищем PDF
                            try:
                                arkusz_response = requests.get(arkusz_page_url, timeout=15)
                                arkusz_soup = BeautifulSoup(arkusz_response.text, "html.parser")
                                
                                # Ищем ссылку на PDF
                                pdf_link = arkusz_soup.find('a', href=re.compile(r'\.pdf$'))
                                if pdf_link:
                                    arkusz_url = f"https://ee-informatyk.pl{pdf_link['href']}"
                                    print(f"      📄 Arkusz PDF: {arkusz_url}")
                            except Exception as e:
                                print(f"      ❌ Ошибка парсинга аркуша: {e}")
                        
                        elif 'Pobierz Pliki' in text:
                            pliki_url = f"https://ee-informatyk.pl{href}"
                            print(f"      📦 Pliki: {pliki_url}")
                        
                        elif 'Pobierz Rozwiązanie' in text:
                            rozwiazanie_url = f"https://ee-informatyk.pl{href}"
                            print(f"      ✅ Rozwiązanie: {rozwiazanie_url}")
                    
                    # Определяем тип (по иконкам)
                    icons = item.find_all('h3', {'data-wenk': True})
                    practice_type = []
                    for icon in icons:
                        wenk_text = icon.get('data-wenk', '').lower()
                        if 'php' in wenk_text:
                            practice_type.append('PHP')
                        if 'baza danych' in wenk_text or 'database' in wenk_text:
                            practice_type.append('Database')
                    
                    practice_data = {
                        'code': code,
                        'date': date,
                        'year': parsed_year,  # ← Используем parsed_year
                        'type': ', '.join(practice_type) if practice_type else 'Standard',
                        'arkusz_url': arkusz_url,
                        'pliki_url': pliki_url,
                        'rozwiazanie_url': rozwiazanie_url,
                    }
                    
                    all_practices.append(practice_data)
                
                except Exception as e:
                    print(f"    ❌ Ошибка обработки элемента: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            time.sleep(1)  # Задержка между годами
        
        return all_practices
    
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return []
    
def scrape_profile_practice(profile_key, base_url):
    """Парсит практические задания для профиля"""
    model = PRACTICE_MODELS.get(profile_key)
    
    if not model:
        print(f"❌ Неизвестный профиль: {profile_key}")
        return
    
    print(f"\n{'='*60}")
    print(f"📚 Практика {profile_key.upper()}")
    print(f"{'='*60}")
    
    practices_data = parse_practice_page(base_url, profile_key)
    
    print(f"\n📊 Всего найдено: {len(practices_data)}")
    
    db = SessionLocal()
    added = 0
    skipped = 0
    
    try:
        for p_data in tqdm(practices_data, desc="  💾 Сохранение"):
            existing = db.query(model).filter(
                model.code == p_data['code']
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            practice = model(
                code=p_data['code'],
                date=p_data['date'],
                year=int(p_data['year']),
                type=p_data['type'],
                arkusz_url=p_data['arkusz_url'],
                pliki_url=p_data['pliki_url'],
                rozwiazanie_url=p_data['rozwiazanie_url'],
                downloaded=0
            )
            
            db.add(practice)
            added += 1
        
        db.commit()
        
        print(f"\n✅ Результат:")
        print(f"   📝 Всего добавлено: {added}")
        print(f"   ⏭️  Пропущено: {skipped}\n")
    
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def main():
    print("\n🚀 СТАРТ ПАРСЕРА ПРАКТИКИ\n")
    
    # Парсим все профили
    for profile_key, base_url in PRACTICE_URLS.items():
        try:
            scrape_profile_practice(profile_key, base_url)
            time.sleep(2)
        except Exception as e:
            print(f"❌ {profile_key}: {e}")
            continue
    
    print("🎉 ГОТОВО!\n")

if __name__ == "__main__":
    main()