import requests
import pandas as pd
import time

BASE_URL = "https://steamspy.com/api.php"

def fetch_all_steamspy_data(max_pages=None):
    page = 0
    all_data = []

    while True:
        print(f"Fetching page: {page}")

        params = {'request': 'all', 'page': page}
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code != 200:
            print(f"Failed to fetch page {page}, status code: {response.status_code} - {response.text} - {response.headers}")
            break

        data = response.json()

        if not data:
            print("No more data available.")
            break

        all_data.extend(data.values())

        page += 1

        # Break if maximum pages specified
        if max_pages and page >= max_pages:
            break

        # Wait for 60 seconds per API rate limits
        time.sleep(60)

    return all_data


if __name__ == '__main__':
    # Specify max_pages=None to fetch all data, or set a limit to control fetching
    data = fetch_all_steamspy_data(max_pages=None)

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv('steamspy_all_data.csv', index=False)

    print("Data successfully saved to steamspy_all_data.csv")
