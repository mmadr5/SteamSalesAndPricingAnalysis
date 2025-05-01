import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json


# Load the JSON game list
with open("100_Steam_Assortment.json", "r", encoding="utf-8") as f:
    games = json.load(f)

appid_type_map = {str(game["appid"]): game["type"] for game in games}

# Paths to historical price data
price_folder = "PriceHistory"
discount_freq = {"AAA": [], "Indie": []}

# Loop through appids and count discount days
for appid, gtype in appid_type_map.items():
    path = os.path.join(price_folder, f"{appid}.csv")
    if not os.path.exists(path):
        continue

    try:
        df_discount_reviews = pd.read_csv(path)
        df_discount_reviews.columns = [col.strip().lower() for col in df_discount_reviews.columns]
        if "final price" not in df_discount_reviews.columns or "historical low" not in df_discount_reviews.columns:
            continue

        df_discount_reviews["final price"] = pd.to_numeric(df_discount_reviews["final price"], errors="coerce")
        df_discount_reviews["historical low"] = pd.to_numeric(df_discount_reviews["historical low"], errors="coerce")

        # A discount is when historical low < final price
        df_discount_reviews["is_discounted"] = df_discount_reviews["historical low"] < df_discount_reviews["final price"]
        num_discount_days = df_discount_reviews["is_discounted"].sum()
        total_days = len(df_discount_reviews)

        if total_days > 0:
            discount_ratio = num_discount_days / total_days
            discount_freq[gtype].append(discount_ratio)
    except Exception as e:
        print(f"Error processing AppID {appid}: {e}")

# Create a DataFrame for visualization
discount_df = pd.DataFrame([
    {"Type": "AAA", "Discount Ratio": ratio} for ratio in discount_freq["AAA"]
] + [
    {"Type": "Indie", "Discount Ratio": ratio} for ratio in discount_freq["Indie"]
])

# Plot the distributions
plt.figure(figsize=(8, 6))
sns.violinplot(data=discount_df, x="Type", y="Discount Ratio", inner="box", palette="Set2")
plt.title("Distribution of Discount Frequency by Game Type")
plt.ylabel("Discount Ratio (Days Discounted / Total Days)")
plt.xlabel("Game Type")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
