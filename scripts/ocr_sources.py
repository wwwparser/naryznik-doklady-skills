from pathlib import Path
import json, subprocess, re, hashlib
from concurrent.futures import ThreadPoolExecutor
import fitz, requests
ROOT=Path(__file__).resolve().parents[1]
TMP=ROOT/'tmp/ocr'
TESS=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def process(job):
    source, number=job
    key=hashlib.sha256(source.name.encode()).hexdigest()[:12]+f'-{number}'
    output=TMP/(key+'.txt')
    if not output.exists():
        with fitz.open(source) as doc:
            image=TMP/(key+'.png')
            doc[number-1].get_pixmap(matrix=fitz.Matrix(1.8,1.8)).save(image)
        subprocess.run([TESS,str(image),str(output.with_suffix('')),'--tessdata-dir',str(TMP),'-l','rus+eng','--psm','11'],check=True,capture_output=True)
    return (source.stem,number,output.read_text(encoding='utf-8'))
if __name__=='__main__':
    TMP.mkdir(parents=True,exist_ok=True)
    for lang in ['rus','eng']:
        dest=TMP/(lang+'.traineddata')
        if not dest.exists():
            r=requests.get(f'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/{lang}.traineddata',timeout=60);r.raise_for_status();dest.write_bytes(r.content)
    inventory=json.loads((ROOT/'data/sources.json').read_text(encoding='utf-8'))
    docs={};jobs=[]
    for item in inventory:
        source=ROOT/'sources'/item['name']; stem=source.stem
        obj=json.loads((ROOT/'data/extracted'/f'{stem}.json').read_text(encoding='utf-8'));docs[stem]=obj
        for p in obj['pages']:
            clean=re.sub(r'БОЛЬШОЙ НАРИЖНИК|ИЛЬЯНА ЛЕВИНА|ИНСТРУМЕНТЫ МАРКЕТОЛОГА|\s+','',p['text'])
            if len(clean)<100:jobs.append((source,p['page']))
    print('OCR pages',len(jobs),flush=True)
    for stem,number,text in ThreadPoolExecutor(max_workers=4).map(process,jobs):
        page=docs[stem]['pages'][number-1];page['ocr_text']=text
        if len(text.strip())>len(page['text'].strip()):page['text']=text
        page['method']='local-tesseract'
        print(stem,number,flush=True)
    for stem,obj in docs.items(): (ROOT/'data/extracted'/f'{stem}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
