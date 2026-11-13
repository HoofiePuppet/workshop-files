// =====================================================================
//  KODIGO CLOUD LISTENER  (Cloudflare Worker: "kodigo-listen")
//  (c) 2026 Hoofie Puppet · CC BY-NC-SA 4.0 · part of the Kodigo project
//
//  Turns short audio clips from the Kodigo app into text with Whisper
//  (Cloudflare Workers AI, free plan: about 210 minutes of audio a day).
//  Used for languages the phone can't listen in itself, e.g. Tagalog on iPhone.
//
//  SETUP (Cloudflare dashboard):
//    1. Workers & Pages -> Create -> Create Worker -> name it  kodigo-listen  -> Deploy
//    2. Edit code -> replace everything with this file -> Deploy
//    3. Settings -> Bindings -> Add -> Workers AI -> Variable name:  AI  -> Deploy
//  Address:  https://kodigo-listen.<your-subdomain>.workers.dev/listen
//
//  API:  POST /listen?lang=tl&task=transcribe     body = the audio clip (webm / mp4 / wav)
//        lang  = ISO 639-1 code ("tl" Tagalog, "en" English ...) or "auto" to detect
//        task  = "transcribe" (same language) or "translate" (into English)
//        ->  { "text": "..." }
//  GET /  -> health check
// =====================================================================

// Only these web pages may use this listener (stops other sites spending your free minutes).
// Add your own site here if you host the Kodigo app somewhere else.
const ALLOWED_ORIGINS = [
  "https://hoofiepuppet.neocities.org",
  "http://localhost:8000",
  "http://127.0.0.1:8000"
];

const MODEL = "@cf/openai/whisper-large-v3-turbo";
const MAX_BYTES = 1_500_000;        // ~1.5 MB: plenty for a 10 s clip, refuses anything huge

// Phrases Whisper is known to "hear" in silence or noise. Dropped if they are the whole caption.
const PHANTOMS = [
  "thank you for watching", "thanks for watching", "thank you.", "thank you", "you",
  "please subscribe", "subscribe", "bye.", "bye", "salamat po sa panonood", "salamat sa panonood",
  "music", "[music]", "(music)", "♪"
];

function cors(origin) {
  const ok = ALLOWED_ORIGINS.includes(origin);
  return {
    "Access-Control-Allow-Origin": ok ? origin : ALLOWED_ORIGINS[0],
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin"
  };
}

function json(data, status, origin) {
  return new Response(JSON.stringify(data), {
    status: status || 200,
    headers: { "Content-Type": "application/json; charset=utf-8", ...cors(origin) }
  });
}

function toBase64(buf) {
  const bytes = new Uint8Array(buf);
  let bin = "";
  const step = 0x8000;
  for (let i = 0; i < bytes.length; i += step) {
    bin += String.fromCharCode.apply(null, bytes.subarray(i, i + step));
  }
  return btoa(bin);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });

    if (request.method === "GET" && (url.pathname === "/" || url.pathname === "/listen")) {
      return json({ ok: true, service: "kodigo-listen", model: MODEL, ai: !!env.AI }, 200, origin);
    }

    if (request.method !== "POST" || url.pathname !== "/listen") return json({ error: "not found" }, 404, origin);
    if (!ALLOWED_ORIGINS.includes(origin)) return json({ error: "origin not allowed" }, 403, origin);
    if (!env.AI) return json({ error: "AI binding missing: Settings -> Bindings -> Workers AI, name AI" }, 500, origin);

    const audio = await request.arrayBuffer();
    if (!audio.byteLength) return json({ error: "no audio" }, 400, origin);
    if (audio.byteLength > MAX_BYTES) return json({ error: "clip too long" }, 413, origin);

    const lang = (url.searchParams.get("lang") || "auto").toLowerCase().slice(0, 5);
    const task = url.searchParams.get("task") === "translate" ? "translate" : "transcribe";

    const input = { audio: toBase64(audio), task, vad_filter: true };
    if (lang !== "auto" && /^[a-z]{2,3}$/.test(lang)) input.language = lang;

    try {
      const out = await env.AI.run(MODEL, input);
      let text = ((out && out.text) || "").replace(/\s+/g, " ").trim();
      if (PHANTOMS.includes(text.toLowerCase())) text = "";
      return json({ text, language: out && out.transcription_info && out.transcription_info.language }, 200, origin);
    } catch (e) {
      const msg = String((e && e.message) || e);
      // Free daily allowance used up (resets 00:00 UTC = 8:00 AM Philippine time)
      const limit = /limit|quota|neuron|4006|capacity/i.test(msg);
      return json({ error: limit ? "daily free limit reached" : "speech service error", detail: msg.slice(0, 200) }, limit ? 429 : 502, origin);
    }
  }
};
