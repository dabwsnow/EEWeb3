import requests
from bs4 import BeautifulSoup
import sys
import os
import re
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app import models
from tqdm import tqdm
import time

# Базовая папка для скачанных файлов
BASE_DOWNLOAD_DIR = Path("downloaded_practice")

# Маппинг профилей на модели (каждый профиль = своя таблица!)
PROFILE_TO_MODEL = {
    'inf02': models.PracticeINF02,
    'ee08': models.PracticeEE08,
    'e12': models.PracticeE12,
    'e13': models.PracticeE13,
    'inf03': models.PracticeINF03,
    'ee09': models.PracticeEE09,
    'e14': models.PracticeE14,
    'inf04': models.PracticeINF04,
}

def download_file(url, save_path):
    """Скачивает файл по URL"""
    try:
        print(f"        🔽 Скачивание: {url}")
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"        ✅ Сохранено: {save_path}")
        return str(save_path)
    except Exception as e:
        print(f"        ❌ Ошибка скачивания: {e}")
        return None

def extract_year_from_code(code):
    """Извлекает год из кода экзамена"""
    try:
        parts = code.split('-')
        if len(parts) >= 3:
            year_part = parts[2].split('.')[0]
            parsed_year = int(year_part)
            if parsed_year >= 14:
                return 2000 + parsed_year
            else:
                return 2000 + parsed_year
        return None
    except Exception as e:
        return None

def get_profile_from_code(code):
    """Определяет профиль из кода экзамена"""
    # INF.02-01-24.05-SG → inf02
    # EE.08-05-23.01-SG → ee08
    code_prefix = code.split('-')[0].replace('.', '').lower()
    return code_prefix

def parse_and_download_inf04():
    """Парсит и скачивает INF.04"""
    base_url = 'https://ee-informatyk.pl/inf04/praktyka/'
    print(f"\n🔍 Парсинг INF.04: {base_url}")
    
    all_practices = []
    
    try:
        response = requests.get(base_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        year_select = soup.find('select', {'name': 'rok'})
        if not year_select:
            print("  ❌ Не найден селектор года")
            return []
        
        years = [opt['value'] for opt in year_select.find_all('option') if opt['value'] != 'all']
        print(f"  📅 Найдено лет: {len(years)}")
        
        for year in years:
            print(f"\n  📅 Год: {year}")
            year_url = f"{base_url}?rok={year}"
            year_response = requests.get(year_url, timeout=15)
            year_soup = BeautifulSoup(year_response.text, "html.parser")
            
            practice_items = year_soup.find_all('div', class_='practice-list--one')
            print(f"    📝 Найдено заданий: {len(practice_items)}")
            
            for item in practice_items:
                try:
                    date_elem = item.find('div', class_='practice-list--one--date')
                    date = date_elem.find('h3').text.strip() if date_elem else None
                    
                    code_elem = item.find('div', class_='practice-list--one--id')
                    code = code_elem.find('h3').text.strip() if code_elem else None
                    
                    if not date or not code:
                        continue
                    
                    parsed_year = extract_year_from_code(code) or int(year)
                    print(f"\n    📋 {code} ({date})")
                    
                    exam_dir = BASE_DOWNLOAD_DIR / "inf04" / code
                    exam_dir.mkdir(parents=True, exist_ok=True)
                    
                    links_ul = item.find('ul', class_='practice-list--one--links')
                    arkusz_path = None
                    rozwiazanie_path = None
                    
                    if links_ul:
                        for link in links_ul.find_all('a'):
                            href = link.get('href', '')
                            text = link.text.strip()
                            
                            if 'Arkusz' in text and 'PDF' in text:
                                arkusz_page_url = f"https://ee-informatyk.pl{href}"
                                try:
                                    arkusz_response = requests.get(arkusz_page_url, timeout=15)
                                    arkusz_soup = BeautifulSoup(arkusz_response.text, "html.parser")
                                    pdf_link = arkusz_soup.find('a', href=re.compile(r'\.pdf$'))
                                    if pdf_link:
                                        pdf_url = f"https://ee-informatyk.pl{pdf_link['href']}"
                                        arkusz_path = download_file(pdf_url, exam_dir / "arkusz.pdf")
                                except Exception as e:
                                    print(f"      ❌ Ошибка аркуша: {e}")
                            
                            elif 'Rozwiązanie' in text:
                                rozwiazanie_url = f"https://ee-informatyk.pl{href}"
                                rozwiazanie_path = rozwiazanie_url
                                print(f"      📝 Rozwiązanie: {rozwiazanie_url}")
                    
                    all_practices.append({
                        'code': code,
                        'date': date,
                        'year': parsed_year,
                        'type': 'INF.04',
                        'profile': 'inf04',
                        'arkusz_path': arkusz_path,
                        'pliki_path': None,
                        'rozwiazanie_path': rozwiazanie_path,
                    })
                    
                    time.sleep(0.5)
                
                except Exception as e:
                    print(f"    ❌ Ошибка: {e}")
                    continue
            
            time.sleep(1)
        
        return all_practices
    
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return []

def parse_and_download_multiprofile(base_url, profiles_list, group_name):
    """Парсит и скачивает группу профилей (INF.02/EE.08/E.13/E.12 или INF.03/EE.09/E.14)"""
    print(f"\n🔍 Парсинг группы {group_name}: {base_url}")
    
    all_practices = []
    session = requests.Session()
    
    try:
        response = session.get(base_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        year_select = soup.find('select', {'name': 'rok'})
        if not year_select:
            print("  ❌ Не найден селектор года")
            return []
        
        years = [opt['value'] for opt in year_select.find_all('option') if opt['value'] != 'all']
        print(f"  📅 Найдено лет: {len(years)}")
        
        for profile in profiles_list:
            print(f"\n  🔄 Профиль: {profile.upper()}")
            
            for year in years:
                print(f"    📅 Год: {year}")
                
                params = {
                    'rok': year,
                    'egzamin': profile
                }
                
                year_response = session.get(base_url, params=params, timeout=15)
                year_soup = BeautifulSoup(year_response.text, "html.parser")
                
                practice_items = year_soup.find_all('div', class_='practice-list--one')
                print(f"      📝 Заданий: {len(practice_items)}")
                
                for item in practice_items:
                    try:
                        date_elem = item.find('div', class_='practice-list--one--date')
                        date = date_elem.find('h3').text.strip() if date_elem else None
                        
                        code_elem = item.find('div', class_='practice-list--one--id')
                        code = code_elem.find('h3').text.strip() if code_elem else None
                        
                        if not date or not code:
                            continue
                        
                        code_profile = get_profile_from_code(code)
                        if code_profile != profile:
                            continue
                        
                        parsed_year = extract_year_from_code(code) or int(year)
                        print(f"\n      📋 {code} ({date})")
                        
                        exam_dir = BASE_DOWNLOAD_DIR / profile / code
                        exam_dir.mkdir(parents=True, exist_ok=True)
                        
                        links_ul = item.find('ul', class_='practice-list--one--links')
                        arkusz_path = None
                        pliki_path = None
                        rozwiazanie_path = None
                        
                        if links_ul:
                            for link in links_ul.find_all('a'):
                                href = link.get('href', '')
                                text = link.text.strip()
                                
                                if 'Arkusz' in text:
                                    arkusz_page_url = f"https://ee-informatyk.pl{href}"
                                    try:
                                        arkusz_response = session.get(arkusz_page_url, timeout=15)
                                        arkusz_soup = BeautifulSoup(arkusz_response.text, "html.parser")
                                        pdf_link = arkusz_soup.find('a', href=re.compile(r'\.pdf$'))
                                        if pdf_link:
                                            pdf_url = f"https://ee-informatyk.pl{pdf_link['href']}"
                                            arkusz_path = download_file(pdf_url, exam_dir / "arkusz.pdf")
                                    except Exception as e:
                                        print(f"        ❌ Ошибка аркуша: {e}")
                                
                                elif 'Pobierz Pliki' in text or ('Pliki' in text and '.zip' in href.lower()):
                                    pliki_url = f"https://ee-informatyk.pl{href}"
                                    pliki_path = download_file(pliki_url, exam_dir / "pliki.zip")
                                
                                elif 'Pobierz Rozwiązanie' in text or ('Rozwiązanie' in text and '.zip' in href.lower()):
                                    rozwiazanie_url = f"https://ee-informatyk.pl{href}"
                                    rozwiazanie_path = download_file(rozwiazanie_url, exam_dir / "rozwiazanie.zip")
                        
                        all_practices.append({
                            'code': code,
                            'date': date,
                            'year': parsed_year,
                            'type': profile.upper(),
                            'profile': profile,
                            'arkusz_path': arkusz_path,
                            'pliki_path': pliki_path,
                            'rozwiazanie_path': rozwiazanie_path,
                        })
                        
                        time.sleep(0.5)
                    
                    except Exception as e:
                        print(f"      ❌ Ошибка: {e}")
                        continue
                
                time.sleep(1)
            
            time.sleep(2)
        
        return all_practices
    
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_to_database(practices_data):
    """Сохраняет данные в базу (каждый профиль в свою таблицу!)"""
    
    if not practices_data:
        print("  ⚠️ Нет данных для сохранения")
        return
    
    db = SessionLocal()
    added = 0
    skipped = 0
    
    try:
        for p_data in tqdm(practices_data, desc="  💾 Сохранение"):
            profile = p_data.get('profile')
            model = PROFILE_TO_MODEL.get(profile)
            
            if not model:
                print(f"      ⚠️ Неизвестный профиль: {profile}")
                continue
            
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
                arkusz_url=p_data.get('arkusz_path'),
                pliki_url=p_data.get('pliki_path'),
                rozwiazanie_url=p_data.get('rozwiazanie_path'),
                downloaded=1 if p_data.get('arkusz_path') else 0
            )
            
            db.add(practice)
            added += 1
        
        db.commit()
        
        print(f"\n✅ Результат:")
        print(f"   📝 Добавлено: {added}")
        print(f"   ⏭️  Пропущено: {skipped}")
    
    except Exception as e:
        print(f"\n❌ Ошибка сохранения: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def main():
    print("\n🚀 СТАРТ ПАРСЕРА И ЗАГРУЗЧИКА ПРАКТИКИ")
    print(f"📁 Файлы → {BASE_DOWNLOAD_DIR.absolute()}\n")
    
    BASE_DOWNLOAD_DIR.mkdir(exist_ok=True)
    
    all_data = []
    
    # 1. INF.04
    try:
        print(f"\n{'='*60}")
        print(f"📚 INF.04")
        print(f"{'='*60}")
        practices = parse_and_download_inf04()
        all_data.extend(practices)
        time.sleep(2)
    except Exception as e:
        print(f"❌ INF.04: {e}")
    
    # 2. INF.02 / EE.08 / E.13 / E.12
    try:
        print(f"\n{'='*60}")
        print(f"📚 INF.02 / EE.08 / E.13 / E.12")
        print(f"{'='*60}")
        practices = parse_and_download_multiprofile(
            'https://ee-informatyk.pl/inf02-ee08/praktyka/',
            ['inf02', 'ee08', 'e13', 'e12'],
            'INF02-GROUP'
        )
        all_data.extend(practices)
        time.sleep(2)
    except Exception as e:
        print(f"❌ INF02 группа: {e}")
    
    # 3. INF.03 / EE.09 / E.14
    try:
        print(f"\n{'='*60}")
        print(f"📚 INF.03 / EE.09 / E.14")
        print(f"{'='*60}")
        practices = parse_and_download_multiprofile(
            'https://ee-informatyk.pl/inf03-ee09/praktyka/',
            ['inf03', 'ee09', 'e14'],
            'INF03-GROUP'
        )
        all_data.extend(practices)
        time.sleep(2)
    except Exception as e:
        print(f"❌ INF03 группа: {e}")
    
    # Сохраняем все в БД
    if all_data:
        print(f"\n{'='*60}")
        print(f"💾 СОХРАНЕНИЕ В БАЗУ ДАННЫХ")
        print(f"{'='*60}")
        save_to_database(all_data)
    
    print("\n🎉 ГОТОВО! Все файлы скачаны и сохранены\n")

if __name__ == "__main__":
    main()