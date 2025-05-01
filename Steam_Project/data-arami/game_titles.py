from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import json

with open("100_Steam_Assortment.json", "r", encoding="utf-8") as f:
    games = json.load(f)

# Create a list of game names
game_names = [game["name"] for game in games if game["name"]]

# Generate word cloud text
text = " ".join(game_names)
# Extract main genre (first in comma-separated genre list if exists)
genres = []
for game in games:
    genre = game.get("genre", "")
    if genre:
        main_genre = genre.split(',')[0].strip()
        genres.append(main_genre)

genre_counts = pd.Series(genres).value_counts()

# Plot
plt.figure(figsize=(12, 6))
genre_counts.plot(kind='bar', color='skyblue')
plt.xticks(rotation=45, ha='right')
plt.xlabel("Main Genre")
plt.ylabel("Number of Games")
plt.title("Distribution of Games by Genre")
plt.tight_layout()
plt.show()
