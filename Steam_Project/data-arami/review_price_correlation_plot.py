import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Paths
review_folder = "ReviewHistory"
price_folder = "PriceHistory"
game_json = "100_Steam_Assortment.json"

# Load game metadata
with open(game_json, "r", encoding="utf-8") as f:
    games = json.load(f)

appid_type_map = {str(game["appid"]): game["type"] for game in games}
records = []

for appid in appid_type_map:
    review_path = os.path.join(review_folder, f"{appid}.csv")
    price_path = os.path.join(price_folder, f"{appid}.csv")

    if not os.path.exists(review_path) or not os.path.exists(price_path):
        continue

    try:
        review_df = pd.read_csv(review_path)
        price_df = pd.read_csv(price_path)

        # Normalize and clean column names
        review_df.columns = [col.strip().lower() for col in review_df.columns]
        price_df.columns = [col.strip().lower() for col in price_df.columns]

        if "final price" not in price_df.columns or "historical low" not in price_df.columns:
            print(f"[{appid}] Missing price columns: {price_df.columns}")
            continue

        # Convert to date only
        review_df["date"] = pd.to_datetime(review_df["datetime"]).dt.date
        price_df["date"] = pd.to_datetime(price_df["datetime"]).dt.date

        # Group data by date
        review_grouped = review_df.groupby("date").agg({
            "positive reviews": "sum",
            "negative reviews": "sum"
        }).reset_index()

        price_grouped = price_df.groupby("date").agg({
            "final price": "last",
            "historical low": "last"
        }).reset_index()

        # Merge
        merged = pd.merge(review_grouped, price_grouped, on="date", how="inner")

        # Calculate metrics
        merged["discount_percent"] = 100 * (merged["final price"] - merged["historical low"]) / merged["final price"]
        merged["discount_percent"] = merged["discount_percent"].clip(lower=0)
        merged["review_volume"] = merged["positive reviews"] + merged["negative reviews"]
        merged = merged.dropna(subset=["discount_percent", "review_volume"])
        merged = merged[merged["review_volume"] > 0]

        for _, row in merged.iterrows():
            records.append({
                "appid": appid,
                "discount_percent": row["discount_percent"],
                "review_volume": row["review_volume"],
                "type": appid_type_map[appid]
            })

    except Exception as e:
        print(f"[{appid}] Error: {e}")
        continue

# Convert to DataFrame
df = pd.DataFrame(records)

if df.empty:
    print("No valid data to plot.")
else:
    plt.figure(figsize=(12, 7))
    sns.scatterplot(
        data=df,
        x="discount_percent",
        y="review_volume",
        hue="type",
        alpha=0.6,
        palette="Set1"
    )
    sns.regplot(
        data=df,
        x="discount_percent",
        y="review_volume",
        scatter=False,
        lowess=True,
        color="black"
    )

    plt.title("Discount % vs Daily Review Volume")
    plt.xlabel("Discount Percentage (%)")
    plt.ylabel("Review Volume (per day)")
    plt.legend(title="Game Type")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
