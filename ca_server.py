#!/usr/bin/env python3
"""
Tamil Nadu CA (Chartered Accountant) Mastery Hub & Bilingual (Tamil + English) Gemini AI Coach Server.
- Serves the interactive ICAI CA Mock Exam & Case-Scenario Practice SPA (Foundation, Intermediate Group I & II, Final & SPOM).
- Grades mock/practice exams server-side against verified questions_bank.json & past_papers_archive.json,
  supporting both CA Foundation Objective MCQ (-0.25 negative marking) and CA Inter/Final/SPOM Case-Scenario MCQ (2M, 0 negative),
  plus automatic ICAI 40% Subject Minimum, 50% Group Aggregate, and 60%+ Permanent/3-Attempt Exemption evaluation.
- Tracks student scores, negative marks, level-wise mastery, and mistake bank in SQLite
  (ca_data.db) + readable mentor summary (student_score_ledger.json).
- Powers the Multilingual (Tamil, Tanglish, English) AI CA Coach using Google Gemini
  (Cloud Gemini REST API via GEMINI_API_KEY, local Gemini via agy CLI, + offline ICAI Statutory/BoS fallback).
"""

import hashlib
import hmac
import html
import http.server
import json
import os
import re
import secrets
import shlex
import smtplib
import socketserver
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

PORT = int(os.environ.get("PORT", "8096"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ca_data.db")
LEDGER_PATH = os.path.join(BASE_DIR, "student_score_ledger.json")
QUESTIONS_PATH = os.path.join(BASE_DIR, "questions_bank.json")
PAST_PAPERS_PATH = os.path.join(BASE_DIR, "past_papers_archive.json")
AGY_BIN = os.environ.get("AGY_BIN", os.path.expanduser("~/.local/bin/agy"))
ADMIN_SECRETS_PATH = os.environ.get(
    "CA_ADMIN_SECRETS_PATH",
    os.path.expanduser("~/.config/ca-prep/admin_secrets.json"),
)

DB_LOCK = threading.Lock()
IP_RATE_LOCK = threading.Lock()
IP_REQUEST_BUCKET = {}

CA_SUBJECT_BUCKETS = (
    "CA Foundation",
    "CA Inter G1",
    "CA Inter G2",
    "CA Final & SPOM",
)


def load_admin_secrets() -> dict:
    """Loads private owner config from outside the git repository (~/.config/ca-prep/admin_secrets.json)."""
    defaults = {
        "owner_notify_email": "",
        "hmac_secret": "default-local-dev-hmac-change-me",
        "admin_key": "",
        "master_passcode": "",
        "ga_measurement_id": "G-KGL9DJNFNR",
        "public_frontend_url": "https://thameema.github.io/ca-prep",
        "public_api_url": "http://localhost:8096",
        "daily_ai_limit_per_code": 40,
        "max_devices_per_code": 2,
        "sender_display_name": "Tamil Nadu CA Mastery Hub (ICAI Foundation • Inter • Final)",
        "sender_noreply_email": "noreply@sirath.com",
        "enforce_access_gate": True,
        "doppler_scope": "/Users/thameema/Documents/ai/zudioz",
        "doppler_project": "sirath-spaces",
        "doppler_config": "prd",
        "resend_api_key": "",
        "gas_webhook_url": "",
        "smtp_host": "",
        "smtp_port": 587,
        "smtp_user": "",
        "smtp_pass": "",
    }
    try:
        if os.path.exists(ADMIN_SECRETS_PATH):
            with open(ADMIN_SECRETS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                defaults.update(data)
    except Exception as exc:
        print(f"[CA-Auth] Warning loading admin secrets: {exc}", file=sys.stderr)
    return defaults


QUESTION_BANK = {"metadata": {}, "modules": {}, "questions": []}
PAST_PAPERS_ARCHIVE = {}
QUESTIONS_BY_ID = {}


def reload_question_banks():
    global QUESTION_BANK, PAST_PAPERS_ARCHIVE, QUESTIONS_BY_ID
    if os.path.exists(QUESTIONS_PATH):
        with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
            QUESTION_BANK = json.load(f)
    if os.path.exists(PAST_PAPERS_PATH):
        with open(PAST_PAPERS_PATH, "r", encoding="utf-8") as f:
            PAST_PAPERS_ARCHIVE = json.load(f)
        QUESTION_BANK.setdefault("modules", {}).update(PAST_PAPERS_ARCHIVE.get("modules", {}))
        existing_ids = {int(q["id"]) for q in QUESTION_BANK.get("questions", [])}
        for pq in PAST_PAPERS_ARCHIVE.get("questions", []):
            if int(pq["id"]) not in existing_ids:
                QUESTION_BANK.setdefault("questions", []).append(pq)
                existing_ids.add(int(pq["id"]))
    QUESTIONS_BY_ID = {int(q["id"]): q for q in QUESTION_BANK.get("questions", [])}


reload_question_banks()


def init_db():
    with DB_LOCK:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                district TEXT DEFAULT 'Chennai (SIRC HQ)',
                board TEXT DEFAULT 'Level 1: CA Foundation (After Class 12)',
                quota_category TEXT DEFAULT 'ICAI BoS Free Live + TAHDCO / SSP Scholarship',
                language_pref TEXT DEFAULT 'bilingual',
                target_score INTEGER DEFAULT 65,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS exam_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                student_name TEXT NOT NULL,
                module_id TEXT NOT NULL,
                module_title TEXT NOT NULL,
                mode TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                attempted INTEGER NOT NULL,
                correct_count INTEGER NOT NULL,
                wrong_count INTEGER NOT NULL,
                unanswered_count INTEGER NOT NULL,
                raw_score REAL NOT NULL,
                max_score REAL NOT NULL,
                negative_marks_lost REAL NOT NULL,
                accuracy_pct REAL NOT NULL,
                projected_720 INTEGER NOT NULL,
                tn_college_tier TEXT NOT NULL,
                time_spent_sec INTEGER NOT NULL,
                subject_breakdown_json TEXT NOT NULL,
                answers_json TEXT NOT NULL,
                wrong_question_ids_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS coach_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                student_name TEXT NOT NULL,
                question_id INTEGER,
                subject TEXT,
                user_choice TEXT,
                language_detected TEXT NOT NULL,
                student_message TEXT NOT NULL,
                coach_reply TEXT NOT NULL,
                engine_used TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS access_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_token TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                district TEXT DEFAULT '',
                purpose TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                access_code TEXT UNIQUE,
                max_devices INTEGER NOT NULL DEFAULT 2,
                daily_ai_limit INTEGER NOT NULL DEFAULT 40,
                ip_address TEXT DEFAULT '',
                user_agent TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                approved_at TEXT DEFAULT ''
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS access_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                access_code TEXT NOT NULL,
                device_id TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                UNIQUE(access_code, device_id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS analytics_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                student_id TEXT DEFAULT '',
                access_code TEXT DEFAULT '',
                page_url TEXT DEFAULT '',
                meta_json TEXT DEFAULT '{}',
                ip_address TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()


def sign_admin_token(request_token: str, action: str) -> str:
    cfg = load_admin_secrets()
    key = str(cfg.get("hmac_secret") or "ca-hmac").encode("utf-8")
    msg = f"{request_token}:{action}".encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def verify_admin_token(request_token: str, action: str, sig: str) -> bool:
    if not request_token or not action or not sig:
        return False
    expected = sign_admin_token(request_token, action)
    return hmac.compare_digest(expected, str(sig).strip())


def generate_unique_access_code() -> str:
    alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    return "CA-" + "".join(secrets.choice(alphabet) for _ in range(6))


def check_ip_rate_limit(ip: str, bucket_key: str, max_hits: int, window_sec: int = 3600) -> bool:
    now = time.time()
    key = f"{bucket_key}:{ip}"
    with IP_RATE_LOCK:
        hits = [t for t in IP_REQUEST_BUCKET.get(key, []) if now - t < window_sec]
        if len(hits) >= max_hits:
            IP_REQUEST_BUCKET[key] = hits
            return False
        hits.append(now)
        IP_REQUEST_BUCKET[key] = hits
        return True


def send_outbound_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str,
    is_owner_alert: bool = False,
    structured_fields: dict | None = None,
) -> dict:
    """
    Sends a rich HTML + plain-text email without ever exposing the owner's personal email address to the requester.
    Uses Amazon SES (`sesv2`) via Doppler (`doppler run` in Zudioz scope) or SSH Postfix relay.
    """
    cfg = load_admin_secrets()
    sender_name = cfg.get("sender_display_name") or "Tamil Nadu CA Mastery Hub (ICAI Foundation • Inter • Final)"
    sender_email = cfg.get("sender_noreply_email") or "noreply@sirath.com"
    sender_domain = sender_email.split("@")[-1] if "@" in sender_email else "sirath.com"

    if is_owner_alert:
        try:
            subprocess.Popen(
                [
                    "osascript",
                    "-e",
                    f'display notification "{text_body[:140].replace(chr(34), chr(39))}" with title "CA Mastery Hub Access Pass"',
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    doppler_scope = str(cfg.get("doppler_scope") or "/Users/thameema/Documents/ai/zudioz").strip()
    doppler_project = str(cfg.get("doppler_project") or "sirath-spaces").strip()
    doppler_config = str(cfg.get("doppler_config") or "prd").strip()
    if doppler_project and doppler_config:
        try:
            ses_payload = json.dumps({
                "from": f"{sender_name} <{sender_email}>",
                "reply_to": sender_email,
                "to": to_email,
                "subject": subject,
                "text": text_body,
                "html": html_body,
            }).encode("utf-8")
            ses_py = (
                "import sys, os, json, boto3; "
                "d = json.load(sys.stdin); "
                "reg = os.environ.get('AWS_SES_REGION') or os.environ.get('AWS_REGION') or 'us-east-1'; "
                "ses = boto3.client('sesv2', region_name=reg); "
                "r = ses.send_email("
                "FromEmailAddress=d['from'], "
                "ReplyToAddresses=[d['reply_to']], "
                "Destination={'ToAddresses': [d['to']]}, "
                "Content={'Simple': {"
                "'Subject': {'Data': d['subject'], 'Charset': 'UTF-8'}, "
                "'Body': {"
                "'Text': {'Data': d['text'], 'Charset': 'UTF-8'}, "
                "'Html': {'Data': d['html'], 'Charset': 'UTF-8'}"
                "}}}); "
                "print(r.get('MessageId', ''))"
            )
            cmd = ["doppler", "run"]
            if doppler_scope and os.path.exists(doppler_scope):
                cmd.extend(["--scope", doppler_scope])
            cmd.extend(["-p", doppler_project, "-c", doppler_config, "--", sys.executable, "-c", ses_py])
            proc = subprocess.run(cmd, input=ses_payload, capture_output=True, timeout=14)
            if proc.returncode == 0 and proc.stdout.decode("utf-8", "ignore").strip():
                msg_id = proc.stdout.decode("utf-8", "ignore").strip().splitlines()[-1]
                return {"sent": True, "transport": "aws_ses_doppler", "message_id": msg_id}
            print(f"[CA-Email] Doppler SES warning: {proc.stderr.decode('utf-8', 'ignore')}", file=sys.stderr)
        except Exception as exc:
            print(f"[CA-Email] Doppler SES error: {exc}", file=sys.stderr)

    ssh_mail_host = str(cfg.get("ssh_mail_host") or "").strip()
    if ssh_mail_host and re.match(r"^[A-Za-z0-9._@-]+$", ssh_mail_host):
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{sender_name} <{sender_email}>"
            msg["To"] = to_email
            msg["Date"] = formatdate(localtime=True)
            msg["Message-ID"] = make_msgid(domain=sender_domain)
            msg.attach(MIMEText(text_body, "plain", "utf-8"))
            msg.attach(MIMEText(html_body, "html", "utf-8"))
            raw_bytes = msg.as_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")

            remote_py = f"""
import sys, hashlib, base64, subprocess, os
raw = sys.stdin.buffer.read()
sep = b"\\r\\n\\r\\n"
hdr_raw, body_raw = raw.split(sep, 1) if sep in raw else (raw, b"")
body_canon = body_raw.rstrip(b"\\r\\n") + b"\\r\\n"
bh = base64.b64encode(hashlib.sha256(body_canon).digest()).decode()
key_path = "/etc/opendkim/userkeys/{sender_domain}/default.private"
if os.path.exists(key_path):
    hdr_lines = hdr_raw.split(b"\\r\\n")
    sign_names = []
    signed_hdrs = []
    for line in hdr_lines:
        for h in (b"From", b"To", b"Subject", b"Date", b"Message-ID"):
            if line.lower().startswith(h.lower() + b":"):
                sign_names.append(h.decode().lower())
                signed_hdrs.append(line)
    dkim_stub = f"DKIM-Signature: v=1; a=rsa-sha256; c=simple/simple; d={sender_domain}; s=default; h={{':'.join(sign_names)}}; bh={{bh}}; b=".encode()
    to_sign = b"\\r\\n".join(signed_hdrs) + b"\\r\\n" + dkim_stub
    sig_bin = subprocess.check_output(["openssl", "dgst", "-sha256", "-sign", key_path], input=to_sign)
    sig_b64 = base64.b64encode(sig_bin).decode()
    raw = dkim_stub + sig_b64.encode() + b"\\r\\n" + hdr_raw + sep + body_canon
subprocess.run(["/usr/sbin/sendmail", "-t", "-i", "-f", "{sender_email}"], input=raw, check=True)
"""
            proc = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=8",
                    ssh_mail_host,
                    "python3 -c " + shlex.quote(remote_py),
                ],
                input=raw_bytes,
                capture_output=True,
                timeout=14,
            )
            if proc.returncode == 0:
                return {"sent": True, "transport": "direct_dkim_postfix"}
        except Exception as exc:
            print(f"[CA-Email] SSH Postfix error: {exc}", file=sys.stderr)

    return {"sent": False, "transport": "queued_in_db_and_live_poll"}


def validate_student_access_code(
    code: str,
    device_id: str = "",
    ip_addr: str = "",
    user_agent: str = "",
    consume_ai_quota: bool = False,
) -> dict:
    clean_code = str(code or "").strip().upper()
    clean_dev = str(device_id or "default_device").strip()[:80]
    if not clean_code:
        return {"valid": False, "reason": "Access code required. Please enter your Access Code or click 'New Here? Get Free Pass'."}

    cfg = load_admin_secrets()
    master_code = str(cfg.get("master_passcode") or "").strip().upper()
    if master_code and hmac.compare_digest(clean_code, master_code):
        return {
            "valid": True,
            "code": clean_code,
            "name": "Verified CA Mentor",
            "email": "",
            "daily_ai_limit": 500,
            "ai_used_today": 0,
            "is_master": True,
        }

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_prefix = datetime.now().strftime("%Y-%m-%d")

    with DB_LOCK:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM access_requests WHERE UPPER(access_code) = ? LIMIT 1",
            (clean_code,),
        )
        row = cur.fetchone()
        if not row:
            conn.close()
            return {"valid": False, "reason": "Invalid Access Code. Please check the code or get a free pass."}

        rec = dict(row)
        if rec.get("status") != "approved":
            conn.close()
            return {"valid": False, "reason": f"This access code is currently {rec.get('status')}."}

        max_devs = int(rec.get("max_devices") or cfg.get("max_devices_per_code") or 2)
        cur.execute(
            "SELECT device_id FROM access_devices WHERE access_code = ?",
            (clean_code,),
        )
        known_devs = [r["device_id"] for r in cur.fetchall()]
        if clean_dev not in known_devs:
            if len(known_devs) >= max_devs:
                conn.close()
                return {
                    "valid": False,
                    "reason": f"Device limit reached ({max_devs} devices max per student code). Access codes cannot be shared.",
                }
            cur.execute(
                "INSERT OR IGNORE INTO access_devices (access_code, device_id, first_seen_at, last_seen_at) VALUES (?, ?, ?, ?)",
                (clean_code, clean_dev, now_str, now_str),
            )
        else:
            cur.execute(
                "UPDATE access_devices SET last_seen_at = ? WHERE access_code = ? AND device_id = ?",
                (now_str, clean_code, clean_dev),
            )

        daily_limit = int(rec.get("daily_ai_limit") or cfg.get("daily_ai_limit_per_code") or 40)
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM analytics_events WHERE access_code = ? AND event_name = 'ai_coach_query' AND created_at LIKE ?",
            (clean_code, f"{today_prefix}%"),
        )
        used_today = int(cur.fetchone()["cnt"] or 0)

        if consume_ai_quota and used_today >= daily_limit:
            conn.commit()
            conn.close()
            return {
                "valid": False,
                "quota_exceeded": True,
                "reason": f"Daily AI Coach limit reached ({daily_limit} questions/day for this code). Offline ICAI BoS bilingual explanations remain unlimited.",
            }

        if consume_ai_quota:
            cur.execute(
                "INSERT INTO analytics_events (event_name, student_id, access_code, page_url, meta_json, ip_address, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("ai_coach_query", rec.get("email", ""), clean_code, "/api/chat", "{}", "", now_str),
            )
            used_today += 1

        conn.commit()
        conn.close()

    return {
        "valid": True,
        "code": clean_code,
        "name": rec.get("name") or "CA Aspirant",
        "email": rec.get("email") or "",
        "district": rec.get("district") or "Chennai",
        "daily_ai_limit": daily_limit,
        "ai_used_today": used_today,
    }


def sync_mentor_ledger():
    """Exports a clean, human-readable JSON ledger of all attempts for mentor/coach tracking."""
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, student_id, student_name, module_id, module_title, mode,
                       total_questions, attempted, correct_count, wrong_count, unanswered_count,
                       raw_score, max_score, negative_marks_lost, accuracy_pct, projected_720,
                       tn_college_tier, time_spent_sec, subject_breakdown_json, wrong_question_ids_json, created_at
                FROM exam_attempts
                ORDER BY id DESC
                LIMIT 200
                """
            )
            rows = [dict(r) for r in cur.fetchall()]
            for r in rows:
                r["subject_breakdown"] = json.loads(r.pop("subject_breakdown_json", "{}"))
                r["wrong_question_ids"] = json.loads(r.pop("wrong_question_ids_json", "[]"))
            conn.close()

        summary = {
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_attempts_recorded": len(rows),
            "best_projected_720": max((r["projected_720"] for r in rows), default=0),
            "average_projected_720": round(sum(r["projected_720"] for r in rows) / len(rows), 1) if rows else 0,
            "attempts": rows,
        }
        with open(LEDGER_PATH, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        print(f"Ledger sync warning: {exc}", file=sys.stderr)


def evaluate_icai_pass_and_exemption_status(score_pct: int, level_category: str = "") -> str:
    """
    Evaluates a CA student's percentage score (0-100) against ICAI's strict three-tier rule:
      - >= 70%: Pass with Distinction + Permanent/3-Attempt Exemption (60%+) + AIR Rank Trajectory
      - >= 60%: EXEMPTION SECURED (60%+) + Group Aggregate Cleared (50%+)
      - >= 50%: GROUP AGGREGATE CLEARED (50%+) & Individual Paper Passed (40%+)
      - 40% - 49%: Individual Paper Minimum Cleared (40%+), but SHORT OF 50% GROUP AGGREGATE
      - < 40%: Below 40% ICAI Individual Paper Passing Floor
    """
    if score_pct >= 70:
        return "ICAI Distinction & Rank Trajectory (70%+) — 60%+ Paper Exemption & 50% Aggregate Cleared!"
    if score_pct >= 60:
        return "ICAI 60%+ EXEMPTION SECURED — Exempt for Next 3 Attempts & 50% Group Aggregate Cleared!"
    if score_pct >= 50:
        return "ICAI PASS (50%+ Group Aggregate & 40%+ Paper Minimum Met) — Aim for 60%+ Exemption!"
    if score_pct >= 40:
        return "40% Paper Floor Met, but Below 50% ICAI Group Aggregate — Need +10% in Practical/MCQ Papers"
    return "Below 40% ICAI Paper Minimum — Focus on BoS Case Scenarios, AS/Ind AS & Statutory Amendments"


def grade_exam_submission(payload: dict) -> dict:
    reload_question_banks()
    student_id = str(payload.get("student_id") or "default_student").strip()
    student_name = str(payload.get("student_name") or "CA Aspirant").strip()
    quota_category = str(payload.get("quota_category") or "ICAI New Scheme").strip()
    module_id = str(payload.get("module_id") or "ca_all_levels_mock_1").strip()
    module_title = str(payload.get("module_title") or "ICAI CA Mock Test").strip()
    mode = str(payload.get("mode") or "mock").strip()
    time_spent_sec = max(0, int(payload.get("time_spent_sec") or 0))
    question_ids = payload.get("question_ids") or []
    answers = payload.get("answers") or {}

    mod = QUESTION_BANK.get("modules", {}).get(module_id) or {}
    if not question_ids:
        if mod.get("questionIds"):
            question_ids = mod["questionIds"]
        else:
            question_ids = [int(k) for k in answers.keys() if str(k).isdigit()]

    marking = mod.get("marking") or {}
    default_corr = float(marking.get("correct", 2.0))
    default_wrong = float(marking.get("wrong", -0.25))

    subjects = {}
    for subj in CA_SUBJECT_BUCKETS:
        subjects[subj] = {
            "total": 0,
            "attempted": 0,
            "correct": 0,
            "wrong": 0,
            "unanswered": 0,
            "score": 0.0,
            "max_score": 0.0,
        }

    total_q = 0
    correct_count = 0
    wrong_count = 0
    unanswered_count = 0
    wrong_q_ids = []
    per_question_review = []
    raw_score = 0.0
    max_score = 0.0
    negative_marks_lost = 0.0

    for raw_qid in question_ids:
        qid = int(raw_qid)
        q = QUESTIONS_BY_ID.get(qid)
        if not q:
            continue
        total_q += 1
        subj = q.get("subject") or "CA Foundation"
        if subj not in subjects:
            subjects[subj] = {
                "total": 0,
                "attempted": 0,
                "correct": 0,
                "wrong": 0,
                "unanswered": 0,
                "score": 0.0,
                "max_score": 0.0,
            }

        # Determine authentic ICAI marking per question or module
        q_corr = float(q.get("marks_correct", default_corr))
        # Foundation Papers 3 & 4 have -0.25 negative marking; Inter/Final/SPOM have 0 negative marking unless module specifies
        if "Foundation" in subj:
            q_wrong = float(q.get("marks_wrong", -0.25 if default_wrong < 0 else default_wrong))
        else:
            q_wrong = float(q.get("marks_wrong", 0.0))

        subjects[subj]["total"] += 1
        subjects[subj]["max_score"] += q_corr
        max_score += q_corr

        chosen = str(answers.get(str(qid)) or answers.get(qid) or "").strip().upper()
        truth = q["correct"]
        acc_opts = set(q.get("acceptedOptions") or [truth])
        ans_status = q.get("answerStatus") or "normal"

        if ans_status == "dropped":
            status = "correct"
            marks = q_corr
            correct_count += 1
            raw_score += q_corr
            subjects[subj]["attempted"] += 1
            subjects[subj]["correct"] += 1
            subjects[subj]["score"] += q_corr
        elif not chosen:
            status = "unanswered"
            marks = 0.0
            unanswered_count += 1
            subjects[subj]["unanswered"] += 1
        elif chosen in acc_opts:
            status = "correct"
            marks = q_corr
            correct_count += 1
            raw_score += q_corr
            subjects[subj]["attempted"] += 1
            subjects[subj]["correct"] += 1
            subjects[subj]["score"] += q_corr
        else:
            status = "wrong"
            marks = q_wrong
            wrong_count += 1
            wrong_q_ids.append(qid)
            raw_score += q_wrong
            negative_marks_lost += abs(q_wrong)
            subjects[subj]["attempted"] += 1
            subjects[subj]["wrong"] += 1
            subjects[subj]["score"] += q_wrong

        per_question_review.append(
            {
                "question_id": qid,
                "subject": subj,
                "chapter": q.get("chapter", ""),
                "chosen": chosen or None,
                "correct": truth,
                "status": status,
                "marks": round(marks, 2),
            }
        )

    attempted = correct_count + wrong_count
    raw_score = round(raw_score, 2)
    max_score = round(max_score, 2)
    negative_marks_lost = round(negative_marks_lost, 2)
    accuracy_pct = round((correct_count / attempted) * 100.0, 1) if attempted > 0 else 0.0
    # projected_720 stores the normalized 0-100 ICAI Paper/Group Percentage for full UI compatibility
    projected_100 = round((raw_score / max_score) * 100) if max_score > 0 else 0
    projected_100 = max(-25, min(100, int(projected_100)))
    icai_verdict = evaluate_icai_pass_and_exemption_status(projected_100, quota_category)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for k in subjects:
        subjects[k]["score"] = round(subjects[k]["score"], 2)
        subjects[k]["max_score"] = round(subjects[k]["max_score"], 2)
    active_subjects = {k: v for k, v in subjects.items() if v["total"] > 0}

    with DB_LOCK:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO exam_attempts (
                student_id, student_name, module_id, module_title, mode,
                total_questions, attempted, correct_count, wrong_count, unanswered_count,
                raw_score, max_score, negative_marks_lost, accuracy_pct, projected_720,
                tn_college_tier, time_spent_sec, subject_breakdown_json, answers_json,
                wrong_question_ids_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student_id,
                student_name,
                module_id,
                module_title,
                mode,
                total_q,
                attempted,
                correct_count,
                wrong_count,
                unanswered_count,
                raw_score,
                max_score,
                negative_marks_lost,
                accuracy_pct,
                projected_100,
                icai_verdict,
                time_spent_sec,
                json.dumps(active_subjects, ensure_ascii=False),
                json.dumps(answers, ensure_ascii=False),
                json.dumps(wrong_q_ids),
                now_str,
            ),
        )
        attempt_id = cur.lastrowid
        conn.commit()
        conn.close()

    sync_mentor_ledger()

    return {
        "attempt_id": attempt_id,
        "student_id": student_id,
        "student_name": student_name,
        "module_id": module_id,
        "module_title": module_title,
        "mode": mode,
        "total_questions": total_q,
        "attempted": attempted,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "unanswered_count": unanswered_count,
        "raw_score": raw_score,
        "max_score": max_score,
        "negative_marks_lost": negative_marks_lost,
        "accuracy_pct": accuracy_pct,
        "projected_720": projected_100,
        "tn_college_tier": icai_verdict,
        "time_spent_sec": time_spent_sec,
        "subject_breakdown": active_subjects,
        "wrong_question_ids": wrong_q_ids,
        "per_question_review": per_question_review,
        "created_at": now_str,
    }


def detect_language_intent(student_msg: str, ui_lang_pref: str = "bilingual") -> str:
    msg = (student_msg or "").strip()
    if re.search(r"[\u0B80-\u0BFF]", msg):
        return "tamil_script"
    lower = msg.lower()
    tanglish_markers = (
        "tamil", "தமிழில்", "enna", "epdi", "eppadi", "puriyala", "sollunga",
        "vilakkam", "yen ", "thavaru", "sari", "puriyavillai", "konjam",
    )
    if any(tok in lower for tok in tanglish_markers):
        return "tamil_requested"
    if ui_lang_pref in ("ta", "tamil"):
        return "tamil_preferred"
    if ui_lang_pref == "bilingual":
        return "bilingual"
    return "english"


def build_ca_gemini_prompt(
    q_data: dict,
    question_number: int,
    user_choice: str,
    student_msg: str,
    student_name: str,
    lang_intent: str,
    recent_history: list,
) -> str:
    reload_question_banks()
    q = q_data or {}
    qid = q.get("id")
    if qid and int(qid) in QUESTIONS_BY_ID:
        q = QUESTIONS_BY_ID[int(qid)]

    subj = q.get("subject", "ICAI CA")
    chapter = q.get("chapter", "")
    statutory_ref = q.get("ncertRef", "ICAI BoS Study Material")
    stem_en = q.get("stem_en", "")
    stem_ta = q.get("stem_ta", "")
    correct = q.get("correct", "")
    exp_en = q.get("explanation_en", "")
    exp_ta = q.get("explanation_ta", "")
    key_pt = q.get("ncert_key_point", "")
    traps = q.get("trap_breakdown") or {}
    choices = q.get("choices") or []
    vid = q.get("videoTutorial") or {}

    choices_block = "\n".join(
        f"  ({c.get('letter')}) {c.get('text_en')} | தமிழ்: {c.get('text_ta')}"
        for c in choices
    ) or "  (General ICAI CA conceptual / statutory / strategy query)"

    traps_block = "\n".join(
        f"  Option {k}: {v}" for k, v in traps.items()
    ) or "  None"

    hist_lines = []
    if isinstance(recent_history, list):
        for turn in recent_history[-6:]:
            if isinstance(turn, dict) and turn.get("text"):
                role = "Student" if turn.get("sender") == "student" else "CA Coach"
                hist_lines.append(f"{role}: {str(turn['text'])[:450]}")
    history_str = "\n".join(hist_lines) if hist_lines else "(Start of coaching thread)"

    if lang_intent in ("tamil_script", "tamil_requested", "tamil_preferred"):
        lang_rule = (
            "Respond primarily in clear, encouraging Tamil Nadu academic Tamil (தமிழ்), "
            "keeping essential ICAI English statutory terms, Section numbers, Accounting Standards (AS / Ind AS), "
            "and Standards on Auditing (SA) in parentheses so the student can write crisp English answers in the ICAI exam!"
        )
    elif lang_intent == "bilingual":
        lang_rule = (
            "Provide a concise, structured ICAI Working Note / Statutory Provision explanation in English FIRST, "
            "followed by a clear, natural Tamil (தமிழ் விளக்கம்) conceptual takeaway so the student understands 100% in both languages."
        )
    else:
        lang_rule = (
            "Respond in clear, crisp ICAI examiner-style English (citing the exact Section / AS / Ind AS / SA / Working Note steps), "
            "with a brief Tamil conceptual takeaway if helpful."
        )

    student_label = student_name or "Student"
    choice_label = user_choice or "Not selected yet"

    return f"""You are a Senior ICAI Chartered Accountancy (CA) All-India Ranker Faculty & SIRC (Southern India Regional Council, Chennai) Mentor coaching Tamil Nadu students across all 3 CA groups/levels:
- Level 1: CA Foundation (Papers 1–4: Accounting, Business Laws, Quantitative Aptitude with -0.25 negative marking, Business Economics with -0.25 negative marking)
- Level 2: CA Intermediate Group I & Group II (Papers 1–6: Advanced Accounting, Corporate & Other Laws, Direct Tax AY 2026-27 & GST, Cost & Management Accounting, Auditing & Ethics SAs, FM & Strategic Management — 30% compulsory Case-Scenario MCQs + 70% Descriptive)
- Level 3: CA Final Group I & Group II + SPOM Sets A–D (FR Ind AS, AFM, Advanced Auditing, Direct & International Tax, Indirect Tax GST/Customs, IBS Open-Book Multidisciplinary Case Study, IBC 2016 / SEBI / SCMPE)

You are tutoring {student_label} one-on-one.

STRICT COACHING & STYLE RULES:
- Do NOT use emojis anywhere in your response.
- Ground every explanation strictly in ICAI Board of Studies (BoS) Study Material (New Scheme), Companies Act 2013, Income-tax Act 1961 (Finance Act amendments / Sec 115BAC Default Regime), CGST Act 2017, Accounting Standards (AS) / Ind AS, and Standards on Auditing (SAs).
- {lang_rule}
- Directly answer what {student_label} asked in 100-220 words (unless they ask for a full working note or practice case scenario).
- Explicitly highlight ICAI's 40% individual paper minimum, 50% group aggregate rule, 60%+ exemption strategy, or why wrong options are examiner traps.
- Use **bold** for Section numbers, Standards (AS/Ind AS/SA), key statutory terms, and answer letters.

ACTIVE ICAI CA QUESTION CONTEXT (Q#{question_number or q.get('id', '')}):
- Level & Paper/Chapter: {subj} — {chapter} ({statutory_ref})
- Question (English): {stem_en}
- Question (Tamil Summary): {stem_ta}
- Options:
{choices_block}
- Student's Current Selected Option: {choice_label}
- Verified Correct Option: {correct}
- Verified English Solution / Working Note: {exp_en}
- Verified Tamil Explanation: {exp_ta}
- ICAI Examiner Tip / Key Provision: {key_pt}
- Examiner Distractor Traps:
{traps_block}
- Recommended Video Channel: {vid.get('title', '')} ({vid.get('url', '')})

RECENT CONVERSATION:
{history_str}

STUDENT'S QUESTION:
{student_msg}

Write your ICAI CA Coach response now:"""


def call_gemini_rest_api(prompt_str: str, api_key: str):
    """Calls Google Gemini API (gemini-2.5-flash / gemini-2.0-flash) directly via HTTPS."""
    for model_id in ("gemini-2.5-flash", "gemini-2.0-flash"):
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_id}:generateContent?key={urllib.parse.quote(api_key)}"
        )
        req_body = json.dumps(
            {
                "contents": [{"parts": [{"text": prompt_str}]}],
                "generationConfig": {"temperature": 0.35, "maxOutputTokens": 900},
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates") or []
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts") or []
                    text = "".join(p.get("text", "") for p in parts).strip()
                    if text:
                        return text, f"google_gemini_api ({model_id})"
        except Exception as exc:
            print(f"Gemini REST ({model_id}) notice: {exc}", file=sys.stderr)
    return None, None


def call_local_agy_gemini(prompt_str: str):
    """Calls authenticated Google Gemini models via local agy CLI on this laptop."""
    if not os.path.exists(AGY_BIN):
        return None, None
    env = os.environ.copy()
    scratch_dir = "/tmp/ca_gemini_scratch"
    os.makedirs(scratch_dir, exist_ok=True)
    for model_name in ("gemini-3.8-flash-low", "gemini-4-argon-low", "gemini-4-carbon-low"):
        try:
            proc = subprocess.run(
                [
                    AGY_BIN,
                    "--model",
                    model_name,
                    "--mode",
                    "plan",
                    "--disable-slash-commands",
                    f"-p={prompt_str}",
                ],
                cwd=scratch_dir,
                text=True,
                capture_output=True,
                timeout=34,
                env=env,
            )
            if proc.returncode == 0 and proc.stdout and proc.stdout.strip():
                return proc.stdout.strip(), f"gemini_agy ({model_name})"
        except Exception as exc:
            print(f"agy Gemini ({model_name}) notice: {exc}", file=sys.stderr)
    return None, None


def build_offline_bilingual_fallback(q_data: dict, question_number: int, user_choice: str, student_msg: str, lang_intent: str) -> str:
    reload_question_banks()
    q = q_data or {}
    qid = q.get("id")
    if qid and int(qid) in QUESTIONS_BY_ID:
        q = QUESTIONS_BY_ID[int(qid)]

    if not q.get("stem_en"):
        return (
            "**ICAI CA New Scheme Coaching Guide (English & தமிழ்)**\n\n"
            "Master the **3 ICAI Levels**: **CA Foundation** (4 Papers, 400M; `-0.25` negative marking in Papers 3 & 4), "
            "**CA Intermediate** (6 Papers across Group I & II; **30% Case-Scenario MCQs** + **70% Descriptive**), and "
            "**CA Final + SPOM Sets A–D** (6 Papers including Open-Book Paper 6 IBS). Remember ICAI's golden rule: "
            "**40% minimum per paper**, **50% group aggregate**, and **60%+ in any paper earns a 3-attempt Exemption**!\n\n"
            "**தமிழ் குறிப்பு:** சி.ஏ (CA) தேர்வில் ஒவ்வொரு தாளிலும் குறைந்தபட்சம் **40%** மதிப்பெண்ணும், குழு சராசரியாக (Aggregate) **50%** மதிப்பெண்ணும் பெற வேண்டும். "
            "ஏதேனும் ஒரு தாளில் **60%+** பெற்றால் அடுத்த 3 தேர்வுகளுக்கு விலக்கு (Exemption) கிடைக்கும்!"
        )

    corr = q.get("correct", "")
    subj = q.get("subject", "")
    chap = q.get("chapter", "")
    ref = q.get("ncertRef", "")
    exp_en = q.get("explanation_en", "")
    exp_ta = q.get("explanation_ta", "")
    key_pt = q.get("ncert_key_point", "")
    traps = q.get("trap_breakdown") or {}
    lower_msg = (student_msg or "").lower()

    if "trap" in lower_msg or "wrong" in lower_msg or "தவறு" in lower_msg:
        trap_lines = [f"- **Option {k}:** {v}" for k, v in traps.items()]
        return (
            f"**ICAI Examiner Trap Analysis — {subj} ({chap})**\n\n"
            + "\n".join(trap_lines)
            + f"\n\n**Verified Correct Option:** **{corr}**\n"
            + f"**தமிழ் விளக்கம்:** {exp_ta}"
        )

    if lang_intent in ("tamil_script", "tamil_requested", "tamil_preferred"):
        return (
            f"**{subj} — {chap} ({ref})**\n\n"
            f"**தமிழ் விளக்கம்:** {exp_ta}\n\n"
            f"**சரியான விடை:** **விருப்பம் {corr}**\n\n"
            f"**ICAI முக்கிய விதி (Statutory Reference):** {key_pt}"
        )

    choice_note = ""
    if user_choice:
        if user_choice == corr:
            choice_note = f"Your selection **{user_choice}** is **Correct**.\n\n"
        elif user_choice in traps:
            choice_note = f"Your selection **{user_choice}** hits an **ICAI Examiner Trap**: {traps[user_choice]}\n\n"

    return (
        f"**{subj} — {chap}** ({ref})\n\n"
        f"{choice_note}"
        f"**ICAI Working Note & Provision:** {exp_en}\n\n"
        f"**தமிழ் விளக்கம்:** {exp_ta}\n\n"
        f"**Examiner Tip:** {key_pt} | **Correct Option:** **{corr}**"
    )


def generate_gemini_coach_reply(payload: dict, custom_api_key: str = ""):
    student_id = str(payload.get("student_id") or "default_student").strip()
    student_name = str(payload.get("student_name") or "Student").strip()
    q_data = payload.get("question_data") or {}
    q_num = payload.get("question_number") or q_data.get("id") or 1
    user_choice = str(payload.get("user_choice") or "").strip().upper()
    student_msg = str(payload.get("student_message") or "Explain this question step by step with ICAI provision and working note.").strip()
    ui_lang_pref = str(payload.get("language_pref") or "bilingual").strip()
    chat_history = payload.get("chat_history") or []

    lang_intent = detect_language_intent(student_msg, ui_lang_pref)
    prompt_str = build_ca_gemini_prompt(
        q_data=q_data,
        question_number=q_num,
        user_choice=user_choice,
        student_msg=student_msg,
        student_name=student_name,
        lang_intent=lang_intent,
        recent_history=chat_history,
    )

    api_key = (custom_api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    reply_text, engine_used = (None, None)

    if api_key:
        reply_text, engine_used = call_gemini_rest_api(prompt_str, api_key)

    if not reply_text:
        reply_text, engine_used = call_local_agy_gemini(prompt_str)

    if not reply_text:
        reply_text = build_offline_bilingual_fallback(q_data, q_num, user_choice, student_msg, lang_intent)
        engine_used = "icai_bos_bilingual_engine"

    reply_text = re.sub(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", "", reply_text).strip()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    qid_val = int(q_data["id"]) if isinstance(q_data, dict) and str(q_data.get("id", "")).isdigit() else None
    subj_val = q_data.get("subject", "") if isinstance(q_data, dict) else ""

    with DB_LOCK:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO coach_interactions (
                student_id, student_name, question_id, subject, user_choice,
                language_detected, student_message, coach_reply, engine_used, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student_id,
                student_name,
                qid_val,
                subj_val,
                user_choice,
                lang_intent,
                student_msg,
                reply_text,
                engine_used,
                now_str,
            ),
        )
        conn.commit()
        conn.close()

    return {
        "reply": reply_text,
        "engine": engine_used,
        "language_detected": lang_intent,
    }


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class CAMasteryHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[CA-Server] {self.address_string()} - {fmt % args}\n")

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, X-Gemini-Key, X-Access-Code, X-Device-Id, X-Admin-Key",
        )
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, status_code: int, html_str: str):
        body = html_str.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _client_ip(self) -> str:
        return (
            self.headers.get("CF-Connecting-IP")
            or self.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or self.client_address[0]
        )

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            return
        if parsed.path == "/":
            self.path = "/index.html"
        return super().do_HEAD()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/api/public_config":
            cfg = load_admin_secrets()
            enforce_gate = bool(cfg.get("enforce_access_gate", True))
            self._send_json(
                200,
                {
                    "ga_measurement_id": cfg.get("ga_measurement_id") or "G-KGL9DJNFNR",
                    "auth_required": enforce_gate,
                    "daily_ai_limit_per_code": int(cfg.get("daily_ai_limit_per_code") or 40),
                    "max_devices_per_code": int(cfg.get("max_devices_per_code") or 2),
                },
            )
            return

        if path == "/api/auth/check_request":
            req_token = (qs.get("request_token") or [""])[0].strip()
            email_lookup = (qs.get("email") or [""])[0].strip().lower()
            with DB_LOCK:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                row = None
                if req_token:
                    cur.execute(
                        "SELECT request_token, name, email, status, access_code, created_at, approved_at FROM access_requests WHERE request_token = ? LIMIT 1",
                        (req_token,),
                    )
                    row = cur.fetchone()
                elif email_lookup:
                    cur.execute(
                        "SELECT request_token, name, email, status, access_code, created_at, approved_at FROM access_requests WHERE LOWER(email) = ? ORDER BY id DESC LIMIT 1",
                        (email_lookup,),
                    )
                    row = cur.fetchone()
                conn.close()
            if not row:
                self._send_json(404, {"found": False, "status": "not_found"})
                return
            rec = dict(row)
            self._send_json(
                200,
                {
                    "found": True,
                    "status": rec["status"],
                    "name": rec["name"],
                    "email": rec["email"],
                    "request_token": rec["request_token"],
                    "access_code": rec["access_code"] if rec["status"] == "approved" else None,
                    "approved_at": rec["approved_at"],
                },
            )
            return

        if path == "/api/auth/admin_action":
            req_token = (qs.get("token") or [""])[0].strip()
            action = (qs.get("action") or [""])[0].strip().lower()
            sig = (qs.get("sig") or [""])[0].strip()
            if action not in ("approve", "reject", "revoke") or not verify_admin_token(req_token, action, sig):
                self._send_html(
                    403,
                    "<html><body style='font-family:sans-serif;padding:30px;'><h2>403 Invalid or Expired Signature</h2></body></html>",
                )
                return

            cfg = load_admin_secrets()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with DB_LOCK:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("SELECT * FROM access_requests WHERE request_token = ? LIMIT 1", (req_token,))
                row = cur.fetchone()
                if not row:
                    cur.execute("SELECT * FROM access_requests ORDER BY id DESC LIMIT 1")
                    row = cur.fetchone()
                if not row:
                    conn.close()
                    self._send_html(404, "<html><body style='font-family:sans-serif;padding:30px;'><h2>No Access Requests Found</h2></body></html>")
                    return
                rec = dict(row)
                req_token = rec["request_token"]
                code = rec.get("access_code")
                if action == "approve":
                    if not code:
                        code = generate_unique_access_code()
                    cur.execute(
                        "UPDATE access_requests SET status = 'approved', access_code = ?, approved_at = ? WHERE request_token = ?",
                        (code, now_str, req_token),
                    )
                else:
                    new_st = "rejected" if action == "reject" else "revoked"
                    cur.execute(
                        "UPDATE access_requests SET status = ? WHERE request_token = ?",
                        (new_st, req_token),
                    )
                conn.commit()
                conn.close()

            frontend_url = (cfg.get("public_frontend_url") or "https://thameema.github.io/ca-prep").rstrip("/")
            magic_link = f"{frontend_url}/?code={urllib.parse.quote(code or '')}"
            revoke_sig = sign_admin_token(req_token, "revoke")
            approve_sig = sign_admin_token(req_token, "approve")
            api_base = (cfg.get("public_api_url") or "").rstrip("/")
            revoke_url = f"{api_base}/api/auth/admin_action?token={req_token}&action=revoke&sig={revoke_sig}"
            reapprove_url = f"{api_base}/api/auth/admin_action?token={req_token}&action=approve&sig={approve_sig}"
            status_badge = "#047857" if action == "approve" else "#be123c"

            page_html = f"""<!DOCTYPE html>
            <html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
            <title>CA Mastery Hub Admin Action — {action.upper()}</title></head>
            <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#0f172a;color:#f8fafc;padding:24px;margin:0;">
              <div style="max-width:540px;margin:20px auto;background:#ffffff;color:#0f172a;border-radius:14px;padding:24px;box-shadow:0 10px 30px rgba(0,0,0,0.35);">
                <div style="display:inline-block;background:{status_badge};color:#fff;font-size:11px;font-weight:800;padding:4px 10px;border-radius:6px;text-transform:uppercase;">
                  Request {html.escape(action.upper())}D
                </div>
                <h2 style="margin:10px 0 6px 0;font-size:20px;">{html.escape(rec['name'])} ({html.escape(rec['email'])})</h2>
                <p style="font-size:13px;color:#475569;margin:0 0 14px 0;">
                  <strong>District/Branch:</strong> {html.escape(rec.get('district') or 'N/A')} &nbsp;|&nbsp;
                  <strong>CA Level:</strong> {html.escape(rec.get('purpose') or 'N/A')}
                </p>
                {f'''
                <div style="background:#f0fdfa;border:2px solid #0d9488;border-radius:10px;padding:14px;text-align:center;margin-bottom:14px;">
                  <div style="font-size:11px;font-weight:700;color:#0f766e;">GENERATED UNIQUE CA STUDENT CODE</div>
                  <div id="code-box" style="font-size:26px;font-weight:900;font-family:monospace;letter-spacing:2px;margin:6px 0;">{html.escape(code)}</div>
                  <button onclick="navigator.clipboard.writeText('{html.escape(magic_link)}');this.textContent='Copied Magic Sign-In Link!';" style="background:#0f766e;color:#fff;border:none;padding:8px 14px;border-radius:6px;font-weight:700;cursor:pointer;font-size:12px;">Copy 1-Click Magic Link</button>
                </div>
                <div style="margin-top:16px;text-align:right;">
                  <a href="{revoke_url}" style="color:#be123c;font-size:12px;font-weight:700;text-decoration:none;">Revoke This Code &rarr;</a>
                </div>
                ''' if action == "approve" else f'''
                <p style="font-size:13.5px;color:#be123c;font-weight:600;">Access for this request has been {html.escape(action)}d.</p>
                <a href="{reapprove_url}" style="display:inline-block;background:#0f766e;color:#fff;text-decoration:none;padding:9px 16px;border-radius:7px;font-size:13px;font-weight:700;">Re-Approve Instead</a>
                '''}
              </div>
            </body></html>"""
            self._send_html(200, page_html)
            return

        if path == "/api/auth/admin_list":
            cfg = load_admin_secrets()
            provided_key = (
                self.headers.get("X-Admin-Key")
                or (qs.get("admin_key") or [""])[0]
            ).strip()
            expected_key = str(cfg.get("admin_key") or "").strip()
            if not expected_key or not provided_key or not hmac.compare_digest(provided_key, expected_key):
                self._send_json(403, {"error": "Unauthorized admin key"})
                return
            with DB_LOCK:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("SELECT * FROM access_requests ORDER BY id DESC LIMIT 200")
                reqs = [dict(r) for r in cur.fetchall()]
                cur.execute(
                    "SELECT event_name, COUNT(*) AS cnt FROM analytics_events GROUP BY event_name"
                )
                ev_counts = {r["event_name"]: r["cnt"] for r in cur.fetchall()}
                conn.close()
            api_base = (cfg.get("public_api_url") or "").rstrip("/")
            for r in reqs:
                tok = r["request_token"]
                r["approve_url"] = f"{api_base}/api/auth/admin_action?token={tok}&action=approve&sig={sign_admin_token(tok, 'approve')}"
                r["revoke_url"] = f"{api_base}/api/auth/admin_action?token={tok}&action=revoke&sig={sign_admin_token(tok, 'revoke')}"
            self._send_json(200, {"requests": reqs, "analytics_summary": ev_counts})
            return

        if path == "/api/health":
            reload_question_banks()
            has_env_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
            has_agy = os.path.exists(AGY_BIN)
            with DB_LOCK:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM exam_attempts")
                attempts_cnt = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM coach_interactions")
                chats_cnt = cur.fetchone()[0]
                conn.close()
            self._send_json(
                200,
                {
                    "status": "ok",
                    "exam": "Tamil Nadu ICAI CA Mastery Hub (Foundation • Inter • Final • SPOM)",
                    "verified_questions": len(QUESTIONS_BY_ID),
                    "gemini_engine": (
                        "google_gemini_api"
                        if has_env_key
                        else ("gemini_agy_cli" if has_agy else "icai_bos_bilingual_fallback")
                    ),
                    "total_attempts_logged": attempts_cnt,
                    "total_coach_chats_logged": chats_cnt,
                },
            )
            return

        if path == "/api/profile":
            student_id = (qs.get("student_id") or ["default_student"])[0]
            with DB_LOCK:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
                row = cur.fetchone()
                conn.close()
            self._send_json(200, {"profile": dict(row) if row else None})
            return

        if path == "/api/scores":
            student_id = (qs.get("student_id") or [""])[0].strip()
            fetch_all = (qs.get("all") or ["0"])[0] == "1"
            with DB_LOCK:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                if fetch_all or not student_id:
                    cur.execute("SELECT * FROM exam_attempts ORDER BY id DESC LIMIT 100")
                else:
                    cur.execute(
                        "SELECT * FROM exam_attempts WHERE student_id = ? ORDER BY id DESC LIMIT 100",
                        (student_id,),
                    )
                rows = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT COUNT(*) FROM coach_interactions")
                total_chats = cur.fetchone()[0]
                conn.close()

            mistake_set = set()
            subject_rollup = {
                s: {"correct": 0, "wrong": 0, "unanswered": 0, "total": 0}
                for s in CA_SUBJECT_BUCKETS
            }
            for r in rows:
                sb = json.loads(r.pop("subject_breakdown_json", "{}"))
                r["subject_breakdown"] = sb
                r.pop("answers_json", None)
                wids = json.loads(r.pop("wrong_question_ids_json", "[]"))
                r["wrong_question_ids"] = wids
                for wid in wids:
                    mistake_set.add(int(wid))
                for s_name, s_stats in sb.items():
                    if s_name not in subject_rollup:
                        subject_rollup[s_name] = {"correct": 0, "wrong": 0, "unanswered": 0, "total": 0}
                    subject_rollup[s_name]["correct"] += s_stats.get("correct", 0)
                    subject_rollup[s_name]["wrong"] += s_stats.get("wrong", 0)
                    subject_rollup[s_name]["unanswered"] += s_stats.get("unanswered", 0)
                    subject_rollup[s_name]["total"] += s_stats.get("total", 0)

            summary = {
                "total_attempts": len(rows),
                "best_projected_720": max((r["projected_720"] for r in rows), default=0),
                "latest_projected_720": rows[0]["projected_720"] if rows else 0,
                "average_projected_720": round(sum(r["projected_720"] for r in rows) / len(rows), 1) if rows else 0,
                "total_negative_marks_lost": round(sum(r["negative_marks_lost"] for r in rows), 2),
                "total_coach_interactions": total_chats,
                "subject_rollup": subject_rollup,
                "mistake_question_ids": sorted(mistake_set),
            }
            self._send_json(200, {"summary": summary, "attempts": rows})
            return

        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/auth/request_access":
            try:
                client_ip = self._client_ip()
                if not check_ip_rate_limit(client_ip, "req_access", 6, 3600):
                    self._send_json(429, {"error": "Too many access requests from this network. Please wait before trying again."})
                    return

                body = self._read_json_body()
                name = str(body.get("name") or "").strip()[:120]
                email = str(body.get("email") or "").strip().lower()[:160]
                district = str(body.get("district") or "").strip()[:120]
                purpose = str(body.get("purpose") or "CA Aspirant (Foundation / Inter / Final)").strip()[:500]
                ua = (self.headers.get("User-Agent") or "")[:240]

                if not name or not email or "@" not in email:
                    self._send_json(400, {"error": "Please enter your Name and a valid Email Address."})
                    return

                cfg = load_admin_secrets()
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                max_dev = int(cfg.get("max_devices_per_code") or 2)
                daily_lim = int(cfg.get("daily_ai_limit_per_code") or 40)

                is_new_signup = True
                with DB_LOCK:
                    conn = sqlite3.connect(DB_PATH)
                    conn.row_factory = sqlite3.Row
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT * FROM access_requests WHERE LOWER(email) = ? ORDER BY id DESC LIMIT 1",
                        (email,),
                    )
                    existing = cur.fetchone()
                    if existing and existing["status"] in ("revoked", "rejected"):
                        conn.close()
                        self._send_json(403, {"error": "Access for this email has been revoked by the administrator."})
                        return

                    if existing:
                        is_new_signup = False
                        req_token = existing["request_token"]
                        code = existing["access_code"] or generate_unique_access_code()
                        cur.execute(
                            "UPDATE access_requests SET name = ?, district = ?, purpose = ?, status = 'approved', access_code = ?, approved_at = COALESCE(approved_at, ?), ip_address = ?, user_agent = ? WHERE request_token = ?",
                            (name, district, purpose, code, now_str, client_ip, ua, req_token),
                        )
                    else:
                        req_token = secrets.token_hex(16)
                        code = generate_unique_access_code()
                        cur.execute(
                            """
                            INSERT INTO access_requests (
                                request_token, name, email, district, purpose,
                                status, access_code, max_devices, daily_ai_limit,
                                ip_address, user_agent, created_at, approved_at
                            ) VALUES (?, ?, ?, ?, ?, 'approved', ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                req_token,
                                name,
                                email,
                                district,
                                purpose,
                                code,
                                max_dev,
                                daily_lim,
                                client_ip,
                                ua,
                                now_str,
                                now_str,
                            ),
                        )

                    cur.execute(
                        """
                        INSERT INTO analytics_events (
                            event_name, student_id, access_code, page_url, meta_json, ip_address, created_at
                        ) VALUES ('access_requested', ?, ?, '', ?, ?, ?)
                        """,
                        (
                            email,
                            code,
                            json.dumps({"name": name, "district": district, "purpose": purpose[:120]}),
                            client_ip,
                            now_str,
                        ),
                    )
                    conn.commit()
                    conn.close()

                api_base = (cfg.get("public_api_url") or f"http://localhost:{PORT}").rstrip("/")
                frontend_url = (cfg.get("public_frontend_url") or "https://thameema.github.io/ca-prep").rstrip("/")
                admin_console_url = f"{frontend_url}/?admin={urllib.parse.quote(str(cfg.get('admin_key') or ''))}"
                magic_link = f"{frontend_url}/?code={urllib.parse.quote(code)}"
                revoke_sig = sign_admin_token(req_token, "revoke")
                revoke_url = f"{api_base}/api/auth/admin_action?token={req_token}&action=revoke&sig={revoke_sig}"

                def _dispatch_signup_emails():
                    try:
                        stu_subj = f"Your Free Student Pass for Tamil Nadu CA Mastery Hub: {code}"
                        stu_html = f"""
                        <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:560px;margin:0 auto;padding:24px;border:1px solid #e2e8f0;border-radius:12px;background:#ffffff;color:#0f172a;">
                          <div style="background:#0f172a;color:#ffffff;padding:14px 18px;border-radius:8px;margin-bottom:18px;">
                            <strong style="color:#5eead4;font-size:12px;letter-spacing:0.6px;">TAMIL NADU ICAI CA MASTERY HUB</strong>
                            <h2 style="margin:4px 0 0 0;font-size:18px;">Your Student Access Pass is Active!</h2>
                          </div>
                          <p style="font-size:14px;line-height:1.6;">Hello <strong>{html.escape(name)}</strong>,</p>
                          <p style="font-size:14px;line-height:1.6;">Welcome to the <strong>Tamil Nadu CA Mastery Hub (Foundation • Intermediate • Final • SPOM) &amp; Bilingual Gemini AI Coach</strong>. Keep this email to sign in on your phone, tablet, or laptop anytime.</p>
                          <div style="background:#f0fdfa;border:2px dashed #0d9488;border-radius:10px;padding:16px;text-align:center;margin:18px 0;">
                            <div style="font-size:11px;font-weight:700;color:#0f766e;text-transform:uppercase;letter-spacing:0.8px;">Your Personal Access Code</div>
                            <div style="font-size:26px;font-weight:900;color:#0f172a;letter-spacing:2px;margin-top:6px;font-family:monospace;">{html.escape(code)}</div>
                            <div style="font-size:11.5px;color:#475569;margin-top:6px;">Valid for up to {max_dev} personal devices • {daily_lim} AI Coach queries/day</div>
                          </div>
                          <p style="text-align:center;margin:22px 0;">
                            <a href="{magic_link}" style="background:#0f766e;color:#ffffff;text-decoration:none;padding:12px 22px;border-radius:8px;font-weight:700;font-size:14px;display:inline-block;">Open CA Mastery Hub &amp; Auto-Sign In &rarr;</a>
                          </p>
                        </div>
                        """
                        stu_text = (
                            f"Hello {name},\n\n"
                            f"Your Personal Access Code for Tamil Nadu CA Mastery Hub: {code}\n"
                            f"Direct Sign-In Link: {magic_link}\n"
                        )
                        if is_new_signup:
                            send_outbound_email(email, stu_subj, stu_html, stu_text, is_owner_alert=False)

                        owner_email = str(cfg.get("owner_notify_email") or "").strip()
                        if owner_email and is_new_signup:
                            subj = f"[CA Hub New Student Pass] {name} ({district or 'TN'}) — {email} [{code}]"
                            owner_html = f"""
                            <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:560px;margin:0 auto;padding:22px;border:1px solid #cbd5e1;border-radius:12px;background:#ffffff;color:#0f172a;">
                              <div style="background:#0f172a;color:#ffffff;padding:12px 16px;border-radius:8px;margin-bottom:16px;">
                                <strong style="color:#5eead4;font-size:11px;letter-spacing:0.6px;">CA MASTERY HUB GATEKEEPER</strong>
                                <h2 style="margin:4px 0 0 0;font-size:17px;">New CA Student Registered (Auto-Unlocked: {html.escape(code)})</h2>
                              </div>
                              <table style="width:100%;border-collapse:collapse;font-size:13.5px;margin-bottom:18px;">
                                <tr><td style="padding:6px 0;color:#64748b;width:130px;"><strong>Name:</strong></td><td style="padding:6px 0;font-weight:700;">{html.escape(name)}</td></tr>
                                <tr><td style="padding:6px 0;color:#64748b;"><strong>Email:</strong></td><td style="padding:6px 0;">{html.escape(email)}</td></tr>
                                <tr><td style="padding:6px 0;color:#64748b;"><strong>District / SIRC Branch:</strong></td><td style="padding:6px 0;">{html.escape(district or 'Not specified')}</td></tr>
                                <tr><td style="padding:6px 0;color:#64748b;"><strong>CA Level / Group:</strong></td><td style="padding:6px 0;">{html.escape(purpose)}</td></tr>
                                <tr><td style="padding:6px 0;color:#64748b;"><strong>Access Code:</strong></td><td style="padding:6px 0;font-family:monospace;font-weight:800;color:#0f766e;">{html.escape(code)}</td></tr>
                                <tr><td style="padding:6px 0;color:#64748b;"><strong>Signed Up At:</strong></td><td style="padding:6px 0;">{now_str} (IP: {html.escape(client_ip)})</td></tr>
                              </table>
                              <div style="background:#f8fafc;padding:16px;border-radius:10px;border:1px solid #e2e8f0;text-align:center;">
                                <p style="margin:0 0 12px 0;font-size:12.5px;color:#334155;">
                                  This student was granted instant access ({daily_lim} AI queries/day limit). Click below anytime to revoke and log out their devices:
                                </p>
                                <a href="{revoke_url}" style="background:#be123c;color:#ffffff;text-decoration:none;padding:12px 18px;border-radius:8px;font-weight:800;font-size:13.5px;display:inline-block;margin:4px;">
                                  &#128683; 1-Click Revoke / Block User
                                </a>
                              </div>
                              <p style="margin:14px 0 0 0;font-size:12px;text-align:center;">
                                <a href="{admin_console_url}" style="color:#0f766e;font-weight:700;text-decoration:none;">Open Full Gatekeeper Admin Console &rarr;</a>
                              </p>
                            </div>
                            """
                            owner_text = (
                                f"New CA Mastery Hub Student Registered (Code: {code})\n"
                                f"Name: {name}\n"
                                f"Email: {email}\n"
                                f"District/Branch: {district}\n"
                                f"CA Level: {purpose}\n\n"
                                f"1-CLICK REVOKE / BLOCK USER:\n{revoke_url}\n"
                            )
                            send_outbound_email(owner_email, subj, owner_html, owner_text, is_owner_alert=True)
                    except Exception:
                        pass

                threading.Thread(target=_dispatch_signup_emails, daemon=True).start()

                self._send_json(
                    200,
                    {
                        "status": "approved",
                        "access_code": code,
                        "request_token": req_token,
                        "name": name,
                        "district": district,
                        "message": f"Welcome {name}! Your personal CA access code {code} is active.",
                    },
                )
            except Exception as exc:
                self._send_json(400, {"error": str(exc)})
            return

        if path == "/api/auth/verify_code":
            try:
                client_ip = self._client_ip()
                if not check_ip_rate_limit(client_ip, "verify_code", 20, 600):
                    self._send_json(429, {"valid": False, "reason": "Too many code verification attempts. Please wait 10 minutes."})
                    return

                body = self._read_json_body()
                code = str(body.get("code") or "").strip().upper()
                device_id = str(body.get("device_id") or "browser_default").strip()[:80]
                ua = (self.headers.get("User-Agent") or "")[:240]

                res = validate_student_access_code(
                    code,
                    device_id=device_id,
                    ip_addr=client_ip,
                    user_agent=ua,
                    consume_ai_quota=False,
                )
                if res.get("valid"):
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with DB_LOCK:
                        conn = sqlite3.connect(DB_PATH)
                        cur = conn.cursor()
                        cur.execute(
                            """
                            INSERT INTO analytics_events (
                                event_name, student_id, access_code, page_url, meta_json, ip_address, created_at
                            ) VALUES ('code_login_success', ?, ?, '', ?, ?, ?)
                            """,
                            (
                                res.get("email") or res.get("name") or "",
                                code,
                                json.dumps({"device_id": device_id}),
                                client_ip,
                                now_str,
                            ),
                        )
                        conn.commit()
                        conn.close()
                    self._send_json(200, res)
                else:
                    self._send_json(403, res)
            except Exception as exc:
                self._send_json(400, {"valid": False, "reason": str(exc)})
            return

        if path == "/api/analytics/track":
            try:
                client_ip = self._client_ip()
                if not check_ip_rate_limit(client_ip, "analytics", 120, 60):
                    self._send_json(200, {"status": "throttled"})
                    return
                body = self._read_json_body()
                event_name = str(body.get("event_name") or "page_view").strip()[:64]
                student_id = str(body.get("student_id") or "").strip()[:120]
                access_code = str(body.get("access_code") or "").strip().upper()[:32]
                page_url = str(body.get("page_url") or "").strip()[:240]
                meta = body.get("meta") if isinstance(body.get("meta"), dict) else {}
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with DB_LOCK:
                    conn = sqlite3.connect(DB_PATH)
                    cur = conn.cursor()
                    cur.execute(
                        """
                        INSERT INTO analytics_events (
                            event_name, student_id, access_code, page_url, meta_json, ip_address, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            event_name,
                            student_id,
                            access_code,
                            page_url,
                            json.dumps(meta)[:1000],
                            client_ip,
                            now_str,
                        ),
                    )
                    conn.commit()
                    conn.close()
                self._send_json(200, {"status": "logged"})
            except Exception as exc:
                self._send_json(400, {"error": str(exc)})
            return

        if path == "/api/profile":
            try:
                body = self._read_json_body()
                student_id = str(body.get("student_id") or "default_student").strip()
                name = str(body.get("name") or "CA Aspirant").strip()
                district = str(body.get("district") or "Chennai (SIRC HQ)").strip()
                board = str(body.get("board") or "Level 1: CA Foundation").strip()
                quota_category = str(body.get("quota_category") or "ICAI BoS Free Live + TAHDCO / SSP Scholarship").strip()
                language_pref = str(body.get("language_pref") or "bilingual").strip()
                target_score = max(40, min(100, int(body.get("target_score") or 65)))
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with DB_LOCK:
                    conn = sqlite3.connect(DB_PATH)
                    cur = conn.cursor()
                    cur.execute(
                        """
                        INSERT INTO students (
                            student_id, name, district, board, quota_category,
                            language_pref, target_score, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(student_id) DO UPDATE SET
                            name=excluded.name,
                            district=excluded.district,
                            board=excluded.board,
                            quota_category=excluded.quota_category,
                            language_pref=excluded.language_pref,
                            target_score=excluded.target_score,
                            updated_at=excluded.updated_at
                        """,
                        (
                            student_id,
                            name,
                            district,
                            board,
                            quota_category,
                            language_pref,
                            target_score,
                            now_str,
                            now_str,
                        ),
                    )
                    conn.commit()
                    conn.close()
                self._send_json(200, {"status": "saved", "student_id": student_id, "name": name})
            except Exception as exc:
                self._send_json(400, {"error": str(exc)})
            return

        if path == "/api/submit_attempt":
            try:
                body = self._read_json_body()
                graded = grade_exam_submission(body)
                self._send_json(200, graded)
            except Exception as exc:
                self._send_json(400, {"error": str(exc)})
            return

        if path == "/api/chat":
            try:
                client_ip = self._client_ip()
                if not check_ip_rate_limit(client_ip, "ai_chat_ip", 35, 3600):
                    self._send_json(
                        429,
                        {
                            "error": "Hourly AI Coach rate limit reached for this network.",
                            "reply": "**Rate Limit Reached:** Too many AI Coach requests from this network in the last hour. Please pause and review your current solutions before asking more questions.",
                        },
                    )
                    return

                body = self._read_json_body()
                custom_key = self.headers.get("X-Gemini-Key", "").strip()
                access_code = (
                    self.headers.get("X-Access-Code", "").strip()
                    or str(body.get("access_code") or "").strip()
                )
                device_id = (
                    self.headers.get("X-Device-Id", "").strip()
                    or str(body.get("device_id") or "browser_default").strip()
                )
                ua = (self.headers.get("User-Agent") or "")[:240]

                cfg = load_admin_secrets()
                enforce_gate = bool(cfg.get("enforce_access_gate", True))

                if not custom_key and (enforce_gate or access_code):
                    auth_check = validate_student_access_code(
                        access_code,
                        device_id=device_id,
                        ip_addr=client_ip,
                        user_agent=ua,
                        consume_ai_quota=True,
                    )
                    if not auth_check.get("valid") and enforce_gate:
                        self._send_json(
                            403,
                            {
                                "error": auth_check.get("reason", "Valid Access Code required."),
                                "auth_required": True,
                                "reply": f"**Access Code Required:** {auth_check.get('reason', 'Please sign in with your personal student access code to use the live AI Coach.')}",
                            },
                        )
                        return

                result = generate_gemini_coach_reply(body, custom_api_key=custom_key)
                self._send_json(200, result)
            except Exception as exc:
                self._send_json(500, {"error": str(exc)})
            return

        self._send_json(404, {"error": "Endpoint not found"})


if __name__ == "__main__":
    init_db()
    sync_mentor_ledger()
    with ThreadedHTTPServer(("", PORT), CAMasteryHandler) as httpd:
        print(f"Tamil Nadu CA Mastery Hub & Gemini Coach running at http://localhost:{PORT}")
        sys.stdout.flush()
        httpd.serve_forever()
