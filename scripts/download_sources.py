"""Download public Drive PDFs and retain a resumable, verified inventory."""
from pathlib import Path
import json, time, hashlib
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
def download(item):
    dest = ROOT / 'sources' / item['name']
    if not dest.exists():
        for attempt in range(3):
            try:
                r = requests.get('https://drive.usercontent.google.com/download', params={'id':item['id'],'export':'download','confirm':'t'}, timeout=120)
                r.raise_for_status()
                if not r.content.startswith(b'%PDF'): raise ValueError('Response is not PDF')
                dest.write_bytes(r.content)
                break
            except Exception:
                if attempt == 2: raise
                time.sleep(2 * (attempt+1))
    item.update(bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),status='downloaded')
    print(item['name'], item['bytes'], flush=True)
    return item

if __name__ == '__main__':
    soup=BeautifulSoup((ROOT/'data/drive-folder.html').read_text(encoding='utf-8'),'html.parser')
    items=[]
    for e in soup.select('[data-id][data-tooltip]'):
        name=e['data-tooltip']
        if name.endswith('.pdf PDF'):
            items.append({'name':name.removesuffix(' PDF').strip(),'id':e['data-id'],'url':'https://drive.google.com/file/d/'+e['data-id']+'/view'})
    (ROOT/'sources').mkdir(exist_ok=True)
    result=list(ThreadPoolExecutor(max_workers=3).map(download,items))
    (ROOT/'data/sources.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
