"""Ping IndexNow API to instantly notify Bing/Yandex about URL changes.

Usage:
    uv run python ping_indexnow.py
"""

import json
import urllib.error
import urllib.request

INDEXNOW_KEY = 'b1c4e8f2a3d7e9f0b5c6d8a1e4f7c3b2'
HOST = 'ad-server.fly.dev'

URLS = [
    f'https://{HOST}/',
    f'https://{HOST}/blog',
    f'https://{HOST}/blog/best_free_tools',
    f'https://{HOST}/blog/preview_html5_banners',
    f'https://{HOST}/blog/open_source_ad_servers',
    f'https://{HOST}/blog/monetize_website',
    f'https://{HOST}/blog/banner_ctr_optimization',
    f'https://{HOST}/publisher',
    f'https://{HOST}/stats',
    f'https://{HOST}/tools',
    f'https://{HOST}/tools/banner-preview-728x90.html',
    f'https://{HOST}/tools/banner-preview-300x250.html',
    f'https://{HOST}/tools/banner-preview-160x600.html',
    f'https://{HOST}/tools/banner-preview-160x300.html',
    f'https://{HOST}/tools/banner-preview-320x50.html',
    f'https://{HOST}/tools/banner-preview-468x60.html',
    f'https://{HOST}/tools/test-html5-banner-preview.html',
    f'https://{HOST}/tools/html5-banner-preview-collection.html',
    f'https://{HOST}/tools/html5-banner-validator.html',
]


def ping_indexnow():
    """Send batch URL notification to IndexNow API."""
    payload = {
        'host': HOST,
        'key': INDEXNOW_KEY,
        'keyLocation': f'https://{HOST}/{INDEXNOW_KEY}.txt',
        'urlList': URLS,
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        'https://api.indexnow.org/IndexNow',
        data=data,
        headers={'Content-Type': 'application/json; charset=utf-8'},
        method='POST',
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f'IndexNow response: {resp.status} {resp.reason}')
            print(f'Submitted {len(URLS)} URLs to IndexNow (Bing, Yandex)')
    except urllib.error.HTTPError as e:
        print(f'IndexNow error: {e.code} {e.reason}')
        if e.code == 202:
            print('Status 202 = Accepted. URLs queued for processing.')
    except urllib.error.URLError as e:
        print(f'Network error: {e.reason}')


if __name__ == '__main__':
    print(f'Pinging IndexNow with {len(URLS)} URLs...\n')
    ping_indexnow()
    print('\nDone.')
