import google.generativeai as genai
import feedparser
import json
import os

# 1. KI-SETUP
# Holt sich den Key aus den GitHub Secrets
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. DEINE AKTUALISIERTE PODCAST-LISTE
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

def kuerze_mit_ki(name, titel, beschreibung):
    """Nutzt Gemini KI für deutsche Zusammenfassungen mit max. 2 Sätzen"""
    # Prompt-Anpassung gemäß Benutzervorgabe
    prompt = (
        f"Podcast: {name}. Folge: {titel}. Info: {beschreibung}. "
        f"Fasse den Inhalt auf DEUTSCH in maximal 2 Sätzen zusammen. "
        f"Antworte nur mit der Zusammenfassung, ohne Einleitung."
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"KI-Fehler bei {name}: {e}")
        return "Spannende neue Folge! Jetzt reinhören für alle Details."

def main():
    ticker_results = []
    for name, url in PODCAST_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                continue
            
            latest = feed.entries[0]
            # Extraktion der Grunddaten aus dem RSS-Feed
            real_title = latest.title
            real_desc = latest.summary if 'summary' in latest else "Keine Info verfügbar."
            real_link = latest.link
            
            # KI-Zusammenfassung generieren
            short_info = kuerze_mit_ki(name, real_title, real_desc)
            
            # Speichern mit den Kürzeln für den Web-Code
            ticker_results.append({
                "p": name,       # Podcast Name
                "t": real_title, # Titel
                "s": short_info, # Summary (max 2 Sätze, Deutsch)
                "l": real_link   # Link
            })
        except Exception as e:
            print(f"Fehler bei {name}: {e}")
            continue

    # Speichern der Ergebnisse als JSON
    with open("ticker_data.json", "w", encoding="utf-8") as f:
        json.dump(ticker_results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
