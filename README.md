# Agent Toolkit

Коллекция переносимых навыков и инструментов для AI-агентов.
Каждый навык хранится отдельно в `skills/<skill-name>/` и содержит `SKILL.md`
с инструкциями и необходимыми ресурсами. Новые навыки добавляются рядом,
не меняя способ установки существующих. Определения агентов и другие типы
материалов в дальнейшем можно разместить в отдельных каталогах;
`npx skills add` устанавливает именно навыки.

## Установка навыков

Нужны Node.js и `npx`. Установка выбранного навыка из GitHub:

```bash
npx skills add https://github.com/crowar/agent-toolkit --skill slides-generator
```

CLI предложит выбрать агентов и способ установки. По умолчанию установка
проектная; добавьте `--global`, если навык нужен во всех проектах.
Для явного выбора агентов:

```bash
npx skills add https://github.com/crowar/agent-toolkit \
  --skill slides-generator --agent github-copilot codex claude-code
```

Список доступных навыков без установки:

```bash
npx skills add https://github.com/crowar/agent-toolkit --list
```

Для будущих навыков замените `slides-generator` на значение `name` из их
`SKILL.md`. Отдельный npm-пакет и публикация в npm не требуются.
Установка навыка копирует инструкции и ресурсы, но не устанавливает Python,
Python-зависимости и авторизацию внешних сервисов.

## Доступные навыки

| Навык | Назначение |
|---|---|
| [slides-generator](skills/slides-generator/SKILL.md) | Исследование, согласование оглавления, редактируемый PowerPoint и речь выступающего |
| [otel-instrumentation](skills/otel-instrumentation/SKILL.md) | OpenTelemetry для frontend/mobile/backend, БД и брокеров; корреляция логов, traces и метрик |
| [presentations](skills/presentations/SKILL.md) | Автономные HTML-презентации и аккуратный перенос анкет в адаптивный формат |

## Presentations (HTML)

Навык находится в [`skills/presentations/`](skills/presentations/SKILL.md) и содержит
подробные правила структуры, навигации, оформления, переноса анкет и проверки
автономных HTML-презентаций.

```bash
npx skills add https://github.com/crowar/agent-toolkit --skill presentations
```

## OpenTelemetry Instrumentation

Навык находится в [skills/otel-instrumentation/SKILL.md](skills/otel-instrumentation/SKILL.md).
Он задаёт workflow подключения и проверки traces, структурированных логов и метрик
для frontend, мобильных приложений, backend и фоновых обработчиков. Включает
Microsoft SQL Server, PostgreSQL, Redis, другие БД, Kafka, RabbitMQ, внешние HTTP/RPC
и прочие вызываемые системы. Отдельно описаны связь логов с активным span,
метрики приложения и exemplars, защита данных и проверка доставки в хранилище.

```bash
npx skills add https://github.com/crowar/agent-toolkit --skill otel-instrumentation
```

Команда из GitHub станет доступна после коммита и push нового навыка. Для локальной
проверки используйте `npx skills add . --list` из корня `agent-toolkit`; для установки
из локальной копии: `npx skills add . --skill otel-instrumentation`.
Навык содержит инструкции и справочники, не устанавливает SDK/Collector автоматически
и не требует аккаунта конкретного поставщика мониторинга.

## Slides Generator

Пакет находится в [`skills/slides-generator/`](skills/slides-generator/SKILL.md).
Сам по себе генератор не проводит исследование: это задача агента и его
доступных инструментов.

### Возможности

- Три режима: исследовательский доклад, предложение идеи/проекта, отчёт.
- Основной дизайн — [Euclidean](https://www.figma.com/community/file/1387141600584938870/euclidean):
  19 исходных композиций, кремовая палитра, Source Serif Pro и Source Sans Pro.
- Интервью и выбор разрешённых источников при каждом запуске.
- Локальные материалы, NotebookLM, авторизованный Gartner и открытый интернет
  используются только в согласованных границах.
- Оглавление с описанием каждого слайда в 2–3 предложениях. До явного одобрения
  этой версии наполнение слайдов и написание речи запрещены.
- Результат: `presentation.pptx`, `speech.md`, `sources.md`. Речь также
  находится в заметках PowerPoint.
- Прежний бело-синий дизайн сохранён как `light-business` для старых презентаций.

### Дизайн Euclidean

Точная палитра, шрифты и координаты извлечены из предоставленного файла
Figma Slides, а не подобраны по превью. Источник геометрии —
[`assets/euclidean/layouts.json`](skills/slides-generator/assets/euclidean/layouts.json);
правила использования —
[`references/design.md`](skills/slides-generator/references/design.md).
Все композиции можно посмотреть на
[справочном листе Euclidean](skills/slides-generator/assets/euclidean/source-preview.png).
Это визуализация извлечённого исходного дизайна, не снимок PowerPoint.

Новые оглавления явно задают `"theme": "euclidean"` и выбирают нужные
`euclidean-*` композиции; все 19 использовать необязательно. У старых
оглавлений без `theme` сохраняется прежний дизайн, чтобы не менять
согласованные презентации незаметно.

Оригинальные шрифты с лицензиями находятся в
[`assets/fonts/`](skills/slides-generator/assets/fonts/).
**Установите их на компьютере, где будет открыт PowerPoint.** Генератор
использует поставляемые файлы для измерения текста, но не устанавливает
системные шрифты и не встраивает их в `.pptx`. Подмена на современные
Source Serif 4 / Source Sans 3 не требуется и автоматически не производится.

### Использование без Skills CLI

Скопируйте **целиком папку `skills/slides-generator`**, а не только `SKILL.md`, в каталог
навыков своего агента. Местоположение каталога зависит от агента и его версии;
проверьте его документацию. Пакет не устанавливается глобально автоматически.

Для работы без установки дайте агенту инструкцию:

> Прочитай skills/slides-generator/SKILL.md и используй этот навык для подготовки
> презентации. Начни с уточнения задачи и разрешённых источников.

Агенту нужны чтение локальных файлов и выполнение Python. Поиск, NotebookLM
и браузер нужны только при выборе соответствующих источников. Наличие навыка
NotebookLM не означает наличие авторизации; готового коннектора Gartner в
пакете нет.

### Локальный генератор

Из корня клонированного репозитория:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/slides-generator/requirements.txt
.venv/bin/python skills/slides-generator/scripts/render_deck.py --help
```

В Windows используется `.venv\Scripts\python.exe` вместо `.venv/bin/python`.
Не создавайте заново окружение, если оно уже существует и подходит.
Если навык установлен через `npx skills add`, замените `skills/slides-generator`
на путь установки, который показал CLI (например,
`.agents/skills/slides-generator` при проектной установке).
Создавайте виртуальное окружение в рабочем проекте, не внутри установленного
навыка: обновление навыка не должно затрагивать окружение и результаты работы.

Демонстрационный шаблон:

```bash
.venv/bin/python skills/slides-generator/scripts/render_deck.py template \
  --theme euclidean --output-dir preview
```

Готовый образец поставляется в
[`skills/slides-generator/assets/template.pptx`](skills/slides-generator/assets/template.pptx).
Это 19 композиций исходника с заполнителями и условными данными, а не
исследование и не готовая содержательная презентация. Для новых презентаций
генератор использует сохранённую геометрию; он не копирует бинарный файл образца.
Произвольные `.deck` и корпоративные `.pptx` как входные шаблоны CLI
не поддерживаются: Euclidean предварительно извлечён и включён в пакет.

Каталог полей для наполнения:

```bash
.venv/bin/python skills/slides-generator/scripts/render_deck.py catalog \
  --theme euclidean
```

Для прежнего образца используйте `template --theme light-business`.

Сборка после согласования:

```bash
.venv/bin/python skills/slides-generator/scripts/render_deck.py outline-hash \
  --outline output/outline.json
.venv/bin/python skills/slides-generator/scripts/render_deck.py render \
  --outline output/outline.json \
  --approval output/approval.json \
  --content output/content.json \
  --output-dir output/final
```

Схемы файлов и правила фиксации согласования описаны в
[`references/data-contract.md`](skills/slides-generator/references/data-contract.md).
Генератор проверяет соответствие версии и контрольной суммы, но не может
доказать, что одобрение действительно дал человек. Эту границу обязан
соблюдать агент: нельзя самостоятельно создавать согласие пользователя.

### Ограничения

Генератор работает локально и не подключается к источникам. Он не проверяет
истинность утверждений и права на распространение материалов. Длинный текст
нужно сокращать или перераспределять с повторным согласованием, а не уменьшать
до нечитаемого размера.

Пустые панели можно заполнить согласованными локальными PNG/JPEG через
`body.images` и `image_slots` из каталога; автоматического поиска иллюстраций
нет. Изображения вписываются в исходные панели без растяжения. Позиции
полос таймлайна и индикаторы чек-листа сохраняют демонстрационный вид.
Не используйте их для данных, которым эта геометрия не соответствует.
Ссылки на источники Euclidean сохраняет в заметках и реестре без добавления
отсутствующих в дизайне визуальных подвалов.

Перед выступлением откройте презентацию в целевой версии PowerPoint:
замена шрифтов и особенности рендеринга могут изменить переносы. Автоматическая
проверка структуры не заменяет просмотр слайдов. Заметки входят в `.pptx`;
перед внешней отправкой также проверьте их на конфиденциальные сведения.
