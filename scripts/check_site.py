"""One-time browser QA for the public static build."""
from pathlib import Path
import json, threading, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urljoin, urlparse, unquote
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/site-review'
OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'public')))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/'
results={'base_url':base,'pages':[],'errors':[],'checks':[]}
for path in (ROOT/'public').rglob('*.html'):
    soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
    for e in soup.select('[href],[src]'):
        ref=e.get('href') or e.get('src')
        if ref.startswith(('https:','http:','data:','#')):continue
        target=(path.parent/unquote(ref.split('#')[0])).resolve()
        assert target.exists(),(path,ref)
results['checks'].append('All local HTML links and assets exist')
probe=Path(r'C:\Users\Yuri\.codex\skills\ui-verification\scripts\page_probe.js').read_text(encoding='utf-8')
with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True)
    context=browser.new_context(permissions=['clipboard-read','clipboard-write'])
    page=context.new_page()
    page.on('pageerror',lambda err:results['errors'].append(str(err)))
    page.on('response',lambda r: results['errors'].append(f'{r.status} {r.url}') if r.status>=400 and r.url.startswith(base) else None)
    for width,height in [(1280,900),(360,800)]:
        page.set_viewport_size({'width':width,'height':height})
        for route,name in [('', 'home'),('talks/leontiev.html','talk')]:
            page.goto(base+route,wait_until='networkidle')
            page.evaluate('document.fonts.ready')
            page.locator('img').evaluate_all('(imgs)=>imgs.forEach(i=>i.loading="eager")')
            for img in page.locator('img').all(): img.evaluate('(i)=>i.decode().catch(()=>{})')
            page.screenshot(path=str(OUT/f'{name}-{width}-first.png'))
            page.screenshot(path=str(OUT/f'{name}-{width}-full.png'),full_page=True)
            report=page.evaluate(probe);results['pages'].append({'name':name,**report})
            assert not report['hasHorizontalOverflow'],(name,width)
            assert report['brokenImageCandidates']['count']==0
        page.goto(base,wait_until='networkidle')
        field=page.get_by_role('searchbox')
        field.fill('Людкевич');assert page.locator('.card:visible').count()==1
        page.get_by_label('Направление',exact=True).select_option('GEO');assert page.locator('.card:visible').count()==0
        assert page.locator('#empty').is_visible()
        page.get_by_role('button',name='Сбросить',exact=True).click();assert page.locator('.card:visible').count()==19
        page.get_by_label('Направление',exact=True).select_option('GEO');assert page.locator('.card:visible').count()==4
        results['checks'].append(f'{width}: search, combined empty result, reset, GEO filter')
    page.goto(base,wait_until='networkidle')
    page.keyboard.press('Tab');assert page.locator(':focus').text_content()=='Перейти к содержимому'
    page.keyboard.press('Tab');assert page.locator(':focus').get_attribute('class')=='brand'
    page.keyboard.press('Tab');assert page.locator(':focus').text_content()=='Доклады'
    page.keyboard.press('Enter');page.wait_for_url('**/index.html')
    results['checks'].append('Keyboard: skip link, brand, navigation and Enter')
    page.goto(base+'talks/leontiev.html',wait_until='networkidle')
    page.get_by_role('button',name='Скопировать',exact=True).click()
    page.wait_for_function("document.querySelector('.copy-status').textContent.length > 0")
    assert 'Промт скопирован' in page.locator('.copy-status').text_content()
    assert 'недельный SEO-отчёт' in page.evaluate('navigator.clipboard.readText()')
    results['checks'].append('Prompt copy: clipboard content verified')
    for file in (ROOT/'public/talks').glob('*.html'):
        page.goto(base+'talks/'+file.name,wait_until='domcontentloaded')
        assert page.locator('#prompt-text').text_content().strip()
        assert page.locator('.evidence .source').count()>=4
    results['checks'].append('All 19 talk pages: prompt and page references present')
    browser.close()
server.shutdown()
(OUT/'measurements.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'checks':results['checks'],'errors':results['errors']},ensure_ascii=False,indent=2))
assert not results['errors']
