# Kodigo cloud listener (Cloudflare Worker)

`kodigo-listen.js` turns short audio clips from the Kodigo app into text with **Whisper large-v3-turbo** on **Cloudflare Workers AI**.
It's used for languages the phone can't listen in itself (Tagalog and Taglish on iPhone).

- **Free:** Workers AI gives 10,000 Neurons a day; Whisper Turbo uses about 47 per audio minute, so about **210 minutes a day**. On the Free plan it just stops for the day when that's used (resets 00:00 UTC = 8:00 AM Philippine time). It can't bill you.
- **Separate worker**, nothing to do with the SysOp console. No location blocking.
- Only answers the sites listed in `ALLOWED_ORIGINS`, refuses clips over 1.5 MB, drops the phrases Whisper tends to "hear" in silence.

## Anyone can have their own (free)

The Kodigo app uses a shared worker by default. Its free minutes are shared by every user, so anyone can make their **own** worker
(own free ~210 minutes a day) and paste its address into the app under **Your own Kodigo cloud → Save & test**. No code editing:
the worker already accepts the official app at hoofiepuppet.neocities.org.

## Set up (step by step)

The full illustrated steps are in **Part 7** of [Kodigo-Setup-Guide.pdf](../Kodigo-Setup-Guide.pdf). Short version:

1. dash.cloudflare.com → **Workers & Pages** → **Create** → *Start with Hello World* → name **`kodigo-listen`** → **Deploy**.
2. **Edit code** → select all, delete → paste `kodigo-listen.js` → check `ALLOWED_ORIGINS` has your site → **Deploy**.
3. Worker → **Settings** → **Bindings** → **Add** → **Workers AI** → variable name **`AI`** → **Deploy**.
4. Open `https://kodigo-listen.<your-subdomain>.workers.dev/` → should show `"ai":true`.
5. In `kodigo-app.html`, set `CLOUD_URL` to that address + `/listen`.

## API

`POST /listen?lang=tl&task=transcribe` with the audio clip as the body (webm, mp4/aac or wav).

| Param | Values |
|---|---|
| `lang` | ISO 639-1 code (`tl`, `en`, `es` …) or `auto` to detect |
| `task` | `transcribe` (same language) or `translate` (into English) |

Returns `{ "text": "...", "language": "tl" }`, or `{ "error": "..." }` with 403 (site not allowed), 413 (clip too big), 429 (free limit used up), 502 (speech service error).
