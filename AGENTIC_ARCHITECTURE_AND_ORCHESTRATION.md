# Agentic Architecture and Orchestration

Короткий конспект по `Domain 1: Agentic Architecture and Orchestration`.

## 1.1 Agentic Loops

### Cross-Layer Mapping: Agentic Loop, `stop_reason`, Tool Use

- **Idea level:** Агент работает циклом: подумал -> если надо, вызвал инструмент -> увидел результат -> подумал снова -> закончил.
- **Language/API level:** После каждого ответа смотришь в `stop_reason`: `tool_use` = продолжать, `end_turn` = остановиться.
- **Planner/runtime level:** Модель сама решает, нужен ли следующий tool call или уже можно дать финальный ответ.
- **Context/history level:** Результат инструмента обязательно добавляется в историю сообщений, иначе модель на следующем шаге "не видит", что произошло.
- **Control-flow level:** Главный switch не текст ответа, а только `stop_reason`.
- **Safety level:** `MAX_ITERATIONS` можно держать только как предохранитель от зацикливания, не как основной способ остановки.
- **Anti-pattern level:** Нельзя останавливать цикл по "в ответе есть текст", по фразам типа "I'm done" или по тупому лимиту шагов.
- **Exam one-liner:** "Agentic loop управляется только через `stop_reason`: `tool_use` -> выполнить tool и вернуть результат в history, `end_turn` -> завершить."

### Супер-короткая формула

`tool_use` -> tool -> result in history -> send again  
`end_turn` -> stop

### Как запомнить на пальцах

- **Мозг агента** = модель
- **Руки агента** = tools
- **Память агента** = conversation history
- **Сигнал стопа** = `stop_reason`

### Одна фраза совсем в лоб

Агент не заканчивает, когда "написал текст", а заканчивает только когда API явно сказало: `end_turn`.

## 1.2 Orchestration Patterns

### Cross-Layer Mapping: Multi-Agent Orchestration, Coordinator, Subagents

- **Idea level:** Сложную задачу разбивает и собирает обратно один центральный агент, а остальные делают узкие подзадачи.
- **Architecture level:** Правильный паттерн тут `hub-and-spoke`: в центре `coordinator`, по краям `subagents`.
- **Communication level:** Все сообщения идут только через координатора; subagents не общаются друг с другом напрямую.
- **Context level:** Subagents изолированы: они не наследуют историю координатора и не шарят память между собой.
- **Prompt/input level:** Всё, что subagent должен знать, координатор обязан явно положить ему в prompt.
- **Routing level:** Координатор сам решает, каких subagents звать, и не гоняет каждую задачу через весь пайплайн без причины.
- **Decomposition level:** Главный риск не в "слабом subagent", а в слишком узкой разбивке задачи со стороны координатора.
- **Refinement level:** Если покрытие неполное, координатор должен перекинуть задачу заново: добрать пробелы и пересобрать результат.
- **Observability/control level:** Централизация нужна ради логов, единых ошибок и контроля, кто что знает.
- **Exam one-liner:** "В multi-agent системе координатор централизованно декомпозирует задачу, явно передает контекст изолированным subagents и маршрутизирует все общение только через себя."

### Супер-короткая формула

`Coordinator decides -> passes context -> subagents work -> results come back -> coordinator checks gaps -> repeats if needed`

### Как запомнить на пальцах

- **Координатор** = начальник и диспетчер
- **Subagents** = узкие исполнители
- **Общая память** = нет
- **Общий чат между subagents** = нет
- **Виновник дыр в покрытии** = чаще всего coordinator

### Одна фраза совсем в лоб

В multi-agent orchestration главный мозг системы это именно `coordinator`: он решает, кого вызвать, что передать и чего не хватает.

## 1.3 Guardrails & Safety

### Cross-Layer Mapping: Task Tool, Context Passing, Metadata, Parallel Spawning

- **Idea level:** Координатор не просто "хочет" вызвать subagent, а делает это через специальный механизм `Task`.
- **SDK/config level:** Если у координатора в `allowedTools` нет `Task`, он физически не может спавнить subagents.
- **Agent-definition level:** Каждый subagent задается через `AgentDefinition`: что делает, какой у него `system prompt`, и к каким tools у него есть доступ.
- **Context level:** Subagent получает только то, что координатор явно передал; автоматического доступа к history или к чужим результатам нет.
- **Data-passing level:** Передавать нужно не просто текст выводов, а структурированные findings: отдельно `content`, отдельно `metadata`.
- **Attribution level:** Если synthesis пишет claims без ссылок, проблема обычно не в synthesis, а в том, что координатор срезал `source_url` / `document_name` / `page_number`.
- **Parallelism level:** Независимые subagents надо запускать параллельно, то есть несколькими `Task` calls в одном ответе координатора.
- **Session level:** `fork_session` = новая независимая ветка от общей базы; `resume` = продолжение той же самой сессии.
- **Exam one-liner:** "Coordinator должен иметь `Task` в `allowedTools`, явно передавать subagents полный структурированный контекст с metadata и запускать независимые задачи параллельно."

### Супер-короткая формула

`No Task -> no subagents`  
`No metadata -> no citations`  
`Independent tasks -> parallel Task calls`

### Как запомнить на пальцах

- **`Task`** = кнопка "создать subagent"
- **`allowedTools`** = разрешение на эту кнопку
- **`metadata`** = паспорт источника
- **без metadata** = красивые, но "бесхозные" утверждения
- **parallel Task calls** = быстрее
- **`fork`** = новая ветка
- **`resume`** = продолжить старую

### Одна фраза совсем в лоб

Мало просто запустить subagent, надо еще правильно его вызвать, накормить контекстом и не потерять metadata.

## 1.5 Multi-Agent Systems

### Cross-Layer Mapping: Hooks, Enforcement, Normalization

- **Idea level:** Hooks нужны, чтобы в нужных местах сделать поведение системы не "примерно правильным", а строго контролируемым.
- **Lifecycle level:** Есть два места для hooks: `before tool execution` и `after tool execution`.
- **Pre-execution level:** `Tool call interception` hook срабатывает до запуска tool и может заблокировать, изменить или перенаправить вызов.
- **Post-execution level:** `PostToolUse` hook срабатывает после запуска tool, но до того, как результат увидит модель; он чистит и нормализует данные.
- **Policy/safety level:** Если правило должно соблюдаться в 100% случаев, нужен именно pre-execution hook, а не prompt.
- **Data level:** Если tools возвращают разные форматы дат, статусов, валют и т.д., это надо выравнивать через `PostToolUse`, а не оставлять на усмотрение модели.
- **Reliability level:** Hooks дают deterministic enforcement, prompts дают probabilistic behavior.
- **Exam one-liner:** "`Tool interception` блокирует или меняет вызов до выполнения, `PostToolUse` нормализует результат после выполнения; hooks нужны для 100% enforcement, prompts — только для предпочтений."

### Супер-короткая формула

`Before tool -> enforce policy`  
`After tool -> normalize data`

### Как запомнить на пальцах

- **Interception hook** = охранник у двери
- **PostToolUse hook** = уборщик после входа
- **Prompt** = просьба
- **Hook** = жесткое правило

### Одна фраза совсем в лоб

Если ошибка даже один раз недопустима, не надейся на prompt, ставь hook.

## 1.6 Human-in-the-Loop

### Cross-Layer Mapping: Task Decomposition, Fixed Pipeline, Attention Dilution

- **Idea level:** Сложную задачу надо правильно нарезать, иначе агент либо не адаптируется, либо начинает поверхностно смотреть часть материалов.
- **Pattern level:** Есть два паттерна: `fixed sequential pipeline` для предсказуемых задач и `dynamic adaptive decomposition` для открытых и исследовательских задач.
- **Fixed-flow level:** Если шаги известны заранее, делаешь фиксированную цепочку: шаг 1 -> шаг 2 -> шаг 3.
- **Adaptive-flow level:** Если по ходу всплывают новые зависимости и непонятки, план должен меняться на лету.
- **Attention level:** Если запихнуть слишком много файлов или объектов в один проход, возникает `attention dilution` — ранние элементы анализируются глубже, поздние хуже.
- **Architecture level:** Лечение attention dilution не в "умнее модель" и не в "лучше prompt", а в `multi-pass architecture`.
- **Local-pass level:** Сначала делаешь отдельный локальный проход по каждому файлу или объекту.
- **Integration-pass level:** Потом отдельно делаешь cross-file / cross-item проход на связи, консистентность и общие паттерны.
- **Exam one-liner:** "Для структурных задач используй fixed pipeline, для открытых расследований dynamic decomposition, а attention dilution лечится только multi-pass схемой: per-item passes + cross-item integration pass."

### Супер-короткая формула

`Known steps -> fixed pipeline`  
`Unknown scope -> adaptive decomposition`  
`Too many items in one pass -> multi-pass`

### Как запомнить на пальцах

- **Fixed pipeline** = конвейер
- **Dynamic decomposition** = расследование
- **Attention dilution** = внимание размазалось
- **Per-file pass** = лупа на один файл
- **Cross-file pass** = проверка связей между файлами

### Одна фраза совсем в лоб

Если задача предсказуемая, строй конвейер; если задача исследовательская, адаптируй план; если элементов слишком много, не пихай всё в один проход.

## 1.7 Error Recovery & Resilience

### Cross-Layer Mapping: Session Management, Stale Context, Resume vs Fork vs Fresh Start

- **Idea level:** Нужно правильно продолжать долгую работу: либо продолжить как есть, либо ответвиться, либо начать заново, но с краткой выжимкой.
- **Session-choice level:** Есть 3 режима: `--resume`, `fork_session`, `fresh start + summary injection`.
- **Continuation level:** `--resume` нужен, когда ты хочешь продолжить ту же самую работу и старый контекст все еще актуален.
- **Branching level:** `fork_session` нужен, когда база анализа уже есть, но теперь надо независимо сравнить разные подходы.
- **Fresh-start level:** `fresh start + summary injection` нужен, когда старые tool results устарели или история засорилась.
- **Staleness level:** Если после прошлой сессии файлы изменились, `resume` тащит в новый запуск старые tool results, и агент может начать путаться между старым и новым состоянием.
- **Recovery level:** Правильный фикс stale context не "resume и перечитай файлы", а новая сессия + краткое summary + точечный re-analysis измененных файлов.
- **Efficiency level:** Если изменились 3 файла из 50, не надо заново обходить все 50; нужен targeted re-analysis только измененных файлов.
- **Exam one-liner:** "`Resume` для продолжения, `fork` для независимого сравнения подходов, `fresh start + summary` для случаев, когда старый контекст протух из-за изменений."

### Супер-короткая формула

`No changes -> resume`  
`Compare approaches -> fork_session`  
`Files changed -> fresh start + summary`

### Как запомнить на пальцах

- **`resume`** = продолжить тот же разговор
- **`fork`** = ответвить новую ветку
- **fresh start** = начать с чистой головы
- **summary injection** = взять с собой только суть, а не весь старый мусор
- **stale context** = агент помнит старую версию файла и путается

### Одна фраза совсем в лоб

Если контекст еще живой, продолжай; если нужен выбор веток, форкай; если контекст протух, начинай заново, но с нормальной выжимкой.
