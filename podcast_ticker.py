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
    # Fallbacks für TV-Ausstrahlung (Maximal 5 Wörter)
    fallbacks = [
        f"Jetzt neu im TV: {name}",
        f"Aktuelle Highlights von {name}",
        f"Die TV-Premiere von {name}",
        f"{name}: Jetzt im Programm",
        f"Sehenswertes Update von {name}"
    ]

    # Bereinigung der Beschreibung (HTML-Tags entfernen)
    clean_desc = beschreibung.replace('<p>', '').replace('</p>', '').replace('<br>', '').strip()
    
    # Prompt-Optimierung für TV-Kontext und hartes 5-Wort-Limit
    if not clean_desc or len(clean_desc) < 20:
        prompt = (f"Schreibe einen ultrakurzen TV-Programmtext für die Sendung '{name}'. "
                  f"Maximal 5 Wörter, Deutsch, professionell.")
    else:
        prompt = (f"Fasse den Inhalt der TV-Folge '{titel}' von '{name}' zusammen. "
                  f"Kontext: {clean_desc[:600]} "
                  f"WICHTIG: Antworte mit maximal 5 Wörtern auf Deutsch. "
                  f"Schreibe für TV-Zuschauer (z.B. 'Thema heute: ...'), nicht für Hörer.")
    
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            # Bereinigung und hartes Abschneiden nach dem 5. Wort
            text = response.text.strip().replace("\n", " ")
            wort_liste = text.split()
            return " ".join(wort_liste[:5])
        else:
            return random.choice(fallbacks)
    except Exception as e:
        print(f"Fehler bei Podcast {name}: {e}")
        return random.choice(fallbacks)

def main():
    ticker_results = []
    print("Starte Update der Podcast-Daten für TV-Ausstrahlung...")
    
    for name, url in PODCAST_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                latest = feed.entries[0]
                img_url = feed.feed.image.href if 'image' in feed.feed else ""
                
                # Zusammenfassung generieren (TV-fokussiert, max 5 Wörter)
                summary = generiere_zusammenfassung(name, latest.title, latest.get('summary', ''))
                
                ticker_results.append({
                    "p": name, 
                    "t": latest.title, 
                    "s": summary,
                    "i": img_url
                })
                print(f"Erfolgreich verarbeitet: {name}")
        except Exception as e:
            print(f"Fehler beim Parsen von {name}: {e}")
            continue
    
    # Speichern der Ergebnisse als JSON
    with open("ticker_data.json", "w", encoding="utf-8") as f:
        json.dump(ticker_results, f, ensure_ascii=False, indent=2)
    
    print("-" * 30)
    print("Update abgeschlossen. Datei 'ticker_data.json' ist bereit.")

if __name__ == "__main__":
    main()
