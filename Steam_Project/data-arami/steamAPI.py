import requests
import time
import json

STEAM_GET_APP_LIST = 'https://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json'
STEAM_APP_DETAILS = 'https://store.steampowered.com/api/appdetails'
RATE_LIMIT = 1.6  # seconds between requests (200 calls per 5 min)

def get_all_apps():
    response = requests.get(STEAM_GET_APP_LIST)
    response.raise_for_status()
    apps = response.json().get('applist', {}).get('apps', [])
    return apps

def get_app_details(appid):
    params = {'appids': appid, 'cc': 'us', 'l': 'en'}
    response = requests.get(STEAM_APP_DETAILS, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get(str(appid), {})

print('Fetching all Steam apps...')
apps = get_all_apps()
print(f'Total apps found: {len(apps)}')

app_details_list = []

for app in apps:
    appid = app['appid']
    name = app['name']
    print(f'Fetching details for AppID {appid} ({name})...')

    details = get_app_details(appid)
    if details.get('success'):
        app_data = details['data']
        if app_data.get('type') == 'game':
            app_details_list.append({
                'appid': appid,
                'name': app_data.get('name'),
                'type': app_data.get('type'),
                'required_age': app_data.get('required_age'),
                'is_free': app_data.get('is_free'),
                'controller_support': app_data.get('controller_support'),
                'dlc': app_data.get('dlc', []),
                'detailed_description': app_data.get('detailed_description'),
                'about_the_game': app_data.get('about_the_game'),
                'short_description': app_data.get('short_description'),
                'supported_languages': app_data.get('supported_languages'),
                'header_image': app_data.get('header_image'),
                'website': app_data.get('website'),
                'developers': app_data.get('developers', []),
                'publishers': app_data.get('publishers', []),
                'price_overview': app_data.get('price_overview', {}),
                'platforms': app_data.get('platforms', {}),
                'categories': app_data.get('categories', []),
                'genres': app_data.get('genres', []),
                'screenshots': app_data.get('screenshots', []),
                'movies': app_data.get('movies', []),
                'release_date': app_data.get('release_date', {}),
                'support_info': app_data.get('support_info', {}),
                'metacritic': app_data.get('metacritic', {}),
                'achievements': app_data.get('achievements', {}),
                'recommendations': app_data.get('recommendations', {}),
                'packages': app_data.get('packages', []),
                'legal_notice': app_data.get('legal_notice'),
                'background': app_data.get('background'),
                'content_descriptors': app_data.get('content_descriptors', {})
            })
    else:
        print(f'No valid data for AppID {appid}')

    time.sleep(RATE_LIMIT)

    if len(app_details_list) % 100 == 0:
        with open('steam_games_full.json', 'w', encoding='utf-8') as f:
            json.dump(app_details_list, f, ensure_ascii=False, indent=4)

with open('steam_games_full.json', 'w', encoding='utf-8') as f:
    json.dump(app_details_list, f, ensure_ascii=False, indent=4)

print('All details saved to steam_games_full.json')