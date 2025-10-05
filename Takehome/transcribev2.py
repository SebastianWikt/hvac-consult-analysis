# pip install assemblyai python-dotenv
import os, json, datetime, sys
from dotenv import load_dotenv
import assemblyai as aai

# --- 0) Setup ---
load_dotenv()  # loads .env if present
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not API_KEY:
    print("Set ASSEMBLYAI_API_KEY in your environment.", file=sys.stderr)
    sys.exit(1)

aai.settings.api_key = API_KEY

# --- 1) Input audio (local path or URL) ---
AUDIO_FILE = "Takehome/39472_N_Darner_Dr_2.m4a"  # your local file

# --- 2) Transcription config tuned for this task ---
# Notes:
# - speaker_labels=True to get diarization (utterances array)
# - speakers_expected=2 to help diarizer converge
# - disfluencies=False (set True if you want "um/uh" to coach)
# - enable pii redaction if you might have payment details in audio
config = aai.TranscriptionConfig(
    speech_model=aai.SpeechModel.universal,  # good general model
    speaker_labels=True,
    speakers_expected=2,       # we have Tech + Customer
    punctuate=True,
    format_text=True,
    disfluencies=False,
    # If your recording is true stereo (tech on L, customer on R), uncomment:
    # dual_channel=True,
    # Privacy (optional):
    # redact_pii=True,
    # redact_pii_audio=True,
    # redact_pii_policies=["credit_card_number","email_address","phone_number","person_name"],
    # Quality helpers:
    word_boost=[
        # HVAC vocabulary to improve recognition
        "HERS", "SEER", "R-32", "R32", "R-410A", "R410A",
        "heat pump", "furnace", "condenser", "coil",
        "thermostat", "Daikin", "Bryant", "Bosch",
        "duct sealing", "MERV", "Energy Star",
        "Silicon Valley Clean Energy", "SVCE", "TECH Clean California",
        "inverter", "line set", "whip", "grille"
    ],
    # boost_param=aai.BoostParam.high,  # raise weight of boosted terms
    # Nice-to-have analytics:
    sentiment_analysis=True,  # set True if you want per-utterance sentiment
    auto_chapters=False,       # set True to get rough sections
    entity_detection=False,    # set True to extract brands/components
)

# --- 3) Run transcription (blocking helper) ---
transcriber = aai.Transcriber(config=config)
transcript = transcriber.transcribe(AUDIO_FILE)

if transcript.status == "error":
    raise RuntimeError(f"Transcription failed: {transcript.error}")

print("Transcript completed.")

# --- 4) (Optional) map speakers A/B -> Tech/Customer heuristic ---
def map_speaker(label: str) -> str:
    # AssemblyAI may label speakers as "A", "B", "SPK_0", "SPK_1", etc.
    # Quick heuristic: whoever mentions technical stuff first is likely the Tech.
    # For most 2-person calls, SPK_0/A will be the Tech. Adjust if needed.
    if label in ("A", "SPK_0", "0"):
        return "Tech"
    if label in ("B", "SPK_1", "1"):
        return "Customer"
    return f"Speaker {label}"

# --- 5) Build a simple JSON for your web app ---
utterances = []
for u in (transcript.utterances or []):
    utterances.append({
        "speaker": map_speaker(u.speaker),
        "start": round(u.start / 1000, 2) if isinstance(u.start, (int, float)) and u.start > 1000 else u.start,
        "end":   round(u.end   / 1000, 2) if isinstance(u.end,   (int, float)) and u.end   > 1000 else u.end,
        "text": u.text
    })

call_json = {
    "meta": {
        "call_type": "Repair follow-up & replacement consultation (HVAC)",
        "date_analyzed": datetime.date.today().isoformat(),
        "transcribed_with": "AssemblyAI (speaker_labels, timestamps, word_boost)"
    },
    # You will fill these after your review in your UI or a separate pass:
    "compliance_check": [],
    "sales_insights": [],
    # Raw structured transcript for rendering
    "utterances": utterances,
    "full_transcript": transcript.text
}

# --- 6) Save for your frontend ---
os.makedirs("data", exist_ok=True)
with open("data/call.json", "w", encoding="utf-8") as f:
    json.dump(call_json, f, indent=2, ensure_ascii=False)

print("Wrote data/call.json")

# =========================
#  A–D: Stage tagging + JSON enrich
# =========================
import re, datetime, json, os

# --- A) Keyword rules (order matters: earlier wins ties) ---
STAGE_RULES = [
    ("Introduction", [
        r"\b(hello|hey|hi)\b", r"\bmy name is\b", r"\b(i'?m with|from)\b",
        r"\bcompany\b", r"\bis now a good time\b"
    ]),
    ("Problem Diagnosis", [
        r"\b(problem|issue|symptom|concern|leak|mold|noise|efficien\w*|hot|cold|not working|diagnos\w*)\b"
    ]),
    ("Solution Explanation", [
        r"\b(option|solution|we can|recommend|install|replace|upgrade|like-?for-?like)\b",
        r"\bheat pump\b", r"\bfurnace\b", r"\bcondenser\b", r"\bcoil\b", r"\bthermostat\b",
        r"\bseer\b", r"\br[- ]?32\b", r"\br[- ]?410a\b", r"\binverter\b", r"\bduct\b",
        r"\bpermit\b", r"\bhers\b", r"\brebate\b", r"\bwarranty\b"
    ]),
    ("Upsell Attempts", [
        r"\bmaintenance\b", r"\bservice plan\b", r"\bmembership\b",
        r"\bduct sealing\b", r"\bfilter\b", r"\bgrille\b", r"\buv\b", r"\bmerv\b"
    ]),
    ("Financing", [
        r"\bfinanc\w*\b", r"\bmonthly payment\b", r"\bapr\b", r"\binterest\b",
        r"\b12 months\b", r"\bno interest\b", r"\bterm\b"
    ]),
    ("Closing & Thank You", [
        r"\bemail\b", r"\bfollow ?up\b", r"\bdecid(e|ing)\b", r"\b(spouse|wife|husband)\b",
        r"\bdeposit\b", r"\bdown payment\b", r"\bcredit\b", r"\bcard\b", r"\bthank(s| you)\b"
    ]),
]
COMPILED_RULES = [(stage, [re.compile(k, re.I) for k in keys]) for stage, keys in STAGE_RULES]

def tag_stage(text: str) -> str:
    t = text or ""
    for stage, patterns in COMPILED_RULES:
        if any(p.search(t) for p in patterns):
            return stage
    return "General"

def merge_adjacent(segments, max_gap_s=8.0):
    """Merge neighbors if same stage and start/end are close in time."""
    if not segments:
        return []
    merged = [segments[0]]
    for seg in segments[1:]:
        last = merged[-1]
        same_stage = (seg["stage"] == last["stage"])
        gap = (seg["start"] - last["end"]) if isinstance(seg["start"], (int,float)) and isinstance(last["end"], (int,float)) else 0
        if same_stage and 0 <= gap <= max_gap_s:
            last["end"] = seg["end"]
            last["text"] = (last["text"] + " " + seg["text"]).strip()
        else:
            merged.append(seg)
    return merged

# (You already have map_speaker; reuse it.)
# def map_speaker(label: str) -> str: ...

# --- B) Build utterance segments with stage tags ---
utterances_tagged = []
for u in (transcript.utterances or []):
    start = u.start
    end = u.end
    # Convert ms → s if needed
    if isinstance(start, (int,float)) and start > 10_000:
        start, end = start/1000.0, end/1000.0
    seg = {
        "speaker": map_speaker(u.speaker),
        "start": round(start or 0, 2) if start is not None else None,
        "end": round(end or 0, 2) if end is not None else None,
        "text": u.text or "",
    }
    seg["stage"] = tag_stage(seg["text"])
    utterances_tagged.append(seg)

segments = merge_adjacent(utterances_tagged, max_gap_s=8.0)

# --- C) Seed compliance checklist using short evidence pulls ---
def short_evidence(stage, limit=2):
    picks = [s for s in segments if s["stage"] == stage][:limit]
    out = []
    for s in picks:
        ts = ""
        if isinstance(s["start"], (int,float)) and isinstance(s["end"], (int,float)):
            ts = f"{s['start']:.0f}s–{s['end']:.0f}s"
        text = s["text"].strip()
        if len(text) > 160:
            text = text[:157] + "..."
        who = s["speaker"]
        out.append(f"[{ts}] {who}: “{text}”")
    return " | ".join(out) or "—"

compliance_seed = [
    {
        "stage":"Introduction","score":0,"max":5,
        "evidence": short_evidence("Introduction"),
        "suggestion":"Open with name, company, role, purpose; confirm it’s a good time."
    },
    {
        "stage":"Problem Diagnosis","score":0,"max":5,
        "evidence": short_evidence("Problem Diagnosis"),
        "suggestion":"Probe symptoms, duration, comfort by room, prior fixes, utility bills, constraints."
    },
    {
        "stage":"Solution Explanation","score":0,"max":5,
        "evidence": short_evidence("Solution Explanation"),
        "suggestion":"Compare options, costs, rebates, permits/HERS, warranties, trade-offs, savings."
    },
    {
        "stage":"Upsell Attempts","score":0,"max":5,
        "evidence": short_evidence("Upsell Attempts"),
        "suggestion":"Offer only need-based upsells; tie benefits to diagnosed issues."
    },
    {
        "stage":"Maintenance Plan Offer","score":0,"max":5,
        "evidence": short_evidence("Upsell Attempts"),
        "suggestion":"Pitch plan explicitly—price, cadence, inclusions; link to warranty terms."
    },
    {
        "stage":"Closing & Thank You","score":0,"max":5,
        "evidence": short_evidence("Closing & Thank You"),
        "suggestion":"Recap decisions, email quotes, schedule follow-up with all decision-makers, thank the customer."
    }
]

# --- D) Read your existing call_json, enrich, and re-write ---
# If you just wrote data/call.json above, we’ll load and update it.
with open("data/call.json","r",encoding="utf-8") as f:
    call_json = json.load(f)

call_json.update({
    "meta": {
        **call_json.get("meta", {}),
        "date_analyzed": datetime.date.today().isoformat(),
        "stages_auto_tagged": True
    },
    "segments": segments,          # merged, stage-tagged segments for easy display
    "utterances": utterances_tagged # per-utterance, pre-merge
})

# Only seed compliance if empty (so you don’t overwrite manual scoring later)
if not call_json.get("compliance_check"):
    call_json["compliance_check"] = compliance_seed

# Ensure sales_insights exists
call_json.setdefault("sales_insights", [])

with open("data/call.json","w",encoding="utf-8") as f:
    json.dump(call_json, f, indent=2, ensure_ascii=False)

print(f"Enriched data/call.json ✔  stages={len(segments)}  utterances={len(utterances_tagged)}")

