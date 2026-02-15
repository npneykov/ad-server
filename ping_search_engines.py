"""Ping Google and Bing to re-crawl the sitemap after a deploy.

Usage:
    uv run python ping_search_engines.py

This also runs the IndexNow submission for instant Bing/Yandex indexing.
"""

import urllib.request

SITEMAP_URL = 'https://ad-server.fly.dev/sitemap.xml'


def ping_google():
    url = f'https://www.google.com/ping?sitemap={SITEMAP_URL}'
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            print(f'[Google] {resp.status} {resp.reason}')
    except Exception as e:
        print(f'[Google] Error: {e}')


def ping_bing():
    url = f'https://www.bing.com/ping?sitemap={SITEMAP_URL}'
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            print(f'[Bing]   {resp.status} {resp.reason}')
    except Exception as e:
        print(f'[Bing]   Error: {e}')


def run_indexnow():
    """Also trigger IndexNow submission."""
    try:
        from ping_indexnow import ping_indexnow

        print('\n--- IndexNow ---')
        ping_indexnow()
    except ImportError:
        print('[IndexNow] ping_indexnow.py not found, skipping.')


if __name__ == '__main__':
    print(f'Pinging search engines with sitemap: {SITEMAP_URL}\n')
    ping_google()
    ping_bing()
    run_indexnow()
    print('\nDone. Search engines notified.')
