"""Display titles for blog posts (breadcrumb + JSON-LD headline).

Body copy stays in templates; this avoids slug-derived titles in structured data.
"""

# Key = URL slug (blog_{slug}.html)
BLOG_DISPLAY_TITLES: dict[str, str] = {
    'best_free_tools': 'Best Free Tools to Test HTML Ads Online (2025)',
    'preview_html5_banners': 'How to Preview HTML5 Banners Without Google Ads',
    'open_source_ad_servers': 'Top 5 Open Source Ad Servers in 2025',
    'monetize_website': 'How to Monetize Your Website with Display Ads in 2026',
    'banner_ctr_optimization': '10 Proven Ways to Increase Banner Ad CTR in 2026',
    'standard_banner_sizes': (
        'Standard Banner Ad Sizes Guide 2026: IAB Dimensions & Best Practices'
    ),
    'html5_testing_guide': (
        'How to Test HTML5 Banner Ads Before Publishing: Complete 2026 Guide'
    ),
    'ad_server_setup': 'Ad Server Setup Guide 2026: Self-Hosted vs Cloud Solutions',
}
