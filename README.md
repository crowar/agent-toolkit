# Agent Toolkit

Коллекция переносимых навыков и инструментов для AI-агентов.
Навыки этого набора хранятся в `skills/<skill-name>/` и содержат `SKILL.md`
с инструкциями и ресурсами. `npx skills add` устанавливает именно навыки.

## Установка навыков

Для установки нужны Node.js, npm и `npx`. Установить `npx skills` отдельно не нужно:
`npx` скачает и запустит CLI `skills` при первом вызове. Проверьте, что Node.js и
`npx` доступны:

```bash
node --version
npx --version
```

Если команды отсутствуют, установите актуальную LTS-версию
[Node.js](https://nodejs.org/), в комплект которой входят npm и `npx`.

Установка выбранного навыка из GitHub:

```bash
npx skills add https://github.com/crowar/agent-toolkit --skill presentations
```

CLI предложит выбрать агентов и способ установки. По умолчанию установка
проектная; добавьте `--global`, если навык нужен во всех проектах.
Для явного выбора агентов:

```bash
npx skills add https://github.com/crowar/agent-toolkit \
  --skill presentations --agent github-copilot codex claude-code
```

Список доступных навыков без установки:

```bash
npx skills add https://github.com/crowar/agent-toolkit --list
```

Для установки другого навыка укажите его значение `name` из `SKILL.md`.
Отдельный npm-пакет и публикация в npm не требуются.
Установка навыка копирует инструкции и ресурсы, но не устанавливает Python,
Python-зависимости и авторизацию внешних сервисов.

## Доступные навыки

Ниже приведены навыки по направлению. Ссылка на название ведет на страницу
навыка с подробными инструкциями; команда рядом устанавливает этот навык.

### Технические навыки

#### CI и качество кода

- [fix-ci-failures](skills/fix-ci-failures/SKILL.md) — диагностика GitLab CI,
  unit-тестов, замечаний SonarQube и обсуждений code review.
  `npx skills add https://github.com/crowar/agent-toolkit --skill fix-ci-failures`

#### Наблюдаемость

- [otel-instrumentation](skills/otel-instrumentation/SKILL.md) — OpenTelemetry
  для frontend, mobile, backend, баз данных и брокеров; traces, логи и метрики.
  `npx skills add https://github.com/crowar/agent-toolkit --skill otel-instrumentation`

### Подготовка контента и презентаций

- [presentations](skills/presentations/SKILL.md) — автономные HTML-презентации
  и перенос анкет в адаптивный формат.
  `npx skills add https://github.com/crowar/agent-toolkit --skill presentations`
