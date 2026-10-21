# Daily beauty card news — workflow

Audience: Korean women in their 30s. Channels: Instagram (@labe.tem), Facebook page, Threads, via Metricool (brand id 7518208).
Every day: research a trending beauty topic, write a 5-card carousel in the fixed design, register it in Metricool as a **draft** for 20:00 KST, and wait for the owner's OK before it can publish.

## 1. Pick today's topic
- Search Korean beauty news from the **last 30 days** (several searches: 올리브영 트렌드, 뷰티 신제품, 스킨케어 트렌드, 계절 피부 고민, SNS 화제 뷰티 등). Prefer Korean news outlets and brand/retailer press releases.
- Read `topics_log.json`. Do not repeat a topic used in the last 21 days; vary the category (skincare / makeup / hair / body / inner beauty / devices / seasonal care).
- Pick the topic most relevant and useful to women in their 30s *right now* (season, weather, recent sales events, viral items).

## 2. Write the copy → `posts/YYYY-MM-DD/content.json`
Copy the structure of `posts/2026-10-19/content.json` exactly (same keys). All copy in natural Korean.
- **card1 (hook, must land in 3 seconds):** tag ≤ 10 chars; title = a question or shocking line, max 3 lines × ~7 chars, wrap the key word in `<span class="hl">`; sub = 2 short lines.
- **card2 (why now):** title max 3 lines × ~11 chars (one phrase in `<span class="under">`); body 2 lines; exactly 3 checks, each ≤ 18 chars.
- **card3 (3 items: mistakes, myths or picks):** title 2 lines (2nd line in `<span class="em">`); `mark_x` true for "don'ts", false otherwise; exactly 3 items, title ≤ 16 chars, desc ≤ 24 chars.
- **card4 (3-step routine/solution):** same limits as card3, exactly 3 steps.
- **card5 (CTA):** title 2 lines with one `<span class="em">`; cta = save prompt (2 lines, starts with 📌); sub = comment prompt (2 lines).
- **caption:** 3 short lines (hook / value + save CTA / comment CTA) + blank line + 5–7 Korean hashtags.
- **sources:** URLs of the articles used.

Content rules (important — this is a public brand account):
- No medical/drug claims (치료, 완치, 재생, 특정 질환 개선 등) and no exaggerated efficacy numbers that aren't in the sources. Phrase as care tips ("도움이 될 수 있어요").
- Do not name or recommend specific brands/products unless the topic is literally a news item about them; never invent product facts.
- Every factual claim must come from the sources you read today.

## 3. Render and check
```
pip install --break-system-packages jinja2 playwright pillow  # only if missing
python3 template/render.py posts/YYYY-MM-DD/content.json
```
- Exit code 2 = text overflows the card → shorten that card's text and re-render.
- Open `preview.png` with Read and actually look at it: no awkward line breaks, nothing clipped, Korean renders correctly.

## 4. Publish images
- Add today's line to `topics_log.json` with status `"draft"`.
- `git add` the post folder + log, commit, `git push origin main`.
- Image URLs: `https://raw.githubusercontent.com/verabella8205/card-news/main/posts/YYYY-MM-DD/card_0N.png` (N = 1..5). Confirm one URL loads before continuing.

## 5. Register the Metricool draft
`createScheduledPost` with blogId `7518208`, date `YYYY-MM-DDT20:00:00+09:00`, and info:
- `draft: true`, `autoPublish: false`
- providers: facebook, instagram, threads
- media: the 5 raw URLs in order
- publicationDate: `{dateTime: "YYYY-MM-DDT20:00:00", timezone: "Asia/Seoul"}`
- text: the caption
- `facebookData: {type: "POST"}`, `instagramData: {type: "POST"}`, `threadsData: {}`
Keep the returned `id`, `uuid` and Metricool's copied media URLs.

## 6. Ask the owner for approval
Send the owner (in Korean, via SendUserMessage and SendUserFile so it reaches the phone):
- `preview.png` plus the 5 cards
- the caption and the topic + 1-line reason it's trending, with source links
- the Metricool planner link
- "8시에 올릴까요? '오케이'라고 답해주시면 8시에 게시돼요. 수정할 부분이 있으면 말씀해 주세요."

Then wait.
- **OK** → `updateScheduledPost` the same post (full content, using Metricool's media URLs) with `draft: false`, `autoPublish: true`. If it is already past 20:00 KST, set the time to now + 3 minutes. Confirm the status, update `topics_log.json` to `"scheduled"`, push.
- **Edits requested** → change content.json, re-render, push, update the Metricool draft, show the new preview, ask again.
- **Every change goes to GitHub:** whenever content.json, the rendered cards, or `topics_log.json` change (edits, re-renders, status changes), commit and `git push origin main` right away, so the repo always matches what is in Metricool.
- **No answer** → do nothing. The post stays a draft and is never published automatically.
