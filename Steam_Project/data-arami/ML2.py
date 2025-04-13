import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split

# Load game metadata
with open("100_Steam_Assortment.json", "r", encoding="utf-8") as f:
    games = json.load(f)

# Map appid to game type (AAA or Indie)
appid_type_map = {str(game["appid"]): game["type"] for game in games}

# Paths
review_folder = "ReviewHistory"
price_folder = "PriceHistory"

records = []

# Load and process the review + price CSVs
for appid in appid_type_map:
    review_path = os.path.join(review_folder, f"{appid}.csv")
    price_path = os.path.join(price_folder, f"{appid}.csv")

    if not os.path.exists(review_path) or not os.path.exists(price_path):
        continue

    try:
        review_df = pd.read_csv(review_path)
        price_df = pd.read_csv(price_path)

        review_df.columns = [col.strip().lower() for col in review_df.columns]
        price_df.columns = [col.strip().lower() for col in price_df.columns]

        if "final price" not in price_df.columns or "historical low" not in price_df.columns:
            continue

        review_df["date"] = pd.to_datetime(review_df["datetime"]).dt.date
        price_df["date"] = pd.to_datetime(price_df["datetime"]).dt.date

        review_grouped = review_df.groupby("date").agg({
            "positive reviews": "sum",
            "negative reviews": "sum"
        }).reset_index()

        price_grouped = price_df.groupby("date").agg({
            "final price": "last",
            "historical low": "last"
        }).reset_index()

        merged = pd.merge(review_grouped, price_grouped, on="date", how="inner")
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

# Prepare DataFrame
df = pd.DataFrame(records)

if df.empty:
    print("No data available.")
else:
    # Machine Learning
    X = df[["discount_percent"]]
    y = df["review_volume"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    # Evaluation
    print("Model Evaluation:")
    print(f"R² Score: {r2_score(y_test, y_pred):.4f}")
    print(f"Mean Absolute Error: {mean_absolute_error(y_test, y_pred):.2f}")

    # Visualization
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x="discount_percent", y="review_volume", data=df, hue="type", alpha=0.6)
    plt.plot(X_test, y_pred, color='black', linewidth=2, label="Regression Line")
    plt.title("ML: Predicting Review Volume from Discount %")
    plt.xlabel("Discount Percentage (%)")
    plt.ylabel("Review Volume")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
