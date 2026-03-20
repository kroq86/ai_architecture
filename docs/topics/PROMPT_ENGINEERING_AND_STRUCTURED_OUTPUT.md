# Prompt Engineering & Structured Output

Короткий конспект по `Domain 4: Prompt Engineering & Structured Output`.

## 4.1 System Prompts

### Cross-Layer Mapping: Explicit Criteria, Trust, Severity Calibration

- **Idea level:** Главная ошибка в production prompts это расплывчатые инструкции вроде "be conservative" или "only report high-confidence findings".
- **Decision-boundary level:** Модель нормально работает не от туманных пожеланий, а от четких категориальных правил: что именно флагать и что именно пропускать.
- **Prompt-design level:** Хороший system prompt не говорит "будь осторожен", а говорит "репорти bugs и security issues, пропускай style nitpicks и local patterns".
- **Precision level:** False positives чаще всего снижаются не confidence-фильтром, а явными критериями и примерами.
- **Trust level:** Если одна категория шумит и дает много false positives, разработчики перестают доверять вообще всем категориям, даже тем, которые реально точные.
- **Recovery level:** Поэтому категорию с высоким FP-rate лучше временно выключить, поправить ей критерии и примеры, и только потом вернуть.
- **Severity level:** Severity надо калибровать не prose-описаниями, а конкретными code examples для `critical`, `major`, `minor`.
- **Confidence level:** Confidence useful only secondarily; сначала должны быть определены критерии, а уже потом confidence можно использовать для routing или human review.
- **Exam one-liner:** "System prompts должны задавать явные категории того, что репортить и что пропускать, с кодовыми примерами по severity; vague instructions и confidence-only filtering не дают надежной precision."

### Супер-короткая формула

`Vague prompt -> vague output`  
`Explicit criteria -> better precision`  
`Bad category trust -> hurts all categories`

### Как запомнить на пальцах

- **"be conservative"** = ни о чем
- **explicit criteria** = четкий фильтр
- **severity examples** = эталонные образцы
- **confidence** = не судья, а вспомогательный сигнал
- **disable noisy category** = сначала спаси доверие, потом чини категорию

### Главное различие

- **"будь осторожен"** -> плохой prompt
- **"флагай bugs/security, игнорируй style"** -> хороший prompt
- **prose severity description** -> слабо
- **severity через code examples** -> сильно

### Главная экзаменационная ловушка

Если категория дает много false positives, не надо лечить это фразой "report only high-confidence findings". Обычно правильнее временно отключить шумную категорию и переписать ей критерии с примерами.

### Одна фраза совсем в лоб

Модель лучше работает от четких правил и примеров, чем от абстрактных слов типа "осторожно" и "уверенно".

## 4.2 Structured Output

### Cross-Layer Mapping: `tool_use`, JSON Schema, `tool_choice`, Semantic Limits

- **Idea level:** Если тебе нужен гарантированно валидный structured output, `tool_use` с JSON schema надежнее, чем просто просить модель "выдай JSON в тексте".
- **Reliability level:** `tool_use + schema` убирает JSON syntax errors, а prompt-based JSON все еще может ломаться на скобках, запятых и формате.
- **`tool_choice` level:** `auto` = модель может выбрать текст вместо tool call; `any` = обязана вызвать какой-то tool; forced specific tool = обязана вызвать конкретный tool.
- **Guarantee level:** Для гарантированного structured output при неизвестном типе документа нужен `tool_choice: any`, а не `auto`.
- **Workflow-control level:** Forced tool используют, когда есть обязательный шаг, который нельзя пропустить, например `extract_metadata` перед остальной обработкой.
- **Schema-design level:** Схема должна учитывать реальность данных: поля, которые могут отсутствовать, надо делать optional или nullable.
- **Fabrication-prevention level:** Если сделать все поля required, модель начинает выдумывать правдоподобные значения для отсутствующих данных.
- **Ambiguity level:** Для неясных случаев полезно добавлять `unclear` в enum, а для edge cases — `other` + detail string.
- **Semantic-validation level:** Schema гарантирует структуру, но не гарантирует смысловую правильность: суммы могут не сходиться, поля могут быть перепутаны, отсутствующие данные могут быть логически неверно заполнены.
- **Exam one-liner:** "`tool_use` с JSON schema нужен для надежного structured output, `tool_choice: any` гарантирует tool call, а optional/nullable fields нужны, чтобы модель не фабриковала данные там, где их нет."

### Супер-короткая формула

`tool_use + schema -> syntax safety`  
`required fields -> fabrication pressure`  
`nullable fields -> honest nulls`

### Как запомнить на пальцах

- **prompt JSON** = "надеемся, что JSON будет нормальный"
- **`tool_use`** = JSON по рельсам
- **`auto`** = может и не вызвать tool
- **`any`** = точно вызовет какой-то tool
- **forced tool** = вызовет именно этот tool
- **nullable** = можно честно сказать "не знаю / нет данных"
- **required** = модель чувствует, что надо что-то вписать любой ценой

### Главное различие

- **Нужно просто дать модели свободу** -> `auto`
- **Нужен guaranteed structured output** -> `any`
- **Нужен обязательный конкретный первый шаг** -> forced named tool

### Главная экзаменационная ловушка

Нельзя думать, что JSON schema решает вообще все. Она чинит структуру ответа, но не защищает от semantic errors вроде придуманных сумм, перепутанных полей или галлюцинаций в required fields.

### Одна фраза совсем в лоб

Схема гарантирует форму ответа, но не гарантирует, что внутри там правда.

## 4.3 Prompt Chaining

### Cross-Layer Mapping: Validation-Retry Loop, Error Feedback, Fixable vs Unfixable

- **Idea level:** Extraction pipeline должен не просто падать на ошибках, а уметь самокорректироваться через validation-retry loop.
- **Retry-design level:** Правильный retry возвращает модели 3 вещи: исходный документ, неудачный extraction и конкретную validation error.
- **Feedback level:** Retry без конкретной ошибки почти бесполезен, потому что модель не понимает, что именно надо исправить.
- **Fixability level:** Ретраить имеет смысл только исправимые ошибки: format mismatch, misplaced values, structural mistakes, bad totals.
- **Boundary level:** Retry бесполезен, если информация реально отсутствует в source document; повторный прогон не создаст данные из воздуха.
- **Validation level:** После `tool_use + schema` остаются semantic errors, и именно их надо ловить внешней validation logic.
- **Self-correction-schema level:** Поля вроде `calculated_total`, `stated_total`, `total_discrepancy`, `conflict_detected` помогают системе самой видеть противоречия.
- **Improvement-loop level:** Поле `detected_pattern` полезно для анализа, какие типы findings потом чаще всего отклоняют люди, чтобы потом улучшать prompts системно.
- **Exam one-liner:** "Validation-retry loop работает только если модель получает исходный документ, свой неудачный extraction и конкретную ошибку; retry нужен для исправимых semantic errors, но не для информации, которой нет в source."

### Супер-короткая формула

`Original doc + failed output + exact error -> useful retry`  
`Fixable error -> retry`  
`Missing source info -> no retry`

### Как запомнить на пальцах

- **retry with feedback** = не "попробуй еще раз", а "вот где именно ты накосячил"
- **format/structure/math issue** = можно починить ретраем
- **field absent in source** = ретрай бессмысленен
- **`calculated_total` vs `stated_total`** = встроенная самопроверка
- **`conflict_detected`** = документ сам себе противоречит
- **`detected_pattern`** = след, по которому потом улучшают prompt

### Главное различие

- **Сумма line items не сходится с total** -> retry with specific discrepancy
- **Значение попало не в то поле** -> retry
- **В документе вообще нет department** -> не retry, а null / human review

### Главная экзаменационная ловушка

Нельзя автоматически ретраить все extraction failures подряд. Сначала надо понять: ошибка исправимая, или модель просто не может извлечь то, чего в документе нет.

### Одна фраза совсем в лоб

Ретрай нужен не для магии, а для исправления конкретной понятной ошибки; если в source нет данных, ретрай ничего не спасет.

## 4.4 Few-Shot & Examples

### Cross-Layer Mapping: Few-Shot Triggers, Reasoning Examples, Consistency

- **Idea level:** Если detailed instructions уже есть, а output все равно плавает, первый нормальный фикс это few-shot examples, а не еще больше инструкций.
- **Consistency level:** Few-shot examples лучше всего стабилизируют формат, judgement calls и extraction из нестандартных структур.
- **Trigger level:** Few-shot особенно нужен в 3 случаях: inconsistent formatting, inconsistent judgement on ambiguous cases, empty/null fields при том, что данные реально есть в документе.
- **Construction level:** Эффективный few-shot это обычно `2-4` targeted examples, а не огромная простыня из десятков кейсов.
- **Reasoning level:** В примере нужен не только input-output, но и объяснение "почему решение именно такое", чтобы модель училась принципу, а не только шаблону.
- **Coverage level:** Примеры должны покрывать именно те failing scenarios, на которых система сыпется, а не абстрактные красивые кейсы.
- **Hallucination level:** Few-shot examples часто снижают hallucination и empty fields в extraction, особенно когда данные встречаются в narrative text, а не только в таблицах.
- **False-positive level:** В review-задачах few-shot examples помогают не только показывать, что флагать, но и что НЕ считать проблемой.
- **Technique-selection level:** Few-shot лечит consistency problems, но не заменяет schema design, tool_use или validation loops там, где проблема структурная или валидационная.
- **Exam one-liner:** "Few-shot examples — первый инструмент для стабилизации формата и суждений; используй 2-4 targeted examples с reasoning, особенно когда инструкции уже есть, но output все еще непоследователен."

### Супер-короткая формула

`Instructions exist but output varies -> add few-shot`  
`2-4 targeted examples -> enough`  
`Examples + reasoning -> generalisation`

### Как запомнить на пальцах

- **few-shot** = показать, как правильно выглядит ответ
- **reasoning** = объяснить, почему именно так
- **format drift** = few-shot
- **ambiguous judgment** = few-shot
- **data exists but comes back empty** = few-shot examples on that structure
- **too many examples** = лишние токены без большого выигрыша

### Главное различие

- **Формат плавает** -> few-shot
- **Narrative text плохо экстрактится** -> few-shot
- **Malformed JSON** -> не few-shot, а `tool_use + schema`
- **Fabricated missing values** -> не few-shot, а optional/nullable fields
- **Totals don't match** -> не few-shot, а validation-retry loop

### Главная экзаменационная ловушка

Если формат или judgment уже нестабилен, не надо первым делом писать еще более длинные инструкции. Обычно правильнее показать модели несколько хороших примеров с reasoning.

### Одна фраза совсем в лоб

Когда слова уже не помогают, покажи модели хорошие образцы и объясни, почему они хорошие.

## 4.5 Prompt Optimisation

### Cross-Layer Mapping: Message Batches API, Cost vs Latency, Retry Strategy

- **Idea level:** `Message Batches API` это инструмент экономии, а не универсальная замена обычных synchronous calls.
- **Cost level:** Batch дает примерно `50% cost savings`, но платой за это является отсутствие нормального latency SLA.
- **Latency level:** Batch может отработать быстро, а может идти до `24 hours`, и на это нельзя закладываться в blocking workflow.
- **Routing level:** Главное правило простое: blocking workflows -> synchronous API, latency-tolerant workflows -> batch API.
- **Workflow-fit level:** Pre-merge checks, real-time review и все, где кто-то ждет ответ прямо сейчас, должны оставаться synchronous; overnight reports и weekly audits можно уводить в batch.
- **Correlation level:** Для batch каждый request должен иметь `custom_id`, чтобы потом можно было сопоставить ответы, ошибки и повторные отправки.
- **Failure-handling level:** При batch-failures надо пересылать не весь batch, а только failed items, причем с точечными изменениями: chunking, prompt refinement, more tokens, few-shot for edge cases.
- **Preparation level:** Самый выгодный шаг до большого batch это sample-set refinement: сначала погонять prompt на `5-10` representative docs, а уже потом лить весь объем.
- **SLA-planning level:** При расчете SLA всегда исходят из worst case: если batch может идти 24 часа, то submission cadence надо считать от этого максимума, а не от "обычно быстро приходит".
- **Capability-boundary level:** Batch API не подходит для multi-turn tool calling внутри одного request; если workflow требует tools mid-processing, нужен synchronous API.
- **Exam one-liner:** "Batch API используют ради экономии только в latency-tolerant workflows; blocking tasks оставляют synchronous, результаты связывают через `custom_id`, а перед массовым запуском prompts обкатывают на sample set."

### Супер-короткая формула

`Need answer now -> synchronous`  
`Can wait -> batch`  
`Batch failures -> retry only failed items`

### Как запомнить на пальцах

- **batch** = дешевле, но медленнее и не по расписанию
- **synchronous** = дороже, но сразу
- **`custom_id`** = номерок для каждой заявки
- **sample set** = прогон перед массовым запуском
- **resubmit failures only** = не жги деньги на успешных кейсах
- **24h max** = думай худшим сценарием, а не лучшим

### Главное различие

- **Developer waiting to merge PR** -> synchronous
- **Report нужен завтра утром** -> batch
- **Workflow требует tool calling по ходу обработки** -> synchronous
- **Большой набор документов без срочности** -> batch

### Главная экзаменационная ловушка

Нельзя переводить все workflows на batch просто ради экономии. Если результат блокирует человека или систему прямо сейчас, batch туда не подходит, даже если "обычно приходит быстро".

### Одна фраза совсем в лоб

Batch нужен там, где можно ждать; если ждать нельзя, плати за synchronous и не мудри.

## 4.6 Output Validation

### Cross-Layer Mapping: Independent Review, Multi-Pass Validation, Confidence Routing

- **Idea level:** Когда модель проверяет свой же результат в той же сессии, она предвзята к собственным решениям, потому что помнит, почему их приняла.
- **Self-review level:** Same-session self-review слабее независимой проверки, потому что модель тащит с собой исходный reasoning context и чаще подтверждает себя, чем реально сомневается.
- **Independent-instance level:** Для нормального review нужен отдельный invocation / fresh instance без старого reasoning context.
- **Attention level:** Большие ревью в один проход страдают от attention dilution: одни файлы смотрятся глубоко, другие поверхностно, плюс появляются противоречивые findings.
- **Architecture level:** Лечение тут structural: per-file local passes + отдельный cross-file integration pass.
- **Local-pass level:** Отдельный review по каждому файлу дает ровную глубину анализа и лучше ловит локальные bugs/security/logic issues.
- **Integration-pass level:** Отдельный cross-file pass ловит data flow issues, inconsistent APIs и противоречия между per-file findings.
- **Confidence-routing level:** Confidence можно добавлять к findings, чтобы отправлять uncertain cases на human review, а clear-cut findings напрямую разработчикам.
- **Calibration level:** Raw confidence нельзя сразу использовать автоматически; thresholds надо калибровать на labelled validation sets.
- **Exam one-liner:** "Не доверяй self-review в той же сессии; используй независимые инстансы, большие ревью дели на per-file и cross-file passes, а confidence для routing применяй только после калибровки."

### Супер-короткая формула

`Same session review -> biased`  
`Independent instance -> better review`  
`Large review -> per-file + cross-file pass`

### Как запомнить на пальцах

- **self-review** = сам у себя проверил домашку
- **fresh instance** = другой проверяющий
- **per-file pass** = смотрим каждый файл отдельно
- **cross-file pass** = смотрим связи между файлами
- **raw confidence** = сырое ощущение модели
- **calibrated threshold** = уже проверенный рабочий порог

### Главное различие

- **"review your own output" в той же сессии** -> слабый вариант
- **Отдельный новый review call** -> сильный вариант
- **Один большой pass на 14 файлов** -> attention dilution
- **Per-file passes + integration pass** -> правильная архитектура

### Главная экзаменационная ловушка

Если multi-file review плохой, не надо лечить это просто большим context window. Проблема обычно не в том, что текст не влез, а в том, что внимание модели размазалось.

### Одна фраза совсем в лоб

Чтобы хорошо валидировать output, нужен свежий взгляд, дробление больших ревью и проверенные confidence thresholds, а не надежда на самопроверку модели.
