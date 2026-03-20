# Context Management & Reliability

Короткий конспект по `Domain 5: Context Management & Reliability`.

## 5.1 Context Window Management

### Cross-Layer Mapping: Persistent Facts, Summarisation Trap, Context Trimming

- **Idea level:** Надежность long-running agent systems зависит от того, что именно ты сохраняешь в контексте, что режешь и что никогда не даешь потерять.
- **Summarisation level:** Progressive summarisation опасна для transactional data, потому что она первой выкидывает точные суммы, даты, order IDs и статусы.
- **Critical-facts level:** Для таких данных нужен `persistent case facts block`, который живет отдельно от summarised history и всегда кладется в prompt.
- **Multi-issue level:** Если в разговоре несколько проблем, факты по каждой issue надо хранить структурированно отдельно, чтобы они не смешивались при summarisation.
- **Positioning level:** Есть эффект `lost in the middle`: важные вещи в середине длинного input модель замечает хуже, поэтому key findings надо ставить в начало.
- **Structure level:** Решение для long context не "просто напомнить модели быть внимательной", а структурировать input: сначала summary of key findings, потом подробности с четкими section headers.
- **Tool-output level:** Verbose tool results быстро убивают token budget; их надо trim-ить до реально нужных полей до того, как они попадут в conversation history.
- **Stateless-API level:** API stateless, поэтому каждый request должен включать весь нужный контекст; нельзя безболезненно просто выкидывать куски истории.
- **Upstream-agent level:** В multi-agent системах upstream agents должны возвращать downstream не простыни рассуждений, а структурированные findings с metadata.
- **Exam one-liner:** "Главный паттерн управления контекстом — persistent case facts block: суммы, даты, IDs и статусы хранятся отдельно от summarised history; tool outputs trim-ятся, а key findings выносятся в начало input."

### Супер-короткая формула

`Summaries lose specifics`  
`Critical facts -> persistent block`  
`Verbose tool output -> trim early`

### Как запомнить на пальцах

- **summary** = короткий пересказ, а не надежное хранилище фактов
- **case facts block** = несгораемый сейф для сумм, дат и ID
- **lost in the middle** = середину длинного текста хуже замечают
- **trim tool results** = не тащи весь мусор в следующий turn
- **stateless API** = каждый раз неси с собой весь нужный смысл

### Главное различие

- **Narrative history** -> можно summarise
- **Amounts / dates / order IDs / statuses** -> нельзя терять, держим в persistent block
- **Полный raw tool output** -> плохо
- **Trimmed relevant fields** -> правильно

### Главная экзаменационная ловушка

Нельзя думать, что summarisation безопасна для транзакционных данных. Именно самые важные числа и идентификаторы она и сжирает в первую очередь.

### Одна фраза совсем в лоб

Все, что нельзя забыть, не должно жить только в summary.

## 5.2 Prompt Caching

Note: в исходном материале под этим заголовком по смыслу идет не `prompt caching`, а `escalation calibration for support agents`.

### Cross-Layer Mapping: Escalation Criteria, Human Handoff, Bad Triggers

- **Idea level:** Качество support agent сильно зависит от того, когда он эскалирует к человеку, а когда нормально решает проблему сам.
- **Valid-trigger level:** Есть 3 нормальных причины эскалации: customer explicitly asks for a human, policy gap/exception, inability to make meaningful progress.
- **Absolute-rule level:** Если клиент прямо просит человека, эскалация должна происходить сразу, без попытки "сначала я попробую помочь сам".
- **Policy level:** Надо различать `policy violation` и `policy gap`: violation может иметь четкий ответ по правилам, а gap значит, что политика вообще не покрывает кейс и нужен человек.
- **Progress level:** "Не могу продвинуться" считается валидной причиной только если агент реально попробовал решить кейс и застрял, а не просто заранее испугался.
- **Bad-trigger level:** Frustration/sentiment и self-reported confidence — плохие триггеры эскалации, потому что они плохо коррелируют с реальной сложностью кейса.
- **Frustration nuance level:** Раздраженный клиент с простой проблемой не требует эскалации автоматически; если кейс решаем, надо признать frustration и предложить решение.
- **Disambiguation level:** Если customer lookup вернул несколько совпадений, нельзя выбирать "самый свежий" или "самый активный" аккаунт; надо просить дополнительные identifiers.
- **Prompt-design level:** Самый пропорциональный первый фикс плохой escalation calibration — прописать explicit escalation criteria в system prompt и добавить few-shot examples.
- **Exam one-liner:** "Эскалировать надо по явному запросу человека, policy gaps и реальному отсутствию прогресса; sentiment и self-confidence для этого ненадежны, а ambiguous customer matches требуют уточнения, а не эвристического выбора."

### Супер-короткая формула

`Ask for human -> escalate now`  
`Policy gap -> escalate`  
`Frustration alone -> not enough`

### Как запомнить на пальцах

- **explicit human request** = без разговоров передаем человеку
- **policy gap** = правила молчат, нужен человек
- **can't progress** = пытались, но реально уперлись
- **sentiment** = эмоция, а не сложность
- **confidence** = плохой компас
- **multiple customer matches** = спроси еще ID, не угадывай

### Главное различие

- **Клиент злой, но кейс простой** -> решай, не эскалируй автоматически
- **Клиент спокойно просит policy exception** -> может понадобиться эскалация
- **Клиент говорит "хочу человека"** -> сразу эскалация
- **Несколько John Smith в базе** -> запросить email / phone / order ID

### Главная экзаменационная ловушка

Нельзя строить эскалацию на sentiment score или confidence threshold. Это красиво звучит, но на практике агент будет эскалировать простые кейсы и лезть в сложные.

### Одна фраза совсем в лоб

Эскалация должна опираться на четкие правила и явные границы, а не на эмоции клиента или "ощущение уверенности" модели.

## 5.3 Long Conversations

Note: в исходном материале под этим заголовком по смыслу идет не `long conversations`, а `structured error propagation in multi-agent systems`.

### Cross-Layer Mapping: Error Propagation, Partial Failure, Recovery Transparency

- **Idea level:** Надежность multi-agent системы зависит от того, как subagent сообщает о провале наверх: прозрачно и структурированно или молча и бесполезно.
- **Error-context level:** Хороший error propagation должен включать 4 вещи: тип ошибки, что именно пытались сделать, какие partial results уже есть, и какие есть alternative approaches.
- **Failure-type level:** Ошибки надо различать по типам: `transient`, `validation`, `business`, `permission`, потому что recovery path у них разный.
- **Coordinator level:** Coordinator не должен получать абстрактное "search unavailable"; он должен понимать, какой был query, что уже получилось, и что можно попробовать дальше.
- **Anti-pattern level:** Самый опасный анти-паттерн это `silent suppression`: subagent словил timeout, но вернул пустой результат как будто все успешно.
- **Pipeline-resilience level:** Второй анти-паттерн это `workflow termination`: убивать весь pipeline из-за одного subagent failure, теряя все остальные уже собранные результаты.
- **Access-vs-empty level:** Критично различать `access failure` и `valid empty result`: первое значит "не смогли выполнить query", второе значит "query выполнился, но совпадений нет".
- **Local-recovery level:** Transient failures сначала должны пытаться чиниться локально внутри subagent через retries/fallbacks, и только потом подниматься к coordinator.
- **Coverage-transparency level:** Если часть темы не покрыта из-за failures, synthesis должен это явно отметить через coverage annotations, а не молча делать вид, что темы просто нет.
- **Exam one-liner:** "Subagents должны поднимать наверх структурированный error context с partial results и alternatives; нельзя ни молча возвращать empty success, ни валить весь pipeline из-за одной ошибки, и обязательно надо различать access failure от valid empty result."

### Супер-короткая формула

`Failure -> propagate context, not silence`  
`Access failure != empty result`  
`One subagent fail != kill whole pipeline`

### Как запомнить на пальцах

- **structured error** = что сломалось, что пробовали, что успели добыть, что можно сделать дальше
- **silent suppression** = соврать, будто ничего не нашли
- **workflow termination** = психануть и уронить весь конвейер
- **partial results** = уже добытая полезная часть
- **coverage annotation** = честно отметить, где есть пробелы

### Главное различие

- **Timeout / connection issue** -> access failure, подумай про retry
- **Query успешно отработал, но пусто** -> valid empty result, retry не нужен
- **Один subagent упал** -> targeted recovery / partial continuation
- **Все результаты спрятали за generic error** -> coordinator слепой

### Главная экзаменационная ловушка

Нельзя ловить timeout и возвращать пустой `success`. Это делает вид, что данных нет, хотя на самом деле система даже не смогла проверить.

### Одна фраза совсем в лоб

Если subagent сломался, coordinator должен получить не туман, а нормальный отчет о том, что произошло и что делать дальше.

## 5.4 Rate Limiting & Quotas

Note: в исходном материале под этим заголовком по смыслу идет не `rate limiting`, а `context degradation during large codebase exploration`.

### Cross-Layer Mapping: Context Degradation, Scratchpads, Delegation, Recovery State

- **Idea level:** При длинном исследовании большой кодовой базы агент начинает забывать конкретику не потому, что "токены кончились", а потому что контекст деградирует под слоем verbose output.
- **Degradation level:** Симптом простой: вместо конкретных классов, файлов и dependency chains агент начинает говорить общими фразами типа "typical repository pattern".
- **Root-cause level:** Проблема не в размере окна сама по себе, а в том, что новые file dumps, search results и listings закапывают старые точные находки.
- **Primary-mitigation level:** Главный фикс это `scratchpad files`: ключевые findings пишутся во внешний файл и потом читаются заново, а не держатся только в разговорном контексте.
- **Delegation level:** Subagent delegation нужна тут не только ради parallelism, а в первую очередь ради `context isolation`: coordinator держит чистый high-level context, subagents переваривают шум.
- **Phase-transition level:** Между фазами исследования нужен `summary injection`, чтобы Phase 2 subagents не начинали с нуля и не дублировали уже сделанную разведку.
- **Compaction level:** Команда `/compact` нужна не только когда все уже забито, а proactively, чтобы поддерживать качество контекста по ходу длинной сессии.
- **Crash-recovery level:** Для длинных exploration sessions нужен state manifest: что уже исследовано, что найдено, какая фаза, что дальше.
- **Resume level:** При возобновлении coordinator загружает manifest и подает его в prompts, чтобы не исследовать кодовую базу заново.
- **Exam one-liner:** "Контекстная деградация в codebase exploration лечится не большим context window, а scratchpad files, context-isolated subagents, phase summaries, `/compact` и state manifests для resume."

### Супер-короткая формула

`Verbose exploration -> context degradation`  
`Key findings -> scratchpad`  
`Long session -> save state`

### Как запомнить на пальцах

- **context degradation** = память замылилась
- **scratchpad** = внешний блокнот с фактами
- **subagents** = отдельные исследователи, не засоряют голову coordinator
- **summary injection** = передай следующей фазе, что уже узнали
- **`/compact`** = вовремя подчищай контекст
- **manifest** = сохранение игры перед вылетом

### Главное различие

- **Проблема: агент стал слишком общо говорить** -> context degradation
- **Решение: больше context window** -> обычно мимо
- **Решение: scratchpad + delegation + state persistence** -> правильно

### Главная экзаменационная ловушка

Нельзя лечить context degradation просто увеличением context window. Если ты продолжаешь закидывать модель шумом, она и в большом окне так же потеряет конкретику.

### Одна фраза совсем в лоб

Если исследование долгое, держи факты вне чата: в scratchpad, summary и manifest, иначе агент начнет говорить общими словами вместо точных находок.

## 5.5 Monitoring & Observability

### Cross-Layer Mapping: Aggregate Metrics Trap, Calibration, Sampling, Review Prioritisation

- **Idea level:** Human review нужен не "вообще", а умно: ограниченную проверку надо направлять туда, где она реально ловит ошибки и снижает риск.
- **Metrics level:** Самая опасная ошибка это смотреть только на aggregate accuracy; высокий общий процент может скрывать провал на отдельных типах документов и полях.
- **Segmentation level:** Accuracy надо мерить не в среднем по больнице, а по `document type` и `field segment`.
- **Confidence level:** Raw model confidence сам по себе ненадежен; один и тот же `0.90` может означать разную реальную точность для разных полей и типов документов.
- **Calibration level:** Поэтому confidence thresholds надо калибровать на `labelled validation sets`, где есть ground truth.
- **Routing level:** Только после калибровки confidence можно использовать для routing: что автоматизировать, что слать человеку, а что держать в ambiguous zone.
- **Sampling level:** Даже high-confidence automated extractions надо иногда проверять через `stratified random sampling`, иначе новые систематические ошибки останутся невидимыми.
- **Reviewer-capacity level:** Review capacity нельзя размазывать ровным слоем по всему потоку; ее надо направлять в `highest-uncertainty items`.
- **Queueing level:** Очередь human review должна быть динамической и сортироваться по uncertainty, а не по времени поступления.
- **Exam one-liner:** "Нельзя автоматизировать по aggregate metrics; accuracy и confidence надо валидировать по document type и field segment, confidence калибровать на labelled sets, high-confidence cases выборочно сэмплировать, а human review отдавать самым uncertain items."

### Супер-короткая формула

`Great aggregate metric -> can still hide bad segments`  
`Raw confidence -> calibrate first`  
`Limited reviewers -> send highest uncertainty first`

### Как запомнить на пальцах

- **aggregate accuracy** = красивая средняя цифра, которая может врать
- **segment metrics** = правда по типам документов и полям
- **calibration** = проверить, что confidence реально значит
- **stratified sampling** = проверять не только плохое, но и "вроде хорошее"
- **review queue** = сначала самые сомнительные кейсы

### Главное различие

- **97% overall accuracy** -> недостаточно для автоматизации
- **97% по standard invoices, 45% по international docs** -> вот это уже реальная картина
- **Raw confidence score** -> сырой сигнал
- **Calibrated threshold** -> рабочий routing rule

### Главная экзаменационная ловушка

Нельзя сказать "у нас 97% overall, значит все выше 95% confidence автоматизируем". Без разбивки по сегментам и калибровки confidence это может скрывать очень плохие зоны.

### Одна фраза совсем в лоб

Смотреть надо не на красивую общую точность, а на то, где именно система ошибается и насколько можно доверять ее confidence в каждом сегменте.

## 5.6 Production Reliability

### Cross-Layer Mapping: Provenance, Conflicts, Temporal Context, Attribution Preservation

- **Idea level:** Надежный research/extraction pipeline это не тот, который звучит убедительно, а тот, где можно проследить, откуда взялось каждое утверждение.
- **Provenance level:** Каждый finding должен иметь structured claim-source mapping: `claim`, `sourceUrl`, `documentName`, `relevantExcerpt`, `publicationDate`.
- **Synthesis-risk level:** Attribution чаще всего умирает на этапе summarisation/synthesis, когда агент красиво перефразирует выводы, но теряет связь с источниками.
- **Preservation level:** Поэтому downstream agents должны явно сохранять и переносить claim-source mappings через каждый шаг pipeline, а не только текст утверждений.
- **Conflict level:** Если два нормальных источника дают разные цифры, нельзя молча выбирать одну; нужно показывать обе с полным attribution.
- **Temporal level:** Разные значения часто объясняются не "ошибкой", а разными датами публикации, периодами измерения или методологией.
- **Interpretation level:** Даты публикации и data-collection context нужны не для красоты, а чтобы отличать реальный конфликт от изменения показателя во времени.
- **Rendering level:** Разный тип контента надо рендерить по-разному: financial data -> tables, news -> prose, technical findings -> structured lists.
- **Pipeline-integrity level:** Анализатор, который видит conflicting values, не должен "решать" конфликт сам; он должен завершить работу, сохранив оба значения и пояснение контекста.
- **Exam one-liner:** "Production reliability требует end-to-end provenance: каждый claim должен сохранять source mapping и publication date, conflicting sources надо аннотировать обеими версиями, а synthesis не должен убивать attribution ради красивого текста."

### Супер-короткая формула

`Every claim -> source mapping`  
`Conflicting sources -> keep both`  
`Dates explain differences`

### Как запомнить на пальцах

- **claim-source mapping** = паспорт каждого утверждения
- **attribution loss** = красиво пересказали, но источник умер
- **conflict** = не выбирай самовольно победителя
- **publication date** = ключ к пониманию, это конфликт или просто разное время
- **content-appropriate rendering** = числа в таблицу, новости в текст, технику в списки

### Главное различие

- **Два разных числа из credible sources** -> показать оба
- **Разные даты публикации** -> возможно это тренд, а не contradiction
- **Synthesis без citations** -> плохо
- **Synthesis с traceable claims** -> правильно

### Главная экзаменационная ловушка

Нельзя автоматически брать "самый новый источник" или усреднять конфликтующие числа. Это уничтожает информацию и создает ложную определенность.

### Одна фраза совсем в лоб

Если ты не можешь показать, откуда взялся каждый claim и почему цифры расходятся, система не надежная, а просто убедительно пишет.
