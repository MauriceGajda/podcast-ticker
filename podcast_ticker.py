import google.generativeai as genai
import feedparser
import json
import os

# KI-SETUP
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Deine Liste
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

def get_ai_summary(podcast, title, desc):
    # Einfacher Prompt für klare Ergebnisse
    prompt = f"Fasse die Podcast-Folge '{title}' von '{podcast}' kurz zusammen (max. 140 Zeichen). Info: {desc}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return desc[:137] + "..." # Fallback falls KI versagt

def main():
    final_data = []
    for name, url in PODCAST_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            if not feed.entries: continue
            
            latest = feed.entries[0]
            # Wir holen die echten Daten aus dem RSS
            real_title = latest.title
            real_desc = latest.summary if 'summary' in latest else "Keine Info verfügbar."
            real_link = latest.link
            
            # KI Zusammenfassung erstellen
            short_info = get_ai_summary(name, real_title, real_desc)
            
            final_data.append({
                "p": name,       # p für Podcast Name
                "t": real_title, # t für Titel
                "s": short_info, # s für Summary
                "l": real_link   # l für Link
            })
        except: continue

    with open("ticker_data.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
