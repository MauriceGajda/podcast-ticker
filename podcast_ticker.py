import google.generativeai as genai
import feedparser
import json
import os
import random

# KI-Setup
# Stellen Sie sicher, dass die Umgebungsvariable GEMINI_API_KEY gesetzt ist
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

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
    "In kleiner Runde": "https://kleinerrunde.podigee.io/feed/mp3",
    "Interior Intim": "https://interiorintim.podigee.io/feed/mp3",
    "Jein!": "https://jein.podigee.io/feed/mp3",
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

def generiere_zusammenfassung(name, titel, beschreibung):
    # Liste für Variationen, falls die API keine Antwort liefert
    fallbacks = [
        f"Tauche ein in die neueste Episode von {name}. Spannende Einblicke garantiert!",
        f"In dieser Folge von {name} gibt es wieder jede Menge Gesprächsstoff. Hör direkt rein!",
        f"Neue Insights und packende Themen erwarten dich bei {name}.",
        f"Verpasse nicht, was {name} in der aktuellen Folge zu berichten hat.",
        f"Eine frische Brise für deine Ohren: {name} ist mit einem neuen Thema zurück."
    ]

    # Bereinigung der Beschreibung
    clean_desc = beschreibung.replace('<p>', '').replace('</p>', '').strip()
    
    # Prompt-Optimierung für mehr Abwechslung
    if not clean_desc or len(clean_desc) < 20:
        prompt = (f"Erstelle eine kurze, mitreißende Teaser-Beschreibung für den Podcast '{name}'. "
                  f"Sei kreativ, direkt und vermeide Standardfloskeln. "
                  f"Maximal 2 Sätze auf DEUTSCH.")
    else:
        prompt = (f"Fasse die Podcast-Folge '{titel}' von '{name}' kurz und knackig zusammen. "
                  f"Variiere den Satzbau und beginne nicht mit 'In dieser Folge'. "
                  f"Nutze maximal 2 Sätze auf DEUTSCH. Kontext: {clean_desc[:800]}")
    
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
        else:
            return random.choice(fallbacks)
    except Exception as e:
        print(f"Fehler bei Podcast {name}: {e}")
        return random.choice(fallbacks)

def main():
    ticker_results = []
    print("Starte Update der Podcast-Daten...")
    
    for name, url in PODCAST_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                latest = feed.entries[0]
                img_url = feed.feed.image.href if 'image' in feed.feed else ""
                
                # Individuelle Zusammenfassung generieren
                summary = generiere_zusammenfassung(name, latest.title, latest.get('summary', ''))
                
                ticker_results.append({
                    "p": name, 
                    "t": latest.title, 
                    "s": summary,
                    "i": img_url
                })
                print(f"Erfolgreich: {name}")
        except Exception as e:
            print(f"Fehler beim Parsen von {name}: {e}")
            continue
    
    # Speichern der Ergebnisse
    with open("ticker_data.json", "w", encoding="utf-8") as f:
        json.dump(ticker_results, f, ensure_ascii=False, indent=2)
    print("Datei 'ticker_data.json' wurde aktualisiert.")

if __name__ == "__main__":
    main()
