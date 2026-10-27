/* ElevenLabs housekeeping shared by `voice` (replace / delete a clone) and `delete-account`. */
import { admin } from "./tier.ts";

export const ELEVEN = "https://api.elevenlabs.io/v1";

// a deleted clone takes every sentence ever synthesized in that voice with it
export async function forget(voiceId: string, key: string) {
  if (key) await fetch(`${ELEVEN}/voices/${voiceId}`, { method: "DELETE", headers: { "xi-api-key": key } });
  const { data: rows } = await admin.from("tts_lines").select("audio_path").eq("voice_id", voiceId);
  const paths = (rows ?? []).map((r) => r.audio_path as string);
  for (let i = 0; i < paths.length; i += 500) await admin.storage.from("tts").remove(paths.slice(i, i + 500));
  await admin.from("tts_lines").delete().eq("voice_id", voiceId);
}
