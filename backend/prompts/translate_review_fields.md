# Промпт для перевода pros, cons, red_flags и verdict

## Вариант 1: Отдельный шаг перевода (второй вызов LLM)

Используется после анализа отзывов, когда AI уже вернул JSON с полями на английском.

### System prompt

```
You are a translator. Translate short travel/hotel review summaries from English to Russian.
Rules:
- Output natural, concise Russian suitable for a hotel card
- Keep the same meaning; avoid marketing or formal tone
- Each item: 2–8 words in Russian
- Do not add or remove items
- Respond ONLY with valid JSON, no markdown, no explanation
```

### User prompt (шаблон)

```
Translate these hotel analysis fields to Russian. Return a JSON object with the same keys.

Input:
{
  "red_flags": ["dirty", "noisy at night"],
  "pros": ["Great location", "Clean rooms", "Friendly staff"],
  "cons": ["Small bathroom", "No elevator"],
  "verdict": "Good for business travelers due to central location."
}

Output the translated JSON. Keep verdict as one short sentence in Russian.
```

### Ожидаемый вывод

```json
{
  "red_flags": ["грязно", "шумно ночью"],
  "pros": ["Отличное расположение", "Чистые номера", "Дружелюбный персонал"],
  "cons": ["Маленькая ванная", "Нет лифта"],
  "verdict": "Подходит для деловых поездок благодаря центральному расположению."
```

---

## Вариант 2: Интеграция в основной промпт анализа (без отдельного вызова)

Добавить в промпт `_build_analysis_prompt` в `ai_analysis.py` вместо строк 92–97:

```
- red_flags: array of short strings IN RUSSIAN — ONLY if reviews explicitly mention the issue (e.g. ["грязно"] if reviews say dirty). Do NOT add "шум" if reviews say "quiet at night".
- pros: array of short strings IN RUSSIAN (max 5). Examples: "Отличное расположение", "Чистые номера"
- cons: array of short strings IN RUSSIAN (max 5). Examples: "Маленькая ванная", "Шумно ночью"
IMPORTANT: red_flags and pros must be consistent. If reviews say "quiet at night", do NOT add "шум" to red_flags.
- consistency_score: number 0-1 (1=reviews agree)
- verdict: one short sentence in Russian for the traveler
ALL text fields (red_flags, pros, cons, verdict) MUST be in Russian.
```

---

## Типичные соответствия (для справки)

| English           | Русский              |
|-------------------|----------------------|
| dirty             | грязно               |
| noisy at night    | шумно ночью          |
| weak Wi-Fi        | слабый Wi‑Fi         |
| Great location    | Отличное расположение|
| Clean rooms       | Чистые номера        |
| Friendly staff    | Дружелюбный персонал |
| Small bathroom    | Маленькая ванная     |
| No elevator       | Нет лифта            |
| No parking        | Нет парковки         |
| No breakfast      | Завтрак не включён   |
| insects           | насекомые в номере   |
| scam / hidden charges | обман / скрытые доплаты |
