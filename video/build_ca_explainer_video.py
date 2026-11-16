#!/usr/bin/env python3
"""
Builds the Polished 1080p Full HD (1920x1080) Live Browser Walkthrough & Explainer Video for:
  "TAMIL NADU ICAI CA MASTERY HUB (FOUNDATION • INTERMEDIATE • FINAL & SPOM) + BILINGUAL GEMINI AI COACH"

Key Quality Guarantees:
  - 100% Real Full-Screen Live Browser Walkthrough of http://localhost:8096.
  - Smooth animated macOS pointer cursor, click ripples, live DOM interactions, smooth scrolling,
    and pixel-exact getBoundingClientRect() focus highlights.
  - Natural Spoken Tamil Nadu Mentor Voiceover (பேச்சுத் தமிழ் / Conversational Tanglish) covering
    all 3 ICAI CA student groups (Foundation, Intermediate Group I & II + Direct Entry, Final + SPOM),
    ICAI 40%/50%/60% exemption rules, TAHDCO & SIRC Tamil Nadu free public coaching institutes,
    and the 24/7 Bilingual Gemini AI CA Coach.
  - Clean Netflix/YouTube-style single-line English Subtitles burned into the bottom center +
    external .srt and .vtt subtitle tracks.
"""

import asyncio
import json
import shutil
import subprocess
import time
import wave
from pathlib import Path
import edge_tts
from playwright.async_api import async_playwright

VIDEO_DIR = Path("/Users/thameema/git/ca-prep/video")
BUILD_DIR = VIDEO_DIR / "build_ca_v1"
OUTPUT_MP4 = VIDEO_DIR / "tamil_nadu_ca_explainer.mp4"
OUTPUT_SRT = VIDEO_DIR / "tamil_nadu_ca_explainer_en.srt"
OUTPUT_VTT = VIDEO_DIR / "tamil_nadu_ca_explainer_en.vtt"

VOICE = "ta-IN-PallaviNeural"
RATE = "+6%"

SEGMENTS = [
    {
        "id": "01_intro_a",
        "vo_ta": "வணக்கம்! நம்ம தமிழ்நாடு மாணவர்கள், I C A I சார்ட்டர்ட் அக்கவுண்டன்சி தேர்வுல முதல் முயற்சியிலேயே தேர்ச்சி பெற்று, ஆடிட்டர் ஆகணும்ங்கிற கனவை நனவாக்க உருவாக்கப்பட்டது தான், இந்த தமிழ்நாடு C A Mastery Hub.",
        "sub_en": "Welcome! The Tamil Nadu ICAI CA Mastery Hub is built to help Tamil Nadu students pass Chartered Accountancy in their first attempt.",
    },
    {
        "id": "01_intro_b",
        "vo_ta": "இதுல C A Foundation, C A Intermediate Group 1 மற்றும் Group 2, அப்புறம் C A Final மற்றும் S P O M அப்படின்னு மூன்று நிலை மாணவர்களுக்கான நானூற்று முப்பதுக்கும் மேற்பட்ட verified வினாக்கள், R T P, M T P, மற்றும் இருபத்தி நாலு மணி நேர ஜெமினி AI Coach எல்லாமே ஒரே இடத்துல இருக்கு.",
        "sub_en": "It covers all 3 student groups — CA Foundation, CA Intermediate Group I & II, and CA Final & SPOM — with 430+ verified questions, RTPs, MTPs, and a 24/7 Bilingual Gemini AI Coach.",
    },
    {
        "id": "02_workspace_a",
        "vo_ta": "முதல் tab, Exam and Coach Workspace. இதுல நீங்க ப்ளஸ் டூ முடிச்சுட்டு Foundation எழுதுறவங்களா இருந்தாலும் சரி, அல்லது டிகிரி முடிச்சுட்டு Direct Entry வழியா Intermediate மற்றும் Final எழுதுறவங்களா இருந்தாலும் சரி, உங்க லெவலுக்கு ஏத்த mock test அ உடனே தேர்ந்தெடுக்கலாம்.",
        "sub_en": "First is the Exam & Coach Workspace. Whether you enter via CA Foundation after Class 12 or Direct Entry into CA Intermediate and Final, pick your exact mock test instantly.",
    },
    {
        "id": "02_workspace_b",
        "vo_ta": "Foundation Paper 3 மற்றும் Paper 4 க்கு உரிய minus zero point two five நெகட்டிவ் மார்க்கிங், மற்றும் Inter, Final க்கு உரிய முப்பது சதவீத Case Scenario M C Q விதிமுறைகள் இங்க துல்லியமா பின்பற்றப்படுது. மேல இருக்கிற பட்டன்ல தமிழ் அல்லது இங்கிலீஷ்னு எப்ப வேணும்னாலும் மாத்திக்கலாம்.",
        "sub_en": "It enforces exact ICAI rules: -0.25 negative marking for Foundation MCQs and +2 / 0 for Inter & Final Case Scenarios, with instant English + Tamil switching.",
    },
    {
        "id": "03_practice_a",
        "vo_ta": "நீங்க எந்த ஒரு வினாவுக்கு விடை அளிச்சாலும், கம்பெனி சட்டம், வருமான வரிப் பிரிவு எண், ஜி எஸ் டி விதி, மற்றும் Accounting Standards படி, அதோட முழுமையான step by step working note இங்கிலீஷ் மற்றும் தமிழ்ல உடனேத் தெரியும்.",
        "sub_en": "As soon as you answer a question, it reveals the exact Companies Act, Income Tax, GST section, or Accounting Standard (AS / Ind AS) with step-by-step working notes in English and Tamil.",
    },
    {
        "id": "04_aicoach_a",
        "vo_ta": "படிக்கும்போது ஏதாவது ஒரு கணக்குலயோ சட்டப் பிரிவுலயோ சந்தேகம் வந்தா, கீழ இருக்கிற Ask Coach பட்டனையோ, அல்லது வலது பக்கம் இருக்கிற தமிழில் விளக்குக பட்டனையோ தட்டுங்க. நம்ம ஜெமினி AI C A Coach உடனேத் தெளிவா சொல்லிக் கொடுக்கும்.",
        "sub_en": "Stuck on a calculation or statutory section? Click 'Ask Coach' or 'Explain in Tamil' on the right, and the Gemini AI CA Coach walks you through the working notes immediately.",
    },
    {
        "id": "05_pyq_a",
        "vo_ta": "இரண்டாவது tab, I C A I Past Papers, R T P மற்றும் Case Scenarios Archive. இதுல கடந்த கால வினாத்தாள்கள், தமிழ் மீடியம் வினாத்தாள்கள், மற்றும் சட்டத் திருத்தங்களால் மாறிய முக்கிய வினாக்கள் தனி மாடியூலா கொடுக்கப்பட்டிருக்கு.",
        "sub_en": "The second tab is the ICAI Past Papers, RTPs & Case Scenarios Archive, including bilingual Tamil booklets and a Statutory Amendments & Disputed Questions dossier.",
    },
    {
        "id": "06_tracker_a",
        "vo_ta": "மூணாவது tab, Score, அறுபது சதவீத Exemption மற்றும் Aggregate Tracker. I C A I விதிப்படி ஒவ்வொரு தாளிலும் குறைந்தது நாப்பது சதவீதம், குரூப் மொத்தத்துல ஐம்பது சதவீதம், மற்றும் அறுபது சதவீதத்துக்கு மேல எடுத்தா கிடைக்கும் Three Attempt Exemption தகுதியை இது தானாகவே கணிச்சுச் சொல்லும்.",
        "sub_en": "The third tab is the Score, 60% Exemption & Aggregate Tracker — automatically checking ICAI's 40% paper floor, 50% group aggregate, and 60%+ 3-attempt paper exemption rule.",
    },
    {
        "id": "07_guide_a",
        "vo_ta": "நாலாவது tab, தமிழ்நாடு C A Guide மற்றும் அரசு இலவசப் பயிற்சி மையங்கள். தமிழ்நாடு அரசின் தாட்கோ நிறுவனம் வழங்கும் நூறு சதவீத இலவச C A பயிற்சி, நான் முதல்வன் திட்டம், I C A I கல்வி உதவித்தொகை, ஆனந்தம் அறக்கட்டளை, மற்றும் சென்னை, கோவை, மதுரை, திருச்சி உள்ளிட்ட பதின்மூன்று S I R C கிளைகளின் முழு விவரங்களும் இதுல இருக்கு.",
        "sub_en": "The fourth tab covers Tamil Nadu Free Public Coaching Institutes — TAHDCO 100% Free CA Coaching, Naan Mudhalvan, ICAI Scholarships, Charitable Trusts, and all 13 SIRC TN branches.",
    },
    {
        "id": "08_finale",
        "vo_ta": "தினமும் நம்பிக்கையோட பயிற்சி பண்ணுங்க, அறுபது சதவீத எக்ஸெம்ப்ஷனோட உங்க சார்ட்டர்ட் அக்கவுண்டன்ட் கனவு நிச்சயம் நனவாகும். All the best!",
        "sub_en": "Practice daily with confidence — claim your 60%+ exemptions and achieve your Chartered Accountant dream. All the Best!",
    },
]


def wav_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def fmt_srt_ts(sec: float) -> str:
    ms = int(round((sec % 1) * 1000))
    s = int(sec) % 60
    m = (int(sec) // 60) % 60
    h = int(sec) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fmt_vtt_ts(sec: float) -> str:
    return fmt_srt_ts(sec).replace(",", ".")


async def generate_voiceover_segments():
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    for seg in SEGMENTS:
        raw_mp3 = BUILD_DIR / f"{seg['id']}_raw.mp3"
        clean_wav = BUILD_DIR / f"{seg['id']}.wav"
        if not clean_wav.exists():
            await edge_tts.Communicate(seg["vo_ta"], voice=VOICE, rate=RATE).save(str(raw_mp3))
            af = (
                "silenceremove=start_periods=1:start_duration=0.03:start_threshold=-45dB:"
                "stop_periods=-1:stop_duration=0.30:stop_threshold=-42dB,"
                "highpass=f=80,"
                "equalizer=f=220:width_type=o:width=1.2:g=1.5,"
                "equalizer=f=3200:width_type=o:width=1.5:g=2.0,"
                "acompressor=threshold=-18dB:ratio=2.2:attack=15:release=160,"
                "loudnorm=I=-16:TP=-1.5:LRA=11,"
                "apad=pad_dur=0.25"
            )
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(raw_mp3), "-af", af, "-ar", "44100", "-ac", "2", str(clean_wav)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        seg["duration"] = wav_duration(clean_wav)
        seg["wav_path"] = clean_wav
        print(f"Segment {seg['id']}: {seg['duration']:.2f}s")


def build_master_audio_and_subtitles() -> Path:
    concat_txt = BUILD_DIR / "vo_concat.txt"
    lines = []
    srt_blocks = []
    vtt_blocks = ["WEBVTT\n"]
    cur_t = 0.0

    for idx, seg in enumerate(SEGMENTS, start=1):
        lines.append(f"file '{seg['wav_path']}'")
        start_t = cur_t
        end_t = cur_t + seg["duration"]
        cur_t = end_t
        seg["start_t"] = start_t
        seg["end_t"] = end_t

        srt_blocks.append(
            f"{idx}\n{fmt_srt_ts(start_t)} --> {fmt_srt_ts(end_t - 0.04)}\n{seg['sub_en']}\n"
        )
        vtt_blocks.append(
            f"{idx}\n{fmt_vtt_ts(start_t)} --> {fmt_vtt_ts(end_t - 0.04)}\n{seg['sub_en']}\n"
        )

    concat_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUTPUT_SRT.write_text("\n".join(srt_blocks), encoding="utf-8")
    OUTPUT_VTT.write_text("\n".join(vtt_blocks), encoding="utf-8")

    master_wav = BUILD_DIR / "master_vo.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
            "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", str(master_wav),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Master Voiceover ready: {master_wav} ({cur_t:.2f}s)")
    return master_wav


OVERLAY_INIT_JS = """() => {
  if (document.getElementById('__walkthrough_root__')) return;
  const root = document.createElement('div');
  root.id = '__walkthrough_root__';
  root.innerHTML = `
    <style>
      #intro-video-btn { display: none !important; }
      #__demo_focus__ {
        position: fixed;
        top: 0; left: 0; width: 0; height: 0;
        border: 2.5px solid #0d9488;
        border-radius: 10px;
        box-shadow: 0 0 0 4px rgba(13, 148, 136, 0.18), 0 12px 32px rgba(15, 23, 42, 0.16);
        pointer-events: none;
        z-index: 99990;
        opacity: 0;
        transition: all 0.45s cubic-bezier(0.22, 1, 0.36, 1);
      }
      #__demo_cursor__ {
        position: fixed;
        top: 0; left: 0;
        width: 28px; height: 28px;
        pointer-events: none;
        z-index: 99999;
        transform: translate(960px, 540px);
        transition: transform 0.55s cubic-bezier(0.22, 1, 0.36, 1);
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.35));
      }
      #__demo_ripple__ {
        position: absolute;
        top: -8px; left: -8px;
        width: 36px; height: 36px;
        border-radius: 50%;
        border: 2.5px solid #0d9488;
        background: rgba(13, 148, 136, 0.22);
        transform: scale(0.2);
        opacity: 0;
        pointer-events: none;
      }
      #__demo_ripple__.clicking {
        animation: __ripple_anim__ 0.5s ease-out forwards;
      }
      @keyframes __ripple_anim__ {
        0% { transform: scale(0.3); opacity: 1; }
        100% { transform: scale(1.75); opacity: 0; }
      }
      #__demo_subtitle_wrap__ {
        position: fixed;
        bottom: 22px;
        left: 0; right: 0;
        display: flex;
        justify-content: center;
        pointer-events: none;
        z-index: 99995;
        padding: 0 48px;
      }
      #__demo_subtitle__ {
        background: rgba(15, 23, 42, 0.92);
        backdrop-filter: blur(8px);
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif;
        font-size: 21px;
        font-weight: 600;
        line-height: 1.4;
        padding: 11px 28px;
        border-radius: 10px;
        max-width: 1460px;
        text-align: center;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.14);
      }
      #__demo_banner__ {
        position: fixed;
        inset: 0;
        background: rgba(15, 23, 42, 0.86);
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 99992;
        opacity: 1;
        transition: opacity 0.6s ease;
        pointer-events: none;
      }
      #__demo_banner__.hidden { opacity: 0; }
      .db-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 40px 54px;
        max-width: 980px;
        text-align: center;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.45);
        border-top: 6px solid #0d9488;
      }
      .db-eyebrow {
        display: inline-block;
        background: #f0fdf4;
        color: #0f766e;
        border: 1px solid #99f6e4;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        padding: 5px 14px;
        border-radius: 999px;
        margin-bottom: 16px;
      }
      .db-title {
        font-size: 34px;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.22;
        margin-bottom: 10px;
      }
      .db-sub-ta {
        font-size: 20px;
        font-weight: 700;
        color: #0f766e;
        margin-bottom: 20px;
      }
      .db-pills {
        display: flex;
        gap: 12px;
        justify-content: center;
        flex-wrap: wrap;
      }
      .db-pill {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        color: #1e293b;
        font-size: 14px;
        font-weight: 700;
        padding: 8px 16px;
        border-radius: 8px;
      }
    </style>

    <div id="__demo_focus__"></div>
    <div id="__demo_cursor__">
      <div id="__demo_ripple__"></div>
      <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M5.5 3.5L21.5 14.5L14 16L18 23.5L15 25L11 17.5L5.5 21.5V3.5Z" fill="#0F172A" stroke="white" stroke-width="2" stroke-linejoin="round"/>
      </svg>
    </div>

    <div id="__demo_banner__">
      <div class="db-card" id="__demo_banner_card__">
        <div class="db-eyebrow">Tamil Nadu ICAI CA Mastery Hub • SIRC Region</div>
        <div class="db-title">Complete Bilingual (English + தமிழ்) CA Foundation, Inter, Final &amp; SPOM Hub</div>
        <div class="db-sub-ta">தமிழக மாணவர்களின் சார்ட்டர்ட் அக்கவுண்டன்ட் (CA) கனவை நனவாக்கும் முழுமையான பயிற்சித் தளம்</div>
        <div class="db-pills">
          <span class="db-pill">3 ICAI Levels + SPOM Sets A–D</span>
          <span class="db-pill">432+ Verified Statutory &amp; RTP Questions</span>
          <span class="db-pill">TAHDCO &amp; 13 SIRC TN Branches Guide</span>
          <span class="db-pill">24/7 Bilingual Gemini AI CA Coach</span>
        </div>
      </div>
    </div>

    <div id="__demo_subtitle_wrap__">
      <div id="__demo_subtitle__"></div>
    </div>
  `;
  document.body.appendChild(root);

  window.__setSubtitle = (text) => {
    const el = document.getElementById('__demo_subtitle__');
    if (el) el.textContent = text || '';
  };

  window.__hideBanner = () => {
    const b = document.getElementById('__demo_banner__');
    if (b) b.classList.add('hidden');
  };

  window.__showFinaleBanner = () => {
    const b = document.getElementById('__demo_banner__');
    const c = document.getElementById('__demo_banner_card__');
    if (b && c) {
      c.innerHTML = `
        <div class="db-eyebrow">All The Best, Future Chartered Accountant! • வாழ்த்துகள்!</div>
        <div class="db-title">Master ICAI Concepts, Claim 60%+ Exemptions &amp; Succeed</div>
        <div class="db-sub-ta">தினமும் நம்பிக்கையோட பயிற்சி பண்ணுங்க, உங்க சார்ட்டர்ட் அக்கவுண்டன்ட் கனவு நிச்சயம் நனவாகும்!</div>
        <div class="db-pills">
          <span class="db-pill">Foundation (-0.25) &amp; Inter/Final Case MCQs</span>
          <span class="db-pill">40% Paper • 50% Aggregate • 60% Exemption</span>
          <span class="db-pill">TAHDCO &amp; ICAI BoS Free Coaching</span>
          <span class="db-pill">24/7 Bilingual Gemini AI CA Coach</span>
        </div>
      `;
      b.classList.remove('hidden');
    }
  };

  window.__moveCursorTo = (selector, clickRipple = false) => {
    const el = typeof selector === 'string' ? document.querySelector(selector) : selector;
    const cur = document.getElementById('__demo_cursor__');
    const rip = document.getElementById('__demo_ripple__');
    if (!el || !cur) return;
    const r = el.getBoundingClientRect();
    const cx = Math.round(r.left + Math.min(r.width * 0.45, 90));
    const cy = Math.round(r.top + Math.min(r.height * 0.5, 28));
    cur.style.transform = `translate(${cx}px, ${cy}px)`;
    if (clickRipple && rip) {
      rip.classList.remove('clicking');
      void rip.offsetWidth;
      setTimeout(() => rip.classList.add('clicking'), 450);
    }
  };

  window.__focusElement = (selector, color = '#0d9488') => {
    const foc = document.getElementById('__demo_focus__');
    if (!foc) return;
    if (!selector) {
      foc.style.opacity = '0';
      return;
    }
    const el = document.querySelector(selector);
    if (!el) {
      foc.style.opacity = '0';
      return;
    }
    const r = el.getBoundingClientRect();
    const pad = 6;
    foc.style.borderColor = color;
    foc.style.top = `${Math.max(4, r.top - pad)}px`;
    foc.style.left = `${Math.max(4, r.left - pad)}px`;
    foc.style.width = `${Math.min(window.innerWidth - 8, r.width + pad * 2)}px`;
    foc.style.height = `${Math.min(window.innerHeight - 85, r.height + pad * 2)}px`;
    foc.style.opacity = '1';
  };
}"""


async def wait_until_mono(t0: float, target_elapsed: float):
    rem = target_elapsed - (time.monotonic() - t0)
    if rem > 0:
        await asyncio.sleep(rem)


async def record_live_browser_walkthrough() -> tuple[Path, float]:
    video_tmp_dir = BUILD_DIR / "pw_video"
    if video_tmp_dir.exists():
        shutil.rmtree(video_tmp_dir)
    video_tmp_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(video_tmp_dir),
            record_video_size={"width": 1920, "height": 1080},
            device_scale_factor=1,
        )
        ctx_start = time.monotonic()
        page = await context.new_page()

        await page.goto("http://localhost:8096", wait_until="domcontentloaded")
        await asyncio.sleep(1.2)
        await page.evaluate("""() => {
            const prof = {
                student_id: "tn_ca_demo",
                name: "Kavin Kumar",
                district: "Chennai",
                board: "Level 2: CA Intermediate (Group I & II)",
                quota_category: "TAHDCO Free CA Coaching (Govt of TN)",
                language_pref: "bilingual",
                target_score: 65,
                custom_gemini_key: ""
            };
            localStorage.setItem("tn_ca_student_profile_v1", JSON.stringify(prof));
            localStorage.setItem("tn_ca_access_code_v1", "NEET720-7B6E13");
        }""")
        await page.reload(wait_until="domcontentloaded")
        await asyncio.sleep(1.5)
        await page.evaluate(OVERLAY_INIT_JS)
        await asyncio.sleep(0.3)

        t0 = time.monotonic()
        video_lead_in = t0 - ctx_start

        # 01_intro_a
        s = SEGMENTS[0]
        await page.evaluate(f"window.__setSubtitle({json.dumps(s['sub_en'])})")
        await asyncio.sleep(3.5)
        await page.evaluate("window.__hideBanner()")
        await asyncio.sleep(0.8)
        await page.evaluate("window.__moveCursorTo('.brand', false)")
        await page.evaluate("window.__focusElement('header', '#0d9488')")
        await wait_until_mono(t0, s["end_t"])

        # 01_intro_b
        s = SEGMENTS[1]
        await page.evaluate(f"window.__setSubtitle({json.dumps(s['sub_en'])})")
        await page.evaluate("window.__moveCursorTo('#module-select', true)")
        await page.evaluate("window.__focusElement('#module-select', '#0284c7')")
        await asyncio.sleep(3.5)
        await page.evaluate("window.__moveCursorTo('.desktop-nav-tabs', false)")
        await page.evaluate("window.__focusElement('.desktop-nav-tabs', '#0d9488')")
        await asyncio.sleep(3.5)
        await page.evaluate("window.__moveCursorTo('aside.coach-sidebar', false)")
        await page.evaluate("window.__focusElement('aside.coach-sidebar', '#0d9488')")
        await wait_until_mono(t0, s["end_t"])

        # 02_workspace_a
        s = SEGMENTS[2]
        await page.evaluate(f"window.__setSubtitle({json.dumps(s['sub_en'])})")
        await page.evaluate("window.__moveCursorTo('#subject-pills', true)")
        await page.evaluate("window.__focusElement('#subject-pills', '#0284c7')")
        await asyncio.sleep(3.5)
        await page.evaluate("window.__moveCursorTo('#question-card', false)")
        await page.evaluate("window.__focusElement('#question-card', '#0d9488')")
        await wait_until_mono(t0, s["end_t"])

        # 02_workspace_b
        s = SEGMENTS[3]
        await page.evaluate(f"window.__setSubtitle({json.dumps(s['sub_en'])})")
        await page.evaluate("""() => {
            selectBubble('D');
            renderOMRPalette();
            renderCurrentQuestion();
        }""")
        await page.evaluate("window.__moveCursorTo('aside.omr-sidebar', true)")
        await page.evaluate("window.__focusElement('aside.omr-sidebar', '#0d9488')")
        await asyncio.sleep(3.5)
        await page.evaluate("window.__moveCursorTo('#lang-select', true)")
        await page.evaluate("window.__focusElement('#lang-select', '#d97706')")
        await wait_until_mono(t0, s["end_t"])

        # 03_practice_a
        s = SEGMENTS[4]
        await page.evaluate(f"window.__setSubtitle({json.dumps(s['sub_en'])})")
        await page.evaluate("""() => {
            loadSelectedModule('ca_tax_gst_drill');
        }""")
        await asyncio.sleep(0.5)
        await page.evaluate("selectBubble('B')")
        await asyncio.sleep(0.6)
        await page.evaluate("revealPracticeSolution()")
        await asyncio.sleep(0.5)
        await page.evaluate("""() => {
            const qs = document.getElementById('question-scroll');
            if (qs) qs.scrollTo({ top: 180, behavior: 'smooth' });
        }""")
        await page.evaluate("window.__moveCursorTo('#solution-panel', false)")
        await page.evaluate("window.__focusElement('#solution-panel', '#059669')")
        await wait_until_mono(t0, s["end_t"])

        # 04_aicoach_a
        s = SEGMENTS[5]
        await page.evaluate(f"window.__setSubtitle({json.dumps(s['sub_en'])})")
        await page.evaluate("window.__moveCursorTo('.coach-quick-chips button:nth-child(2)', true)")
        await page.evaluate("window.__focusElement('aside.coach-sidebar', '#0d9488')")
        await asyncio.sleep(1.5)
        await page.evaluate("""() => {
            chatHistory = [
                {
                    sender: "coach",
                    text: "வணக்கம்! Welcome to your **Tamil Nadu ICAI CA Mastery Workspace**. Ask me in **English**, **தமிழ்**, or **Tanglish** for step-by-step statutory sections, AS/Ind AS working notes, or -0.25 trap analysis."
                },
                {
                    sender: "student",
                    text: "Explain Section 16(2) CGST Act 2017 Input Tax Credit (ITC) conditions in Tamil and English."
                },
                {
                    sender: "coach",
                    text: "**CGST Act 2017 — Section 16(2) Input Tax Credit (ITC) Conditions:**\\n\\n1. **Statutory Provision:** A registered person is entitled to ITC only when (a) they possess a valid tax invoice/debit note, (b) details are communicated in **GSTR-2B**, (c) goods/services have been **actually received**, (d) tax has been paid to the Government, and (e) return under **Sec 39 (GSTR-3B)** is filed.\\n2. **180-Day Rule (2nd Proviso to Sec 16(2)):** Value + tax must be paid to the supplier within **180 days** from invoice date (except reverse charge), otherwise ITC is reversed with **18% interest u/s 50**.\\n3. **தமிழ் விளக்கம்:** சரக்கு அல்லது சேவை பெறப்பட்டு, GSTR-2B-ல் விவரம் பதிவாகி, 180 நாட்களுக்குள் சப்ளையருக்குத் தொகை செலுத்தப்பட்டால் மட்டுமே ITC கோர முடியும்!"
                }
            ];
            renderChat();
        }""")
        await page.evaluate("window.__moveCursorTo('#coach-messages', false)")
        await page.evaluate("window.__focusElement('#coach-messages', '#0d9488')")
        await wait_until_mono(t0, s["end_t"])

        # 05_pyq_a
        s = SEGMENTS[6]
        await page.evaluate(f"window.__setSubtitle({json.dumps(s['sub_en'])})")
        await page.evaluate("window.__moveCursorTo('.desktop-nav-tabs button:nth-child(2)', true)")
        await asyncio.sleep(0.5)
        await page.evaluate("switchView('pyq')")
        await asyncio.sleep(0.5)
        await page.evaluate("window.__focusElement('#pyq-overview-kpis', '#0284c7')")
        await asyncio.sleep(3.0)
        await page.evaluate("""() => {
            const sc = document.querySelector('#view-pyq .page-scroll');
            if (sc) sc.scrollTo({ top: 450, behavior: 'smooth' });
        }""")
        await asyncio.sleep(0.8)
        await page.evaluate("window.__focusElement('#pyq-paper-cards', '#0d9488')")
        await wait_until_mono(t0, s["end_t"])

        # 06_tracker_a
        s = SEGMENTS[7]
        await page.evaluate(f"window.__setSubtitle({json.dumps(s['sub_en'])})")
        await page.evaluate("window.__moveCursorTo('.desktop-nav-tabs button:nth-child(3)', true)")
        await asyncio.sleep(0.5)
        await page.evaluate("switchView('tracker')")
        await asyncio.sleep(0.5)
        await page.evaluate("window.__focusElement('#tracker-kpis', '#0d9488')")
        await asyncio.sleep(3.5)
        await page.evaluate("window.__focusElement('#view-tracker .section-card:nth-of-type(1)', '#0284c7')")
        await wait_until_mono(t0, s["end_t"])

        # 07_guide_a
        s = SEGMENTS[8]
        await page.evaluate(f"window.__setSubtitle({json.dumps(s['sub_en'])})")
        await page.evaluate("window.__moveCursorTo('.desktop-nav-tabs button:nth-child(4)', true)")
        await asyncio.sleep(0.5)
        await page.evaluate("switchView('guide')")
        await asyncio.sleep(0.5)
        await page.evaluate("window.__focusElement('#view-guide .section-card:nth-of-type(1)', '#0d9488')")
        await asyncio.sleep(4.5)
        await page.evaluate("""() => {
            const sc = document.querySelector('#view-guide .page-scroll');
            if (sc) sc.scrollTo({ top: 420, behavior: 'smooth' });
        }""")
        await asyncio.sleep(0.8)
        await page.evaluate("window.__focusElement('#view-guide .section-card:nth-of-type(2)', '#0284c7')")
        await wait_until_mono(t0, s["end_t"])

        # 08_finale
        s = SEGMENTS[9]
        await page.evaluate(f"window.__setSubtitle({json.dumps(s['sub_en'])})")
        await page.evaluate("window.__focusElement(null)")
        await page.evaluate("window.__showFinaleBanner()")
        await wait_until_mono(t0, s["end_t"])

        video_path_str = await page.video.path()
        await context.close()
        await browser.close()
        return Path(video_path_str), video_lead_in


def mux_final_mp4(raw_webm: Path, video_lead_in: float, master_wav: Path, total_dur: float):
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", f"{video_lead_in:.3f}",
            "-i", str(raw_webm),
            "-i", str(master_wav),
            "-i", str(OUTPUT_SRT),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-map", "2:s:0",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-r", "24",
            "-c:a", "aac",
            "-b:a", "160k",
            "-ar", "44100",
            "-c:s", "mov_text",
            "-metadata:s:a:0", "language=tam",
            "-metadata:s:a:0", "title=Tamil (CA Mentor Walkthrough)",
            "-metadata:s:s:0", "language=eng",
            "-metadata:s:s:0", "title=English Subtitles",
            "-t", f"{total_dur:.2f}",
            "-movflags", "+faststart",
            str(OUTPUT_MP4),
        ],
        check=True,
    )
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    size_mb = OUTPUT_MP4.stat().st_size / (1024 * 1024)
    print(f"SUCCESS: {OUTPUT_MP4} ({size_mb:.2f} MB, {total_dur:.1f}s)")


async def main():
    await generate_voiceover_segments()
    master_wav = build_master_audio_and_subtitles()
    total_dur = SEGMENTS[-1]["end_t"]
    raw_webm, video_lead_in = await record_live_browser_walkthrough()
    mux_final_mp4(raw_webm, video_lead_in, master_wav, total_dur)


if __name__ == "__main__":
    asyncio.run(main())
