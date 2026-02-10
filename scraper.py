import os
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin

BASE_URL = "https://www.folklore.ee/pubte/eraamat/rahvamuusika/en/index"
ROOT_URL = "https://www.folklore.ee/pubte/eraamat/rahvamuusika/en/"
MEDIA_ROOT = "https://www.folklore.ee/pubte/eraamat/rahvamuusika/_media/"
NOTATION_ROOT = "https://www.folklore.ee/pubte/eraamat/rahvamuusika/_notation/"
OUTPUT_DIR = "data"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def download_file(url, path):
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return True
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            return False
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def clean_text(element):
    if not element:
        return ""
    clone = BeautifulSoup(str(element), 'html.parser')
    for s in clone(['script', 'style']):
        s.decompose()
        
    # Preserving linguistic markups
    for sup in clone.find_all('sup'):
        sup_content = sup.get_text()
        sup.replace_with(f"__SUP_START__{sup_content}__SUP_END__")
    
    # Handle line breaks and paragraphs to match HTML rendering
    for p in clone.find_all('p'):
        p.append('__PARA_BREAK__')
    for br in clone.find_all('br'):
        br.replace_with('__LINE_BREAK__')
        
    text = clone.get_text()
    
    # 1. Replace source code newlines with space (they don't render in HTML)
    text = text.replace('\n', ' ')
    # 2. Normalize whitespace
    text = re.sub(r' +', ' ', text)
    # 3. Convert our markers to real newlines
    text = text.replace('__LINE_BREAK__', '\n')
    text = text.replace('__PARA_BREAK__', '\n\n')
    # 4. Restore <sup> tags
    text = text.replace('__SUP_START__', '<sup>').replace('__SUP_END__', '</sup>')
    
    # Strip each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    # Normalize multiple newlines (max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def get_lyrics(song_soup):
    estonian_lyrics = []
    english_lyrics = []
    
    # Global search for lyrics classes
    origs = song_soup.find_all(class_='song-orig')
    transs = song_soup.find_all(class_='song-trans')
    
    for o in origs:
        if not o.find_parent(class_='song-note'):
            estonian_lyrics.append(clean_text(o))
    for t in transs:
        if not t.find_parent(class_='song-note'):
            english_lyrics.append(clean_text(t))
            
    if not estonian_lyrics and not english_lyrics:
        tekst_divs = song_soup.find_all('div', class_='tekst')
        for div in tekst_divs:
            clone = BeautifulSoup(str(div), 'html.parser')
            note = clone.find(class_='song-note')
            if note: note.decompose()
            if clone.find('h4') or clone.find(class_='audioplayer'):
                continue
            text = clean_text(clone)
            if text:
                estonian_lyrics.append(text)
                
    return "\n\n".join(estonian_lyrics), "\n\n".join(english_lyrics)

def scrape(limit=None):
    soup = get_soup(BASE_URL)
    if not soup: return

    sidebar = soup.find(id="sidebar-wrapper")
    if not sidebar: return

    song_links = []
    for a in sidebar.find_all('a', href=True):
        href = a['href']
        if re.match(r'^\d{3}-', href):
            song_links.append(href)
    
    song_links = sorted(list(set(song_links)))
    if limit:
        song_links = song_links[:limit]
        print(f"Processing {len(song_links)} songs.")

    for href in song_links:
        song_id = href.split('-')[0]
        full_url = urljoin(ROOT_URL, href)
        song_soup = get_soup(full_url)
        if not song_soup: continue
            
        title_tag = song_soup.find('h2', class_='song-head')
        title = title_tag.get_text(strip=True) if title_tag else href
        
        performer_info = ""
        performer_name = ""
        performer_url = ""
        region = ""
        
        tekst_divs = song_soup.find_all('div', class_='tekst')
        if tekst_divs:
            first_h4 = tekst_divs[0].find('h4')
            if first_h4:
                performer_info = first_h4.get_text(separator=" ", strip=True)
                performer_a = first_h4.find('a', href=True)
                if performer_a:
                    performer_name = performer_a.get_text(strip=True)
                    performer_url = urljoin(ROOT_URL, performer_a['href'])
                    after_a = performer_a.next_sibling
                    if after_a:
                        after_text = str(after_a)
                        region_match = re.search(r'^([^\(]+)', after_text)
                        if region_match:
                            region = region_match.group(1).strip()

        est_lyrics, eng_lyrics = get_lyrics(song_soup)

        notation_url = None
        noodiriba = song_soup.find('div', class_='noodiriba')
        if noodiriba:
            img = noodiriba.find('img')
            if img and img.get('src'):
                notation_url = urljoin(full_url, img['src'])
        if not notation_url:
            notation_img = song_soup.find('img', src=re.compile(r'_notation'))
            if notation_img:
                notation_url = urljoin(full_url, notation_img['src'])
        if not notation_url:
             notation_url = f"{NOTATION_ROOT}{song_id}.png"

        mp3_url = f"{MEDIA_ROOT}{song_id}.mp3"
        ogg_url = f"{MEDIA_ROOT}{song_id}.ogg"
        
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")
        song_dir_name = f"{song_id}_{safe_title}"
        song_path = os.path.join(OUTPUT_DIR, song_dir_name)
        if not os.path.exists(song_path): os.makedirs(song_path)
            
        if notation_url:
            download_file(notation_url, os.path.join(song_path, f"{song_id}_notation.png"))
        download_file(mp3_url, os.path.join(song_path, f"{song_id}.mp3"))
        download_file(ogg_url, os.path.join(song_path, f"{song_id}.ogg"))
             
        if est_lyrics:
            with open(os.path.join(song_path, "lyrics_estonian.txt"), 'w', encoding='utf-8') as f:
                f.write(est_lyrics)
        if eng_lyrics:
            with open(os.path.join(song_path, "lyrics_english.txt"), 'w', encoding='utf-8') as f:
                f.write(eng_lyrics)
        
        metadata = {
            'id': song_id,
            'title': title,
            'performer_full_info': performer_info,
            'performer_name': performer_name,
            'performer_url': performer_url,
            'region': region,
            'original_url': full_url
        }
        with open(os.path.join(song_path, f"{song_id}_metadata.json"), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
            
        print(f"Processed {song_id}: {title}")

if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    scrape(limit=limit)
