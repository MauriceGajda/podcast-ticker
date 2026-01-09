import google.generativeai as genai
import feedparser
import json
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor

# KI-Setup
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Erweiterte Feed-Liste
PODCAST_FEEDS = {
    "Aktivkohle": "https://aktivkohle-show.podigee.io/feed/mp3",
    "Bart & Schnauze": "https://bartundschnauze.podigee.io/feed/mp3",
    "Base Talk – Goethe WG": "https://basetalk.podigee.io/feed/mp3",
    "Big Problems Only": "https://bigproblemsonly.podigee.io/feed/mp3",
    "Busenfreundin": "https://anchor.fm/s/10ca0f264/podcast/rss",
    "Catch Me If You Speak": "https://catchmeifyouspeak.podigee.io/feed/mp3",
    "Celebrate Organizations": "https://celebrateorganizations.podigee.io/feed/mp3",
    "Champagner & Chaos": "https://champagnerundchaos.podigee.io/feed/mp3",
    "Cineolux": "https://cineolux.podigee.io/feed/mp3",
    "Dachboden Revue": "https://dachbodenrevue.podigee.io/feed/mp3",
    "Das Schatten Q*abinett": "https://bkatheater.podigee.io/feed/mp3",
    "Democracy Now!": "https://www.democracynow.org/podcast.xml",
    "Gschichtn aus der Schwulenbar": "https://gschichtnausderschwulenbar.podigee.io/feed/mp3",
    "Häppchenwiese": "https://haeppchenwiese.podigee.io/feed/mp3",
    "In kleiner Runde": "https://kleinerrunde.podigee.io/feed/mp3",
    "Interior Intim": "https://interiorintim.podigee.io/feed/mp3",
    "Jein!": "https://jein.podigee.io/feed/mp3",
    "Leben Reicht": "https://lebenreicht.podigee.io/feed/mp3",
    "Meryl Deep Talk": "https://meryldeeptalk.podigee.io/feed/mp3",
    "Reality TV News": "https://talknow-news.podigee.io/feed/mp3",
    "Robin Gut": "https://robingut.podigee.io/feed/mp3",
    "Stoeckel und Krawall": "https://stoeckelundkrawall.podigee.io/feed/mp3",
    "Süß & Leiwand": "https://bkatheater.podigee.io/feed/mp3",
    "TMDA": "https://fynnkliemann.libsyn.com/rss",
    "TV Noir": "https://tvnoir.podigee.io/feed/mp3",
    "Überdosis Crime": "https://ueberdosiscrime.podigee.io/feed/mp3",
    "Übers Podcasten": "https://uebers-podcasten.podigee.io/feed/mp3",
    "Wechselwillig": "https://wechselwillig.podigee.io/feed/mp3"
}

def clean_html(text):
    if not text: return ""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

def generiere_zusammenfassung(name, titel, beschreibung):
    fallbacks = [f"Neu bei {name}", f"Highlight: {titel[:20]}...", f"Jetzt anhören: {name}"]
    clean_desc = clean_html(beschreibung)
    
    prompt = (
        f"Aufgabe: Fasse die TV-Folge '{titel}' von '{name}' zusammen.\n"
        f"Inhalt: {clean_desc[:500]}\n"
        f"Regel: Antworte IMMER mit EXAKT 5 Wörtern auf Deutsch im Stil einer TV-Zeitschrift. Kein Punkt am Ende."
    )
    
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            words = response.text.strip().split()
            return " ".join(words[:5])
    except:
        pass
    return random.choice(fallbacks)

def process_podcast(name, url, old_data_dict):
    try:
        # Cache-Busting & User-Agent
        bust_url = f"{url}?v={int(time.time())}" if "?" not in url else f"{url}&v={int(time.time())}"
        feed = feedparser.parse(bust_url, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        
        if not feed.entries:
            print(f"⚠️  Keine Einträge gefunden für: {name}")
            return None
        
        latest = feed.entries[0]
        titel = latest.title
        
        # Caching: Nur überspringen, wenn der Titel exakt gleich ist
        if name in old_data_dict and old_data_dict[name]['t'] == titel:
            return old_data_dict[name]

        print(f"✨ Aktualisiere: {name}...")
        
        img_url = ""
        if 'image' in feed.feed: img_url = feed.feed.image.href
        elif 'itunes_image' in feed.feed: img_url = feed.feed.itunes_image
        
        summary = generiere_zusammenfassung(name, titel, latest.get('summary', ''))
        
        return {"p": name, "t": titel, "s": summary, "i": img_url}
    except Exception as e:
        print(f"❌ Fehler bei {name}: {str(e)}")
        return None

def main():
    old_data_dict = {}
    if os.path.exists("ticker_data.json"):
        try:
            with open("ticker_data.json", "r", encoding="utf-8") as f:
                old_list = json.load(f)
                old_data_dict = {item['p']: item for item in old_list}
        except: pass

    print(f"🔄 Starte Scan für {len(PODCAST_FEEDS)} Podcasts...")
    
    results = []
    # Höhere worker_anzahl für schnellere Verarbeitung
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_podcast, n, u, old_data_dict): n for n, u in PODCAST_FEEDS.items()}
        for future in futures:
            res = future.result()
            if res:
                results.append(res)

    # WICHTIG: Sortiere die Liste alphabetisch nach Podcast-Name ("p")
    # Das verhindert, dass immer nur die gleichen 3 vorne stehen
    results.sort(key=lambda x: x['p'])

    with open("ticker_data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Fertig! {len(results)} von {len(PODCAST_FEEDS)} Podcasts erfolgreich geladen.")

if __name__ == "__main__":
    main()
