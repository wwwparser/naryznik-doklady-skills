# Нарижник / Практика

База знаний по 19 презентациям «Большого Нарижника»: 892 страницы исходного корпуса, разборы, применение, технические сценарии, 19 промтов и 19 предложений по навыкам Codex.

Сайт: https://wwwparser.github.io/naryznik-doklady-skills/

## Просмотр локально

Из корня запустить `python -m http.server 8000 --directory public`, открыть http://localhost:8000.

## Состав

- `public/` — каталог, 19 отдельных разборов, обзор, идеи навыков и методика.
- `data/talks.json` — редакционные карточки; `data/sources.json` — реестр оригиналов.
- `sources/` и `data/extracted/` — локальные PDF и текст, исключены из Git.
- `scripts/author_talks.py` — авторский источник карточек.
- `scripts/build_site.py` — генератор HTML.
- `scripts/download_sources.py`, `extract_pdf.py`, `ocr_sources.py` — подготовка корпуса.
- `docs/` — план, варианты реализации, статус и проверка.
- `artifacts/site-review/` — локальные снимки и измерения браузера.

## Обновление

После анализа обновить `scripts/author_talks.py`, выполнить `python scripts/author_talks.py` и `python scripts/build_site.py`. Для обработки PDF нужны зависимости `requirements.txt`; OCR использует Tesseract. Браузерная проверка `scripts/check_site.py` требует установленного Playwright и Chrome.

Исходники — ветка `main`. GitHub Pages обслуживает только `public/`, вынесенную в `gh-pages` командой `git subtree push --prefix public origin gh-pages`.

## Ограничения

Тексты и смысловой анализ подготовлены Codex. Предложения навыков ещё не являются установленными навыками. Кейсы и проценты спикеров не представлены как гарантии. Записи выступлений и дополнительные материалы по QR не изучались. Актуальные тарифы, правила площадок и API проверять перед внедрением. Оригинальные PDF не опубликованы повторно: сайт ссылается на Drive.
