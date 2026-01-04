import google.generativeai as genai
import feedparser
import json
import os

# KI-Setup
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
    # Falls keine Beschreibung da ist, erzwingen wir eine allgemeine Show-Info
    if not beschreibung or len(beschreibung) < 15:
        prompt = f"Erstelle eine allgemeine, spannende Zusammenfassung auf DEUTSCH (max. 2 Sätze) für den Podcast '{name}'. Erkläre kurz worum es geht."
    else:
        prompt = f"Fasse die Podcast-Folge '{titel}' von '{name}' auf DEUTSCH zusammen. Nutze maximal 2 Sätze. Info: {beschreibung}"
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        # Letzter Fallschirm, falls KI-API komplett streikt:
        return f"Entdecke die neueste Welt von {name}. Ein Muss für alle Fans von spannenden Gesprächen."

def main():
    ticker_results = []
    for name, url in PODCAST_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                latest = feed.entries[0]
                img_url = feed.feed.image.href if 'image' in feed.feed else ""
                
                # Zwingende Zusammenfassung generieren
                summary = generiere_zusammenfassung(name, latest.title, latest.get('summary', ''))
                
                ticker_results.append({
                    "p": name, 
                    "t": latest.title, 
                    "s": summary,
                    "i": img_url
                })
        except: continue
    
    with open("ticker_data.json", "w", encoding="utf-8") as f:
        json.dump(ticker_results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
