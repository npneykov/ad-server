import requests

# Replace with your actual sitemap URL
sitemap_url = 'https://ad-server.fly.dev/sitemap.xml'

ping_url = f'https://www.google.com/ping?sitemap={sitemap_url}'

res = requests.get(ping_url)

if res.status_code == 200:
    print('✅ Sitemap pinged successfully.')
else:
    print(f'❌ Failed to ping sitemap. Status: {res.status_code}')
