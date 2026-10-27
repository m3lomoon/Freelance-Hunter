// Supabase Edge Function · synthesize
// Two routes, both authenticated:
//   POST /synthesize?op=clone   multipart { sample }      → creates an ElevenLabs Instant Voice Clone, stores voice_id
//   POST /synthesize?op=speak   json { script_id }        → synthesizes each line (cached per sentence), returns signed URLs
//
// Cache rule: the same sentence in the same voice is synthesized once, ever.
// The six goals × eight affirmations × three tones fit in ~150 sentences, so
// a heavy user costs the first month, then almost nothing.
//
// secrets: ELEVENLABS_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

import { createClient } from "npm:@supabase/supabase-js@2";

const ELEVEN = "https://api.elevenlabs.io/v1";
const MODEL = "eleven_multilingual_v2";

async function sha256(s: string) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

Deno.serve(async (req) => {
  const url = new URL(req.url);
  const op = url.searchParams.get("op");
  const auth = req.headers.get("Authorization") ?? "";
  const supabase = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
  const { data: { user } } = await supabase.auth.getUser(auth.replace("Bearer ", ""));
  if (!user) return Response.json({ error: "unauthorized" }, { status: 401 });
  const key = Deno.env.get("ELEVENLABS_API_KEY")!;

  const { data: profile } = await supabase.from("profiles").select("name, plan, voice_id, voice_consent_at").eq("id", user.id).single();
  if (!profile) return Response.json({ error: "no profile" }, { status: 400 });
  if (profile.plan === "free") return Response.json({ error: "upgrade_required" }, { status: 402 });

  // ---------- clone ----------
  if (op === "clone") {
    const form = await req.formData();
    const sample = form.get("sample");
    if (!(sample instanceof File)) return Response.json({ error: "sample required" }, { status: 400 });
    if (!profile.voice_consent_at) return Response.json({ error: "consent_required" }, { status: 403 });

    // keep the consent recording (user can delete it → we delete the clone too)
    const path = `${user.id}/${Date.now()}.webm`;
    await supabase.storage.from("voice-samples").upload(path, sample, { contentType: sample.type });

    // replace any previous clone so each user only ever has one voice
    if (profile.voice_id) await fetch(`${ELEVEN}/voices/${profile.voice_id}`, { method: "DELETE", headers: { "xi-api-key": key } });

    const fd = new FormData();
    fd.append("name", `melomood-${user.id.slice(0, 8)}`);
    fd.append("files", sample, "sample.webm");
    fd.append("remove_background_noise", "true");
    const r = await fetch(`${ELEVEN}/voices/add`, { method: "POST", headers: { "xi-api-key": key }, body: fd });
    if (!r.ok) return Response.json({ error: "clone_failed", detail: await r.text() }, { status: 502 });
    const { voice_id } = await r.json();

    await supabase.from("profiles").update({ voice_id, voice_sample: path }).eq("id", user.id);
    return Response.json({ voice_id });
  }

  // ---------- speak ----------
  if (op === "speak") {
    const { script_id } = await req.json();
    const { data: script } = await supabase.from("scripts").select("lines, kind").eq("id", script_id).eq("user_id", user.id).single();
    if (!script) return Response.json({ error: "not found" }, { status: 404 });
    const voice = profile.voice_id;
    if (!voice) return Response.json({ error: "no_voice" }, { status: 400 });
    const speed = script.kind === "sleep" ? 0.8 : 0.92;

    const out: { t: string; pause: number; url: string }[] = [];
    for (const line of script.lines as { t: string; pause: number }[]) {
      const hash = await sha256(`${MODEL}|${speed}|${line.t}`);
      const { data: hit } = await supabase.from("tts_cache").select("audio_path").eq("voice_id", voice).eq("text_hash", hash).maybeSingle();
      let path = hit?.audio_path;
      if (!path) {
        const r = await fetch(`${ELEVEN}/text-to-speech/${voice}?output_format=mp3_44100_128`, {
          method: "POST",
          headers: { "xi-api-key": key, "content-type": "application/json" },
          body: JSON.stringify({ text: line.t, model_id: MODEL, voice_settings: { stability: 0.55, similarity_boost: 0.8, style: 0.2, speed } }),
        });
        if (!r.ok) return Response.json({ error: "tts_failed", detail: await r.text() }, { status: 502 });
        path = `cache/${voice}/${hash}.mp3`;
        await supabase.storage.from("audio").upload(path, await r.blob(), { contentType: "audio/mpeg", upsert: true });
        await supabase.from("tts_cache").insert({ voice_id: voice, text_hash: hash, audio_path: path, chars: line.t.length });
      }
      const { data: signed } = await supabase.storage.from("audio").createSignedUrl(path, 60 * 60);
      out.push({ t: line.t, pause: line.pause, url: signed!.signedUrl });
    }
    return Response.json({ lines: out });
  }

  return Response.json({ error: "unknown op" }, { status: 400 });
});
