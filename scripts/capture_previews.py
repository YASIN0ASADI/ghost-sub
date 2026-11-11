#!/usr/bin/env python3
"""Capture the real, synthetic purple fixture in a locally installed browser."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--panel', choices=['sub', 'marzban', 'pasarguard'], default='sub')
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        parser.error('Install Playwright in a private preview venv; see docs/THEME_PREVIEW_FA.md')
    subprocess.run([sys.executable, str(ROOT / 'scripts/build_preview.py')], check=True)
    errors = []
    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            for label, width, height in [('mobile', 390, 844), ('desktop', 1440, 1100)]:
                page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1, reduced_motion='reduce')
                page.on('pageerror', lambda exc: errors.append(str(exc)))
                # Fixtures use only invented hosts and sample data. Never query a real panel.
                page.route('https://**/*', lambda route: route.abort())
                page.route('http://**/*', lambda route: route.abort())
                page.goto((ROOT / 'preview' / (args.panel + '-purple.html')).as_uri(), wait_until='load')
                page.wait_for_selector('body.theme-purple')
                page.wait_for_selector('#page-loader', state='hidden')
                page.mouse.move(0, 0)
                page.wait_for_timeout(900)  # Finish chart entry transitions before capture.
                if page.evaluate('document.documentElement.scrollWidth > innerWidth'):
                    raise RuntimeError('Horizontal overflow at ' + label)
                target = ROOT / 'screenshots' / ('preview-purple.jpg' if label == 'mobile' else 'preview-purple-desktop.jpg')
                page.screenshot(path=str(target), full_page=True, type='jpeg', quality=90, animations='disabled')
                print('Captured:', target)
                page.close()
    if errors:
        raise RuntimeError('Preview JavaScript errors: ' + '\n'.join(errors))
    readme = ROOT / 'README.md'
    text = readme.read_text(encoding='utf-8').replace('screenshots/preview-purple.svg', 'screenshots/preview-purple.jpg').replace('screenshots/preview-purple.png', 'screenshots/preview-purple.jpg')
    text = text.replace('تصویر بنفش، پیش‌نمایش SVG پالت جدید با دادهٔ نمونه است؛ اسکرین‌شات مرورگر نیست.', 'تصویر بنفش از قالب اجراشده در مرورگر و با دادهٔ نمونه ثبت شده است.')
    readme.write_text(text, encoding='utf-8')
    print('README now points to the captured mobile screenshot. Review both images before committing.')


if __name__ == '__main__':
    main()
