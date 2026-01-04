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

def generiere_beschreibung(name, titel=None, beschreibung=None):
    if titel and beschreibung and len(beschreibung) > 10:
        # Fall 1: Zusammenfassung der aktuellen Folge
        prompt = f"Podcast: {name}. Folge: {titel}. Info: {beschreibung}. Fasse den Inhalt auf DEUTSCH in maximal 2 Sätzen zusammen."
    else:
        # Fall 2: Allgemeiner Text über den Podcast (wenn Daten fehlen)
        prompt = f"Schreibe einen kurzen, spannenden Text (auf DEUTSCH, max. 2 Sätze) darüber, worum es im Podcast '{name}' allgemein geht."
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "Ein Highlight aus unserem Netzwerk. Jetzt reinhören!"

def main():
    ticker_results = []
    for name, url in PODCAST_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                latest = feed.entries[0]
                summary = generiere_beschreibung(name, latest.title, latest.get('summary', ''))
                ticker_results.append({"p": name, "t": latest.title, "s": summary})
        except: continue
    
    with open("ticker_data.json", "w", encoding="utf-8") as f:
        json.dump(ticker_results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
