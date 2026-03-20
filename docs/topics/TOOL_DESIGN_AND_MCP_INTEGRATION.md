# Tool Design & MCP Integration

Короткий конспект по `Domain 2: Tool Design & MCP Integration`.

## 2.1 Tool Schema Design

### Cross-Layer Mapping: Tool Descriptions, Misrouting, Boundaries

- **Idea level:** Модель выбирает tools в первую очередь по их описаниям, поэтому описание инструмента это не декоративный текст, а главный механизм выбора.
- **Schema/definition level:** Хорошее описание должно включать 5 вещей: что tool делает, какие входы принимает, примеры запросов, ограничения и явные границы с похожими tools.
- **Selection level:** Если описания короткие и похожие, модель начинает путать инструменты и отправлять запросы не туда.
- **Disambiguation level:** Самая важная часть описания это не только "что делает tool", но и "когда НЕ использовать этот tool, а использовать другой".
- **Design level:** Если один tool слишком общий и расплывчатый, его лучше дробить на несколько purpose-specific tools с узкой задачей.
- **Naming level:** Если названия tools похожи или расплывчаты, переименование тоже помогает убрать путаницу даже без смены реализации.
- **Prompt-interaction level:** Даже хорошие descriptions может сломать system prompt, если в нем есть keyword-sensitive инструкции, которые толкают модель к неправильному tool.
- **Optimization level:** При misrouting первый фикс почти всегда не classifier и не consolidation, а улучшение descriptions.
- **Exam one-liner:** "Tool descriptions — основной механизм tool selection; при misrouting сначала улучшают descriptions, уточняют boundaries и проверяют system prompt на конфликтующие инструкции."

### Супер-короткая формула

`Bad descriptions -> misrouting`  
`Clear boundaries -> better tool selection`  
`Fix descriptions first`

### Как запомнить на пальцах

- **Tool description** = инструкция для модели, какой ключ куда подходит
- **Boundary** = табличка "не сюда, а в соседнюю дверь"
- **Few-shot** = костыль, если описание уже хреновое
- **Routing classifier** = тяжелая артиллерия, не первый шаг
- **Tool split** = разделить швейцарский нож на нормальные инструменты

### Главное различие

- **Проблема в выборе между tools** -> сначала перепиши descriptions
- **Один tool делает слишком много разного** -> split into smaller tools
- **Названия похожи и путают** -> rename for clarity

### Главная экзаменационная ловушка

Если модель путает `get_customer` и `lookup_order`, не надо первым делом лепить few-shot, classifier или один супер-tool. Сначала надо нормально описать оба инструмента.

### Одна фраза совсем в лоб

LLM выбирает инструмент в основном по описанию, так что плохой tool description = плохой routing.

## 2.2 MCP Server Implementation

### Cross-Layer Mapping: Structured Errors, `isError`, Recovery Paths

- **Idea level:** Когда tool падает, важно не просто сообщить "ошибка", а дать агенту понять, что именно случилось и как на это реагировать.
- **Protocol level:** В MCP для этого есть `isError`; он явно сообщает модели, что tool execution провалился, а не вернул обычный результат.
- **Classification level:** Ошибки надо делить минимум на 4 типа: `transient`, `validation`, `business`, `permission`.
- **Recovery level:** У каждого типа свой recovery path: `transient` -> retry, `validation` -> исправить input, `business` -> не retry, а alternative workflow / escalation, `permission` -> получить доступ или эскалировать.
- **Metadata level:** Одного текста ошибки мало; нужны структурированные поля вроде `errorCategory`, `isRetryable`, `description`.
- **Semantic level:** Критически важно различать `access failure` и `valid empty result`: первое значит "не смогли проверить", второе значит "проверили и ничего не нашли".
- **Agent-behavior level:** Если tool не различает empty result и failure, агент начинает зря ретраить, зря эскалировать и вообще принимает неправильные решения.
- **Multi-agent level:** Subagent должен по возможности чинить transient failures локально, а наверх отправлять только нерешенные ошибки, причем с partial results и описанием, что уже было попробовано.
- **Exam one-liner:** "Хороший MCP tool возвращает не просто текст ошибки, а структурированный error result через `isError` + metadata, чтобы агент мог отличить retryable failures от permanent/business failures и не путал их с valid empty results."

### Супер-короткая формула

`isError = true -> tool failed`  
`empty result != failure`  
`error type decides recovery`

### Как запомнить на пальцах

- **`isError`** = красная лампа "tool реально сломался"
- **`transient`** = попробуй еще раз
- **`validation`** = ты криво спросил
- **`business`** = правило запрещает, повторять бесполезно
- **`permission`** = у тебя нет допуска
- **empty result** = дверь открылась, но внутри никого нет
- **access failure** = ты вообще в здание не попал

### Главное различие

- **`isError: false` + `resultCount: 0`** -> запрос успешно выполнился, просто данных нет
- **`isError: true`** -> tool не смог корректно выполнить запрос

### Главная экзаменационная ловушка

Если после lookup пришел пустой результат, это не значит, что надо retry. Сначала надо понять: база была реально опрошена и ничего не нашла, или tool вообще не смог до нее достучаться.

### Одна фраза совсем в лоб

Пустой результат это не ошибка; ошибка это когда tool не смог надежно проверить данные.

## 2.3 MCP Client Integration

### Cross-Layer Mapping: Tool Scoping, `tool_choice`, Scoped Cross-Role Tools

- **Idea level:** Чем больше tools ты даешь одному агенту, тем хуже он их выбирает; tool distribution это архитектурное решение, а не мелкая настройка.
- **Scoping level:** Нормальный ориентир это `4-5 tools per agent`, причем только под роль конкретного агента.
- **Role level:** Search agent должен иметь search tools, synthesis agent должен иметь synthesis tools; если дать лишнее, агент начнет лезть в чужую работу и дублировать шаги.
- **Selection-complexity level:** 18 tools у одного агента = перегрузка выбора, больше decision complexity и больше misrouting.
- **`tool_choice` level:** `auto` = модель сама решает, нужен ли tool; `any` = обязательно вызвать какой-то tool; `tool`/forced = обязательно вызвать конкретный tool.
- **Workflow-ordering level:** Forced selection используют, когда шаг обязателен и его нельзя пропустить или переставить местами.
- **Structured-output level:** `any` нужен, когда нельзя допустить plain-text ответ и нужен гарантированный structured output через один из tools.
- **Latency level:** Если 85% запросов это простые проверки, не надо каждый раз гонять их через coordinator; лучше дать агенту scoped cross-role tool для простого кейса.
- **Least-privilege level:** Вместо общего `fetch_url` лучше давать ограниченный `load_document`, который умеет только нужный и безопасный поднабор действий.
- **Exam one-liner:** "Инструменты нужно жестко скоупить по ролям, держать примерно `4-5` на агента, использовать правильный `tool_choice`, а частые простые cross-role операции закрывать scoped tools вместо лишних coordinator round-trips."

### Супер-короткая формула

`Too many tools -> worse selection`  
`4-5 tools per role -> better reliability`  
`Simple frequent cross-role task -> scoped tool`

### Как запомнить на пальцах

- **4-5 tools** = рабочий набор
- **18 tools** = швейцарский склад, агент тупит
- **`auto`** = сам решай
- **`any`** = обязательно возьми какой-то инструмент
- **forced tool** = бери именно этот инструмент
- **scoped cross-role tool** = маленький пропуск в соседний отдел
- **least privilege** = дай ровно столько доступа, сколько реально нужно

### Главное различие

- **Нужна свободная обычная работа** -> `tool_choice: auto`
- **Нужно гарантировать хоть какой-то structured tool output** -> `tool_choice: any`
- **Нужно заставить выполнить конкретный первый шаг** -> forced specific tool

### Главная экзаменационная ловушка

Если synthesis agent часто уходит к coordinator ради простых проверок, не надо сразу ускорять coordinator. Обычно правильнее дать synthesis агенту маленький ограниченный `verify_fact` для простых кейсов.

### Одна фраза совсем в лоб

Чем уже и чище набор tools у агента, тем надежнее его поведение.

## 2.4 Tool Error Handling

Note: в исходном материале под этим заголовком по смыслу идет не `error handling`, а именно `MCP server configuration and scoping`.

### Cross-Layer Mapping: MCP Configuration, Scoping, Resources, Reuse vs Build

- **Idea level:** MCP servers надо подключать так, чтобы команда делила общий toolset без хаоса в конфигурации и без утечки секретов.
- **Scoping level:** Есть два уровня конфигурации: project-level `.mcp.json` и user-level `~/.claude.json`.
- **Team-sharing level:** `.mcp.json` лежит в репозитории, version-controlled и шарится на команду; сюда кладут team-wide integrations.
- **Personal level:** `~/.claude.json` личный, не version-controlled и не шарится; сюда кладут персональные или экспериментальные servers.
- **Discovery level:** Все tools со всех подключенных servers доступны одновременно при connection time; ручной "активации" по сути нет.
- **Secrets level:** Секреты нельзя хардкодить в `.mcp.json`; надо использовать `${ENV_VAR}` expansion, чтобы конфиг был общий, а credentials локальные.
- **Resource level:** MCP resources показывают агенту каталог доступного контента заранее, чтобы он не тратил tool calls на тупое исследование "а что вообще доступно?".
- **Integration-strategy level:** Для стандартных интеграций сначала смотрят community servers; custom MCP server строят только если есть специфичные командные workflow или проприетарные системы.
- **Tool-competition level:** Если MCP tool описан бедно, модель может предпочесть built-in tools; поэтому MCP descriptions тоже должны быть богатыми и конкретными.
- **Exam one-liner:** "Team-wide MCP servers кладут в `.mcp.json`, personal ones — в `~/.claude.json`, секреты передают через `${ENV_VAR}`, ресурсы используют для каталога данных, а community servers проверяют раньше custom build."

### Супер-короткая формула

`.mcp.json -> shared`  
`~/.claude.json -> personal`  
`${ENV_VAR} -> no secrets in git`

### Как запомнить на пальцах

- **`.mcp.json`** = общий шкаф команды
- **`~/.claude.json`** = твой личный ящик
- **`${TOKEN}`** = ссылка на секрет, а не сам секрет
- **resource** = витрина "вот какие данные вообще есть"
- **community server** = готовое решение
- **custom server** = пилим сами только если реально надо

### Главное различие

- **Нужно всей команде** -> `.mcp.json`
- **Нужно только тебе или это эксперимент** -> `~/.claude.json`
- **Стандартный Jira/GitHub/Slack use case** -> сначала community server
- **Уникальная внутренняя логика или proprietary system** -> custom server

### Главная экзаменационная ловушка

Не надо первым делом строить свой MCP server для стандартной штуки вроде Jira. Правильный первый шаг почти всегда: посмотреть, есть ли нормальный community server.

### Одна фраза совсем в лоб

Хорошая MCP-конфигурация это общий конфиг для команды, локальные секреты через env vars и минимум самописщины без необходимости.

## 2.5 Tool Selection & Routing

### Cross-Layer Mapping: Grep vs Glob, Edit vs Read/Write, Incremental Discovery

- **Idea level:** У каждого built-in tool есть своя роль, и если путать их, ты тратишь лишние токены, время и получаешь неправильный workflow.
- **Search level:** `Grep` ищет содержимое файлов, а `Glob` ищет сами файлы по имени, маске или пути.
- **Content-vs-path level:** Если ищешь function callers, import statements, error messages или usage patterns, это `Grep`; если ищешь `*.test.tsx`, `config.*` или файлы в конкретной папке, это `Glob`.
- **Modification level:** Для точечных правок сначала пробуют `Edit`, потому что он дешевле по контексту и точнее.
- **Fallback level:** Если `Edit` не может надежно отработать из-за неуникального совпадения, тогда fallback это `Read + Write`.
- **Exploration level:** Кодовую базу нельзя читать всю сразу; правильный путь это incremental discovery: сначала `Grep`, потом `Read` только нужных файлов, потом снова `Grep` по новым зацепкам.
- **Tracing level:** Если функция идет через wrapper или barrel file, одного поиска по исходному имени мало; надо читать экспорт и потом grep-ить уже экспортируемые имена и точки импорта.
- **Refactor-workflow level:** Типичный паттерн для deprecated API: сначала `Grep` ищет всех callers, потом `Glob` находит тесты этих callers, потом `Read`, потом `Edit`, и только если надо `Read + Write`.
- **Efficiency level:** Ошибка "read all files upfront" убивает context budget и считается архитектурно неправильным способом исследования кодовой базы.
- **Exam one-liner:** "`Grep` ищет внутри файлов, `Glob` ищет файлы по пути, кодовую базу изучают инкрементально, а для изменений сначала используют `Edit`, а `Read + Write` оставляют как fallback."

### Супер-короткая формула

`Inside files -> Grep`  
`File paths/names -> Glob`  
`Try Edit first -> fallback Read + Write`

### Как запомнить на пальцах

- **`Grep`** = что написано внутри
- **`Glob`** = как файл называется и где лежит
- **`Read`** = посмотреть целиком
- **`Edit`** = точечно заменить
- **`Write`** = переписать файл целиком
- **incremental discovery** = не жри весь проект сразу, иди по следам

### Главное различие

- **Ищу вызовы `processLegacyOrder()`** -> `Grep`
- **Ищу test files этих модулей** -> `Glob`
- **Надо заменить одну сигнатуру или вызов** -> сначала `Edit`
- **`Edit` не сработал из-за неуникального текста** -> `Read + Write`

### Главная экзаменационная ловушка

Нельзя использовать `Glob` для поиска function callers, потому что он не смотрит внутрь файлов. И нельзя по умолчанию открывать все файлы проекта или всегда редактировать через `Read + Write`.

### Одна фраза совсем в лоб

`Grep` = внутри файлов, `Glob` = сами файлы, `Edit` = сначала, `Read + Write` = только если без этого уже никак.
