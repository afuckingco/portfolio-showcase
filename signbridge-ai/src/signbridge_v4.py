"""
╔══════════════════════════════════════════════════════╗
║         SignBridge AI  v4.0  — by SignBridge         ║
║  Real-time BISINDO → Bahasa Indonesia (Claude AI)    ║
╚══════════════════════════════════════════════════════╝

PERBAIKAN v4.2:
  • Path model otomatis mengikuti lokasi script (tidak perlu cd dulu)
  • Fallback otomatis: best_checkpoint.h5 → hand_lstm_model.h5
  • Label encoder otomatis dibuat dari data/raw/ jika .pkl tidak ada
  • Error API ditampilkan di layar (bukan diam-diam gagal)
  • Fallback otomatis: jika API gagal, tampilkan label mentah
  • Model tidak ada → mode demo (label tangan ditampilkan manual)
  • API key dibaca dari env OPENROUTER_API_KEY atau ANTHROPIC_API_KEY
"""

from __future__ import annotations

import os, sys, json, time, math, queue, threading, logging
import urllib.request, urllib.error
from collections import deque, Counter
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np

try:
    import tensorflow as tf
    tf.get_logger().setLevel("ERROR")
    _TF = True
except ImportError:
    _TF = False

try:
    import joblib
    _JL = True
except ImportError:
    _JL = False

try:
    import pyttsx3
    _TTS_LIB = True
except ImportError:
    _TTS_LIB = False

logging.basicConfig(
    level=logging.INFO,
    format="\033[90m%(asctime)s\033[0m \033[1m%(name)s\033[0m %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("SB4")

# ── Direktori dasar: folder tempat script ini berada ─────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CONFIG                                                                   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
@dataclass
class Config:
    # Path model otomatis mengikuti lokasi script ini
    model_path:        str   = str(_SCRIPT_DIR / "models" / "hand_lstm_model.h5")
    encoder_path:      str   = str(_SCRIPT_DIR / "models" / "label_encoder.pkl")
    transcript_path:   str   = str(_SCRIPT_DIR / "signbridge_transcript.txt")
    seq_len:           int   = 30
    conf_thresh:       float = 0.28
    conf_adapt_lr:     float = 0.02
    ema_alpha:         float = 0.55
    vote_win:          int   = 10
    vote_frac:         float = 0.40
    pred_cooldown:     float = 0.90
    dwell_sec:         float = 0.50
    silence_sec:       float = 1.8
    delta_features:    bool  = True
    # ══════════════════════════════════════════════════════════════
    # CARA MENGISI API KEY (pilih salah satu):
    #
    # 1. Isi langsung di sini (paling mudah):
    #    api_key = "sk-or-v1-xxxx"   ← OpenRouter
    #    api_key = "sk-ant-xxxx"     ← Anthropic langsung
    #
    # 2. File .env di folder yang sama:
    #    Buat file bernama ".env", isi dengan:
    #    OPENROUTER_API_KEY=sk-or-v1-xxxx
    #    atau
    #    ANTHROPIC_API_KEY=sk-ant-xxxx
    #
    # 3. Environment variable (terminal):
    #    set OPENROUTER_API_KEY=sk-or-v1-xxxx   (Windows)
    #    export OPENROUTER_API_KEY=sk-or-v1-xxxx (Linux/Mac)
    # ══════════════════════════════════════════════════════════════
    api_key:           str   = ""          # ← isi di sini jika mau hardcode
    use_openrouter:    bool  = True
    model_claude:      str   = "anthropic/claude-sonnet-4-5"
    translate_enabled: bool  = True
    max_buf_labels:    int   = 14
    context_turns:     int   = 4
    tts_enabled:       bool  = True
    tts_rate:          int   = 150
    speak_delay:       float = 0.5
    cam_idx:           int   = 0
    win_title:         str   = "SignBridge AI  v4"
    show_topk:         int   = 3
    target_fps:        int   = 30
    edit_mode_timeout: float = 8.0


def _load_env_file() -> None:
    """Baca file .env di folder yang sama dengan script ini."""
    env_path = _SCRIPT_DIR / ".env"
    if not env_path.exists():
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    log.info("📄 File .env dimuat dari %s", env_path)


def _resolve_api_key() -> None:
    """
    Prioritas key:
      1. Hardcode di CFG.api_key
      2. File .env
      3. Environment variable
      4. Input manual dari terminal saat startup
    Deteksi otomatis apakah OpenRouter (sk-or-) atau Anthropic (sk-ant-).
    """
    _load_env_file()

    # Ambil dari env jika CFG masih kosong
    if not CFG.api_key:
        if os.environ.get("ANTHROPIC_API_KEY"):
            CFG.api_key        = os.environ["ANTHROPIC_API_KEY"]
            CFG.use_openrouter = False
            CFG.model_claude   = "claude-sonnet-4-20250514"
        elif os.environ.get("OPENROUTER_API_KEY"):
            CFG.api_key        = os.environ["OPENROUTER_API_KEY"]
            CFG.use_openrouter = True

    # Deteksi tipe key dari prefix
    if CFG.api_key.startswith("sk-ant-"):
        CFG.use_openrouter = False
        CFG.model_claude   = "claude-sonnet-4-20250514"
    elif CFG.api_key.startswith("sk-or-"):
        CFG.use_openrouter = True
        CFG.model_claude   = "anthropic/claude-sonnet-4-5"

    # Masih kosong → tanya user di terminal
    if not CFG.api_key:
        print("\n" + "═"*55)
        print("  API key tidak ditemukan.")
        print("  Dapatkan key gratis di: https://openrouter.ai")
        print("═"*55)
        try:
            key = input("  Masukkan API key (atau Enter untuk skip): ").strip()
        except (EOFError, KeyboardInterrupt):
            key = ""
        if key:
            CFG.api_key = key
            if key.startswith("sk-ant-"):
                CFG.use_openrouter = False
                CFG.model_claude   = "claude-sonnet-4-20250514"
            else:
                CFG.use_openrouter = True
            # Simpan ke .env supaya tidak perlu input lagi
            env_path = _SCRIPT_DIR / ".env"
            env_var  = "ANTHROPIC_API_KEY" if key.startswith("sk-ant-") else "OPENROUTER_API_KEY"
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"{env_var}={key}\n")
            log.info("✅ Key disimpan ke %s (tidak perlu input lagi)", env_path)
        else:
            log.warning("⚠️  Tidak ada API key — terjemahan dinonaktifkan")

    if CFG.api_key:
        mode = "OpenRouter" if CFG.use_openrouter else "Anthropic"
        log.info("🔑 API key siap  [%s / %s]", mode, CFG.model_claude)


CFG = Config()
_resolve_api_key()


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  PHASE STATE MACHINE                                                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
class Phase(Enum):
    IDLE        = auto()
    COLLECTING  = auto()
    TRANSLATING = auto()
    SPEAKING    = auto()
    COOLDOWN    = auto()
    EDITING     = auto()


@dataclass
class AppState:
    phase:         Phase     = Phase.IDLE
    label_buf:     List[str] = field(default_factory=list)
    translation:   str       = ""
    last_hand_ts:  float     = field(default_factory=time.time)
    phase_ts:      float     = field(default_factory=time.time)
    paused:        bool      = False
    history:       List[Tuple[List[str], str]] = field(default_factory=list)
    vocab_counter: Counter   = field(default_factory=Counter)
    edit_cursor:   int       = 0
    conf_spark:    deque     = field(default_factory=lambda: deque(maxlen=40))
    api_error:     str       = ""

    def set_phase(self, p: Phase) -> None:
        self.phase    = p
        self.phase_ts = time.time()

    def phase_age(self) -> float:
        return time.time() - self.phase_ts

    def add_label(self, lbl: str) -> None:
        if not self.label_buf or self.label_buf[-1] != lbl:
            self.label_buf.append(lbl)
            self.vocab_counter[lbl] += 1
            if len(self.label_buf) > CFG.max_buf_labels:
                self.label_buf.pop(0)
            self.translation = ""
            self.api_error   = ""

    def add_to_history(self, labels: List[str], translation: str) -> None:
        self.history.append((list(labels), translation))
        if len(self.history) > 20:
            self.history.pop(0)

    def export_transcript(self) -> None:
        if not self.history:
            return
        with open(CFG.transcript_path, "a", encoding="utf-8") as f:
            f.write(f"\n=== Session {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            for labels, tr in self.history:
                f.write(f"  [{', '.join(labels)}]  →  {tr}\n")
        log.info("💾 Transkrip disimpan ke %s", CFG.transcript_path)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  GESTURE PREDICTOR                                                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
@dataclass
class Pred:
    label: str
    conf:  float
    topk:  List[Tuple[str, float]]


def _build_encoder_from_data() -> Optional[object]:
    """
    Buat LabelEncoder secara otomatis dari folder data/raw/
    jika file label_encoder.pkl tidak ditemukan.
    """
    if not _JL:
        return None
    data_dir = _SCRIPT_DIR / "data" / "raw"
    if not data_dir.exists():
        return None
    try:
        from sklearn.preprocessing import LabelEncoder
        gestures = sorted([d.name for d in data_dir.iterdir() if d.is_dir()])
        if not gestures:
            return None
        le = LabelEncoder()
        le.fit(gestures)
        # Simpan supaya tidak perlu dibuat ulang
        enc_path = Path(CFG.encoder_path)
        enc_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(le, str(enc_path))
        log.info("✅ Label encoder dibuat otomatis dari data/raw/ → %d gesture: %s",
                 len(gestures), gestures)
        return le
    except Exception as exc:
        log.warning("⚠️  Gagal membuat encoder otomatis: %s", exc)
        return None


class GesturePredictor:
    def __init__(self) -> None:
        self._seq:             deque                   = deque(maxlen=CFG.seq_len)
        self._votes:           deque                   = deque(maxlen=CFG.vote_win)
        self._last:            Tuple[str, float]       = ("", 0.0)
        self._ema_prob:        Optional[np.ndarray]    = None
        self._raw_topk:        List[Tuple[str, float]] = []
        self._dwell_lbl:       str                     = ""
        self._dwell_start:     float                   = 0.0
        self._adaptive_thresh: float                   = CFG.conf_thresh
        self._prev_kp:         Optional[np.ndarray]    = None
        self.model:            Optional[object]        = None
        self.classes:          List[str]               = []
        self._load()

    def _load(self) -> None:
        if not _TF:
            log.warning("⚠️  TensorFlow tidak tersedia — model dilewati")
            return

        model_path   = Path(CFG.model_path)
        encoder_path = Path(CFG.encoder_path)
        checkpoint   = _SCRIPT_DIR / "models" / "best_checkpoint.h5"

        # ── 1. Tentukan file model yang akan dipakai ──────────────────────
        if model_path.exists():
            chosen_model = model_path
            log.info("📂 Menggunakan model: %s", chosen_model)
        elif checkpoint.exists():
            chosen_model = checkpoint
            log.warning("⚠️  hand_lstm_model.h5 tidak ditemukan")
            log.warning("   Menggunakan fallback: %s", checkpoint)
        else:
            log.error("❌ Tidak ada file model ditemukan di: %s", model_path.parent)
            log.error("   Jalankan train_model.py untuk membuat model")
            return

        # ── 2. Load model ─────────────────────────────────────────────────
        try:
            self.model = tf.keras.models.load_model(str(chosen_model))
            log.info("✅ Model loaded: input=%s", self.model.input_shape)
        except Exception as exc:
            log.error("❌ Gagal load model %s: %s", chosen_model.name, exc)
            self.model = None
            return

        # ── 3. Load atau buat label encoder ──────────────────────────────
        le = None
        if encoder_path.exists() and _JL:
            try:
                le = joblib.load(str(encoder_path))
                log.info("✅ Encoder loaded: %d kelas → %s", len(le.classes_), list(le.classes_[:4]))
            except Exception as exc:
                log.warning("⚠️  Gagal load encoder: %s — mencoba buat otomatis", exc)
                le = None

        if le is None:
            log.warning("⚠️  label_encoder.pkl tidak ditemukan — mencoba buat dari data/raw/")
            le = _build_encoder_from_data()

        if le is None:
            log.error("❌ Encoder tidak bisa dibuat. Jalankan train_model.py.")
            self.model = None
            return

        # Validasi jumlah kelas vs output model
        n_model_out = self.model.output_shape[-1]
        if len(le.classes_) != n_model_out:
            log.error("❌ Jumlah kelas encoder (%d) tidak cocok dengan output model (%d)",
                      len(le.classes_), n_model_out)
            log.error("   Jalankan train_model.py ulang dengan data yang sama")
            self.model = None
            return

        self.classes = list(le.classes_)
        log.info("✅ Siap — %d gesture: %s", len(self.classes), self.classes)

    @property
    def model_loaded(self) -> bool:
        return self.model is not None

    def push(self, kp: np.ndarray) -> Optional[Pred]:
        if CFG.delta_features:
            delta = (kp - self._prev_kp) if self._prev_kp is not None else np.zeros_like(kp)
            self._prev_kp = kp.copy()
            feat = np.concatenate([kp, delta])
        else:
            feat = kp

        self._seq.append(feat)

        if self.model is None or len(self._seq) < CFG.seq_len:
            return None

        raw = self.model.predict(np.expand_dims(np.array(self._seq), 0), verbose=0)[0]

        if self._ema_prob is None:
            self._ema_prob = raw.copy()
        else:
            self._ema_prob = CFG.ema_alpha * raw + (1 - CFG.ema_alpha) * self._ema_prob

        smoothed = self._ema_prob
        top_idx  = np.argsort(smoothed)[-CFG.show_topk:][::-1]
        topk     = [(self.classes[i], float(smoothed[i])) for i in top_idx]
        self._raw_topk = topk

        best_lbl, best_p = topk[0]

        if best_p >= self._adaptive_thresh:
            self._adaptive_thresh = min(self._adaptive_thresh + CFG.conf_adapt_lr * 0.5, 0.70)
        else:
            self._adaptive_thresh = max(self._adaptive_thresh - CFG.conf_adapt_lr, CFG.conf_thresh)

        if best_p < self._adaptive_thresh:
            self._votes.clear()
            return None

        self._votes.append(best_lbl)
        filled = len(self._votes)
        maj_lbl, maj_n = Counter(self._votes).most_common(1)[0]
        if maj_n / filled < CFG.vote_frac:
            return None

        now = time.time()
        if maj_lbl != self._dwell_lbl:
            self._dwell_lbl   = maj_lbl
            self._dwell_start = now
        if (now - self._dwell_start) < CFG.dwell_sec:
            return None

        if maj_lbl == self._last[0] and (now - self._last[1]) < CFG.pred_cooldown:
            return None

        self._last = (maj_lbl, now)
        return Pred(label=maj_lbl, conf=best_p, topk=topk)

    @property
    def raw_topk(self) -> List[Tuple[str, float]]:
        return self._raw_topk

    @property
    def adaptive_thresh(self) -> float:
        return self._adaptive_thresh

    def reset(self) -> None:
        self._seq.clear()
        self._votes.clear()
        self._ema_prob    = None
        self._raw_topk    = []
        self._dwell_lbl   = ""
        self._dwell_start = 0.0
        self._prev_kp     = None


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  CLAUDE TRANSLATOR  — mendukung Anthropic API & OpenRouter               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
class ClaudeTranslator:
    SYSTEM = (
        "Kamu adalah sistem AI yang mengubah label gesture bahasa isyarat "
        "Indonesia (BISINDO) menjadi kalimat bahasa Indonesia yang natural.\n\n"
        "Aturan ketat:\n"
        "• Balas HANYA dengan kalimat hasil — tidak ada penjelasan, tidak ada tanda kutip.\n"
        "• Label kata/frasa: susun menjadi kalimat logis, perbaiki tata bahasa.\n"
        "• Gunakan konteks percakapan sebelumnya untuk inferensi yang lebih baik.\n"
        "• Jika terlalu ambigu, kembalikan label apa adanya dipisah spasi.\n"
        "• Maksimal 1 kalimat. Singkat dan jelas."
    )

    def __init__(self) -> None:
        self._key      = CFG.api_key
        self._lock     = threading.Lock()
        self._result   = ""
        self._pending  = False
        self._last_error: str = ""
        self._history: List[dict] = []
        self._q: queue.Queue = queue.Queue(maxsize=2)
        threading.Thread(target=self._worker, daemon=True, name="claude-worker").start()

        if self._key:
            mode = "OpenRouter" if CFG.use_openrouter else "Anthropic"
            log.info("✅ Claude Translator siap  [%s / %s]", mode, CFG.model_claude)
        else:
            log.warning("⚠️  API key tidak diset — terjemahan dinonaktifkan")
            log.warning("   Set env: OPENROUTER_API_KEY=sk-or-...  atau  ANTHROPIC_API_KEY=sk-ant-...")

    @property
    def ready(self) -> bool:
        return bool(self._key) and CFG.translate_enabled

    @property
    def pending(self) -> bool:
        return self._pending

    @property
    def result(self) -> str:
        with self._lock:
            return self._result

    @property
    def last_error(self) -> str:
        return self._last_error

    def translate(self, labels: List[str], on_done: Optional[Callable] = None) -> None:
        if not self.ready or not labels:
            return
        try:
            self._q.put_nowait((list(labels), on_done))
            self._pending = True
        except queue.Full:
            log.debug("Antrian terjemahan penuh — permintaan dibuang")

    def add_history(self, labels: List[str], translation: str) -> None:
        self._history.append({"role": "user",      "content": "Label: " + ", ".join(labels)})
        self._history.append({"role": "assistant", "content": translation})
        max_msgs = CFG.context_turns * 2
        if len(self._history) > max_msgs:
            self._history = self._history[-max_msgs:]

    def clear_history(self) -> None:
        self._history.clear()

    def clear_result(self) -> None:
        with self._lock:
            self._result = ""
        self._last_error = ""

    def _worker(self) -> None:
        while True:
            labels, callback = self._q.get()
            try:
                text = self._call_api(labels)
                with self._lock:
                    self._result = text
                self._last_error = ""
                log.info("🌐 %s  →  \"%s\"", labels, text)
                if callback:
                    callback(text)
            except urllib.error.HTTPError as exc:
                try:
                    body    = exc.read().decode("utf-8", errors="replace")
                    err_data = json.loads(body)
                    api_msg  = err_data.get("error", {}).get("message", body[:80])
                except Exception:
                    api_msg = f"HTTP {exc.code}"
                self._last_error = f"API Error {exc.code}: {api_msg[:60]}"
                log.error("❌ %s", self._last_error)
                fallback = " ".join(labels)
                with self._lock:
                    self._result = fallback
                if callback:
                    callback(fallback)
            except urllib.error.URLError as exc:
                self._last_error = f"Jaringan: {str(exc.reason)[:60]}"
                log.error("❌ %s", self._last_error)
                fallback = " ".join(labels)
                with self._lock:
                    self._result = fallback
                if callback:
                    callback(fallback)
            except Exception as exc:
                self._last_error = f"Error: {str(exc)[:60]}"
                log.error("❌ Translator error: %s", exc)
                fallback = " ".join(labels)
                with self._lock:
                    self._result = fallback
                if callback:
                    callback(fallback)
            finally:
                self._pending = False
                self._q.task_done()

    def _call_api(self, labels: List[str]) -> str:
        messages = list(self._history) + [{
            "role":    "user",
            "content": "Label gesture: " + ", ".join(labels),
        }]

        if CFG.use_openrouter:
            # ── OpenRouter (sk-or-...) ────────────────────────────────────
            payload = json.dumps({
                "model":      CFG.model_claude,
                "max_tokens": 120,
                "messages":   [{"role": "system", "content": self.SYSTEM}] + messages,
            }).encode()
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=payload, method="POST",
                headers={
                    "Content-Type":  "application/json",
                    "Authorization": f"Bearer {self._key}",
                    "HTTP-Referer":  "https://signbridge.ai",
                    "X-Title":       "SignBridge AI",
                },
            )
            with urllib.request.urlopen(req, timeout=12) as r:
                data = json.loads(r.read())
            return data["choices"][0]["message"]["content"].strip()

        else:
            # ── Anthropic langsung (sk-ant-...) ───────────────────────────
            payload = json.dumps({
                "model":      CFG.model_claude,
                "max_tokens": 120,
                "system":     self.SYSTEM,
                "messages":   messages,
            }).encode()
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload, method="POST",
                headers={
                    "Content-Type":      "application/json",
                    "x-api-key":         self._key,
                    "anthropic-version": "2023-06-01",
                },
            )
            with urllib.request.urlopen(req, timeout=12) as r:
                data = json.loads(r.read())
            return data["content"][0]["text"].strip()


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  TTS ENGINE                                                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
class TTSEngine:
    def __init__(self) -> None:
        self._ready = False
        self._q: queue.Queue = queue.Queue()
        if not (CFG.tts_enabled and _TTS_LIB):
            if CFG.tts_enabled and not _TTS_LIB:
                log.warning("⚠️  pyttsx3 tidak terinstall — TTS dinonaktifkan")
            return
        threading.Thread(target=self._worker, daemon=True, name="tts").start()
        self._ready = True
        log.info("✅ TTS siap (%d wpm)", CFG.tts_rate)

    @property
    def ready(self) -> bool:
        return self._ready

    def speak(self, text: str) -> None:
        if self._ready and text.strip():
            self._q.put(text)

    def _worker(self) -> None:
        while True:
            text = self._q.get()
            try:
                eng = pyttsx3.init()
                eng.setProperty("rate", CFG.tts_rate)
                eng.say(text)
                eng.runAndWait()
                eng.stop()
            except Exception as exc:
                log.debug("TTS error: %s", exc)
            finally:
                self._q.task_done()


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  KEYPOINT EXTRACTOR                                                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
def extract_kp(result) -> np.ndarray:
    L = np.zeros(63, dtype=np.float32)
    R = np.zeros(63, dtype=np.float32)
    if result.multi_hand_landmarks:
        for lm, hd in zip(result.multi_hand_landmarks, result.multi_handedness):
            pts = np.array([[p.x, p.y, p.z] for p in lm.landmark], dtype=np.float32).flatten()
            if hd.classification[0].label == "Left":
                L = pts
            else:
                R = pts
    return np.concatenate([L, R])


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  HUD RENDERER                                                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
class ModernHUD:
    ACCENT  = (255, 160,  40)
    GREEN   = ( 80, 220,  80)
    RED     = ( 60,  60, 220)
    YELLOW  = ( 40, 200, 220)
    GRAY    = (130, 130, 140)
    WHITE   = (240, 240, 248)
    TRANS_C = ( 60, 200, 255)
    EDIT_C  = (100, 255, 180)
    ERR_C   = ( 80, 100, 255)

    PHASE_COLORS = {
        Phase.IDLE:        (100, 100, 110),
        Phase.COLLECTING:  ( 50, 180, 255),
        Phase.TRANSLATING: (255, 180,  40),
        Phase.SPEAKING:    ( 80, 220,  80),
        Phase.COOLDOWN:    (100, 100, 110),
        Phase.EDITING:     (100, 255, 180),
    }
    PHASE_LABELS = {
        Phase.IDLE:        "SIAP",
        Phase.COLLECTING:  "MEREKAM",
        Phase.TRANSLATING: "MENERJEMAHKAN",
        Phase.SPEAKING:    "BERBICARA",
        Phase.COOLDOWN:    "JEDA",
        Phase.EDITING:     "EDIT",
    }

    def __init__(self) -> None:
        self._dot_phase = 0.0

    def _glass(self, img, x, y, w, h, alpha=0.72):
        fh, fw = img.shape[:2]
        x1, y1 = max(0, x),    max(0, y)
        x2, y2 = min(fw, x+w), min(fh, y+h)
        if x2 <= x1 or y2 <= y1:
            return
        roi = img[y1:y2, x1:x2]
        cv2.addWeighted(np.full_like(roi, [14, 14, 20]), alpha, roi, 1-alpha, 0, roi)
        img[y1:y2, x1:x2] = roi
        cv2.rectangle(img, (x1, y1), (x2-1, y2-1), (40, 40, 60), 1)

    def _text(self, img, txt, x, y, scale=0.6, color=None, bold=False):
        color = color or self.WHITE
        th = 2 if bold else 1
        cv2.putText(img, txt, (x+1, y+1), cv2.FONT_HERSHEY_SIMPLEX, scale, (0,0,0), th+1, cv2.LINE_AA)
        cv2.putText(img, txt, (x,   y  ), cv2.FONT_HERSHEY_SIMPLEX, scale, color,   th,   cv2.LINE_AA)

    def _bar(self, img, x, y, w, h, frac, color):
        cv2.rectangle(img, (x, y), (x+w, y+h), (40, 40, 55), -1)
        filled = int(w * max(0.0, min(1.0, frac)))
        if filled:
            cv2.rectangle(img, (x, y), (x+filled, y+h), color, -1)
        cv2.rectangle(img, (x, y), (x+w, y+h), (60, 60, 80), 1)

    def _dots(self) -> str:
        self._dot_phase = (self._dot_phase + 0.12) % 3
        n = int(self._dot_phase) + 1
        return "*" * n + "." * (3 - n)

    def _wrap(self, text: str, max_w: int, scale: float) -> List[str]:
        words, lines, cur = text.split(), [], ""
        for w in words:
            test = (cur + " " + w).strip()
            tw, _ = cv2.getTextSize(test, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)[0]
            if tw > max_w and cur:
                lines.append(cur); cur = w
            else:
                cur = test
        if cur:
            lines.append(cur)
        return lines or [""]

    def _sparkline(self, img, confs, x, y, w, h):
        if len(confs) < 2:
            return
        vals = list(confs)
        step = w / (len(vals) - 1)
        pts  = [(int(x + i*step), int(y + h - v*h)) for i, v in enumerate(vals)]
        for i in range(len(pts)-1):
            a   = i / len(pts)
            col = tuple(int(self.ACCENT[c]*a + self.GRAY[c]*(1-a)) for c in range(3))
            cv2.line(img, pts[i], pts[i+1], col, 1, cv2.LINE_AA)
        ty = int(y + h - CFG.conf_thresh * h)
        cv2.line(img, (x, ty), (x+w, ty), self.RED, 1)

    def draw(self, frame: np.ndarray, state: AppState,
             topk: List[Tuple[str, float]], fps: float,
             adapt_thresh: float, tts_ok: bool, api_ok: bool,
             model_ok: bool = True, api_error: str = "") -> None:

        fh, fw = frame.shape[:2]
        now    = time.time()

        # Phase strip
        pc    = self.PHASE_COLORS[state.phase]
        pulse = 0.55 + 0.45 * math.sin(now * 4.0)
        bc    = tuple(int(c * pulse) for c in pc) \
                if state.phase in (Phase.TRANSLATING, Phase.COLLECTING, Phase.EDITING) else pc
        cv2.rectangle(frame, (0, 0), (fw, 3), bc, -1)

        # Top bar — label chips
        self._glass(frame, 0, 3, fw, 44, alpha=0.80)
        self._text(frame, self.PHASE_LABELS[state.phase], 10, 26, scale=0.48, color=pc, bold=True)

        chip_x = 120
        for i, lbl in enumerate(state.label_buf[-9:]):
            is_cur = (state.phase == Phase.EDITING and
                      i == state.edit_cursor % max(len(state.label_buf), 1))
            tw, th = cv2.getTextSize(lbl, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)[0]
            px, py = chip_x, 10
            cv2.rectangle(frame, (px-4, py), (px+tw+4, py+th+6),
                          (50, 80, 60) if is_cur else (40, 40, 60), -1)
            cv2.rectangle(frame, (px-4, py), (px+tw+4, py+th+6),
                          self.EDIT_C if is_cur else (70, 70, 100), 1)
            col = self.EDIT_C if is_cur else (
                  self.ACCENT if i == len(state.label_buf)-1 else self.GRAY)
            self._text(frame, lbl, px, py+th+1, scale=0.48, color=col)
            chip_x += tw + 14
            if chip_x > fw - 200:
                break

        # Main translation panel
        main_y, panel_h = 52, 90
        self._glass(frame, 0, main_y, fw, panel_h, alpha=0.85)

        if state.phase == Phase.EDITING:
            self._text(frame, "MODE EDIT - A/D pindah  |  Del hapus kata  |  Enter konfirmasi",
                       16, main_y+28, scale=0.44, color=self.EDIT_C)
            cur_lbl = state.label_buf[state.edit_cursor] if state.label_buf else "-"
            self._text(frame, f"Kata dipilih:  {cur_lbl}",
                       16, main_y+58, scale=0.65, color=self.WHITE, bold=True)

        elif state.phase == Phase.TRANSLATING:
            self._text(frame, f"Menerjemahkan  {self._dots()}",
                       16, main_y+34, scale=0.75, color=self.ACCENT, bold=True)
            self._text(frame, " > ".join(state.label_buf[-6:]),
                       16, main_y+62, scale=0.50, color=self.GRAY)

        elif api_error:
            self._text(frame, "Terjemahan gagal:", 16, main_y+28, scale=0.48, color=self.ERR_C)
            short_err = api_error[:70]
            self._text(frame, short_err, 16, main_y+54, scale=0.42, color=self.ERR_C)

        elif state.translation:
            for li, line in enumerate(self._wrap(state.translation, fw-32, 0.85)[:2]):
                self._text(frame, line, 16, main_y+36+li*30,
                           scale=0.85, color=self.TRANS_C, bold=True)

        elif not model_ok and state.phase == Phase.COLLECTING:
            self._text(frame, "Model LSTM tidak ditemukan — mode demo",
                       16, main_y+28, scale=0.48, color=self.YELLOW)
            self._text(frame, "Tekan T untuk terjemah manual  |  pastikan folder models/ ada",
                       16, main_y+54, scale=0.38, color=self.GRAY)

        elif state.label_buf:
            for li, line in enumerate(self._wrap(" | ".join(state.label_buf), fw-32, 0.72)[:2]):
                self._text(frame, line, 16, main_y+36+li*28, scale=0.72)

        else:
            self._text(frame, "Tunjukkan isyarat tangan ke kamera...",
                       16, main_y+40, scale=0.65, color=self.GRAY)

        # History strip
        if state.history:
            hx = fw - 235
            self._glass(frame, hx, main_y, 235, panel_h, alpha=0.65)
            self._text(frame, "Riwayat", hx+8, main_y+16, scale=0.38, color=self.GRAY)
            for hi, (_, tr) in enumerate(reversed(state.history[-3:])):
                fade  = 1.0 - hi * 0.35
                col   = tuple(int(c * fade) for c in self.WHITE)
                short = (tr[:30] + "...") if len(tr) > 30 else tr
                self._text(frame, short, hx+8, main_y+30+hi*22, scale=0.42, color=col)

        # Top-K panel
        if topk:
            tk_h = len(topk)*38 + 46
            tk_y = fh - tk_h - 4
            self._glass(frame, 0, tk_y, 285, tk_h, alpha=0.80)
            self._text(frame, "KANDIDAT GESTURE", 10, tk_y+14, scale=0.38, color=self.GRAY)
            for i, (lbl, prob) in enumerate(topk):
                ry   = tk_y + 20 + i*38
                best = (i == 0 and prob >= adapt_thresh)
                self._bar(frame, 8, ry+4, 260, 18, prob,
                          self.ACCENT if best else (60, 60, 80))
                tw2, _ = cv2.getTextSize(f"{prob:.0%}", cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)[0]
                self._text(frame, lbl, 12, ry+17, scale=0.52,
                           color=self.WHITE if best else self.GRAY, bold=best)
                self._text(frame, f"{prob:.0%}", 268-tw2, ry+17, scale=0.48,
                           color=self.ACCENT if best else self.GRAY)
            self._text(frame, f"thresh {adapt_thresh:.2f}", 10, tk_y+tk_h-10,
                       scale=0.36, color=self.GRAY)
            if state.conf_spark:
                self._sparkline(frame, state.conf_spark, 8, tk_y+tk_h-34, 265, 26)

        # Vocab panel
        if state.vocab_counter:
            top_vocab = state.vocab_counter.most_common(4)
            vw, vh = 220, len(top_vocab)*18 + 24
            vx, vy = (fw - vw) // 2, fh - vh - 26
            self._glass(frame, vx, vy, vw, vh, alpha=0.70)
            self._text(frame, "VOCAB SESI", vx+8, vy+14, scale=0.36, color=self.GRAY)
            max_cnt = state.vocab_counter.most_common(1)[0][1]
            for vi, (word, cnt) in enumerate(top_vocab):
                self._bar(frame, vx+8, vy+18+vi*18, 120, 10, cnt/max_cnt, (60, 120, 80))
                self._text(frame, f"{word}  x{cnt}", vx+8, vy+28+vi*18,
                           scale=0.36, color=self.WHITE)

        # Status bar
        sb_w, sb_h = 165, 130
        self._glass(frame, fw-sb_w-4, fh-sb_h-4, sb_w, sb_h, alpha=0.80)
        sx = fw - sb_w + 4

        fps_col = self.GREEN if fps > 25 else (self.ACCENT if fps > 15 else self.RED)
        self._bar(frame, sx, fh-sb_h, 150, 4, min(fps/60, 1.0), fps_col)
        self._text(frame, f"FPS  {fps:4.1f}", sx, fh-sb_h+18, scale=0.50, color=fps_col)

        live_col = self.GREEN if not state.paused else self.RED
        self._text(frame, f"{'[*]' if not state.paused else '[ ]'} {'LIVE' if not state.paused else 'JEDA'}",
                   sx, fh-sb_h+38, scale=0.50, color=live_col)

        self._text(frame, f"TTS   {'ON'  if tts_ok   else 'OFF'}",
                   sx, fh-sb_h+58, scale=0.50, color=self.GREEN if tts_ok else self.GRAY)

        if not api_ok:
            api_label, api_col = "NO KEY", self.RED
        elif api_error:
            api_label, api_col = "ERR",    self.ERR_C
        else:
            api_label, api_col = "OK",     self.GREEN
        self._text(frame, f"API   {api_label}",
                   sx, fh-sb_h+78, scale=0.50, color=api_col)

        mdl_col = self.GREEN if model_ok else self.YELLOW
        self._text(frame, f"MDL   {'OK' if model_ok else 'MISSING'}",
                   sx, fh-sb_h+98, scale=0.50, color=mdl_col)

        self._text(frame, f"THR   {adapt_thresh:.2f}",
                   sx, fh-sb_h+118, scale=0.42, color=self.GRAY)

        # Silence countdown ring
        if state.phase == Phase.COLLECTING and state.label_buf:
            elapsed = now - state.last_hand_ts
            frac    = min(elapsed / CFG.silence_sec, 1.0)
            cx, cy  = fw // 2, fh - 42
            r = 18
            cv2.circle(frame, (cx, cy), r, (40, 40, 60), -1)
            cv2.circle(frame, (cx, cy), r, (60, 60, 80),  2)
            for a in range(0, int(360*frac), 3):
                ra = math.radians(a - 90)
                cv2.circle(frame, (int(cx + r*math.cos(ra)),
                                   int(cy + r*math.sin(ra))), 2, self.ACCENT, -1)
            self._text(frame, f"{max(0.0, CFG.silence_sec-elapsed):.1f}s",
                       cx-14, cy+6, scale=0.44)

        # Shortcut legend
        keys = "[Q]Keluar [C]Hapus [S]Ucapkan [T]Terjemah [P]Jeda [E]Edit [W]Simpan"
        tw3, _ = cv2.getTextSize(keys, cv2.FONT_HERSHEY_SIMPLEX, 0.34, 1)[0]
        kx = (fw - tw3) // 2
        self._glass(frame, kx-6, fh-22, tw3+12, 20, alpha=0.70)
        self._text(frame, keys, kx, fh-8, scale=0.34, color=self.GRAY)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  MAIN                                                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
def main() -> None:
    predictor  = GesturePredictor()
    translator = ClaudeTranslator()
    tts        = TTSEngine()
    hud        = ModernHUD()
    state      = AppState()

    mp_h   = mp.solutions.hands
    mp_drw = mp.solutions.drawing_utils
    hands  = mp_h.Hands(
        static_image_mode=False,
        min_detection_confidence=0.55,
        min_tracking_confidence=0.55,
        max_num_hands=2,
    )

    cap = cv2.VideoCapture(CFG.cam_idx)
    if not cap.isOpened():
        log.error("Kamera %d tidak bisa dibuka", CFG.cam_idx)
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)

    log.info("═══ SignBridge AI v4 started ═══")
    log.info("Direktori : %s", _SCRIPT_DIR)
    log.info("Model     : %s", CFG.model_path)
    log.info("Encoder   : %s", CFG.encoder_path)
    log.info("API       : %s", "siap ✅" if translator.ready else "tidak ada key ⚠️")
    log.info("Model ML  : %s", "siap ✅" if predictor.model_loaded else "tidak ditemukan ⚠️")
    log.info("Kontrol   : Q=keluar  C=hapus  S=ucapkan  T=terjemah  P=jeda  E=edit  W=simpan")

    fps_q        = deque(maxlen=30)
    t_prev       = time.time()
    frame_budget = 1.0 / CFG.target_fps

    def on_translated(text: str) -> None:
        state.translation = text
        state.api_error   = translator.last_error
        state.add_to_history(state.label_buf, text)
        translator.add_history(state.label_buf, text)
        state.set_phase(Phase.SPEAKING)
        def _speak():
            time.sleep(CFG.speak_delay)
            tts.speak(text)
        threading.Thread(target=_speak, daemon=True).start()

    while cap.isOpened():
        loop_start = time.time()
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.02)
            continue

        now    = time.time()
        dt     = now - t_prev
        t_prev = now
        fps_q.append(1.0 / max(dt, 1e-6))
        fps = float(np.mean(fps_q))

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = hands.process(rgb)
        rgb.flags.writeable = True

        hand_visible = bool(result.multi_hand_landmarks)
        if hand_visible:
            state.last_hand_ts = now
            for hl in result.multi_hand_landmarks:
                mp_drw.draw_landmarks(
                    frame, hl, mp_h.HAND_CONNECTIONS,
                    mp_drw.DrawingSpec((100, 230, 100), 2, 4),
                    mp_drw.DrawingSpec((200, 200, 200), 1),
                )

        if not state.paused and state.phase != Phase.EDITING:
            silence = now - state.last_hand_ts

            if state.phase == Phase.IDLE:
                if hand_visible:
                    state.set_phase(Phase.COLLECTING)

            elif state.phase == Phase.COLLECTING:
                kp   = extract_kp(result)
                pred = predictor.push(kp)
                if pred:
                    state.add_label(pred.label)
                    state.conf_spark.append(pred.conf)
                    log.info("✋ %s  (%.0f%%)", pred.label, pred.conf * 100)

                if silence >= CFG.silence_sec and state.label_buf:
                    state.set_phase(Phase.TRANSLATING)
                    if translator.ready:
                        translator.translate(list(state.label_buf), on_done=on_translated)
                    else:
                        state.translation = " ".join(state.label_buf)
                        state.set_phase(Phase.SPEAKING)
                elif not hand_visible and silence > 5.0 and not state.label_buf:
                    state.set_phase(Phase.IDLE)

            elif state.phase == Phase.TRANSLATING:
                if state.phase_age() > 20.0:
                    log.warning("⏱  Terjemahan timeout — menampilkan label mentah")
                    state.translation = " ".join(state.label_buf)
                    state.api_error   = "Timeout (>20 detik) — cek koneksi internet"
                    state.set_phase(Phase.SPEAKING)

            elif state.phase == Phase.SPEAKING:
                if state.phase_age() > 3.5:
                    state.set_phase(Phase.COOLDOWN)

            elif state.phase == Phase.COOLDOWN:
                if state.phase_age() > 1.2:
                    state.label_buf.clear()
                    state.translation = ""
                    state.api_error   = ""
                    translator.clear_result()
                    predictor.reset()
                    state.set_phase(Phase.IDLE)

        if state.phase == Phase.EDITING and state.phase_age() > CFG.edit_mode_timeout:
            state.set_phase(Phase.COLLECTING if state.label_buf else Phase.IDLE)

        hud.draw(frame, state,
                 topk=predictor.raw_topk,
                 fps=fps,
                 adapt_thresh=predictor.adaptive_thresh,
                 tts_ok=tts.ready,
                 api_ok=translator.ready,
                 model_ok=predictor.model_loaded,
                 api_error=state.api_error)

        cv2.imshow(CFG.win_title, frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        elif key == ord("c"):
            state.label_buf.clear()
            state.translation = ""
            state.api_error   = ""
            translator.clear_result()
            translator.clear_history()
            predictor.reset()
            state.set_phase(Phase.IDLE)
            log.info("🗑  Buffer + history dihapus")
        elif key == ord("s"):
            txt = state.translation or " ".join(state.label_buf)
            if txt:
                tts.speak(txt)
        elif key == ord("t"):
            if state.label_buf and translator.ready and not translator.pending:
                state.set_phase(Phase.TRANSLATING)
                translator.translate(list(state.label_buf), on_done=on_translated)
            elif state.label_buf and not translator.ready:
                state.translation = " ".join(state.label_buf)
                state.set_phase(Phase.SPEAKING)
                log.info("📝 Mode tanpa API — menampilkan label: %s", state.translation)
        elif key == ord("p"):
            state.paused = not state.paused
            log.info("⏸  Paused: %s", state.paused)
        elif key == ord("w"):
            state.export_transcript()
        elif key == ord("e"):
            if state.phase == Phase.EDITING:
                state.set_phase(Phase.COLLECTING if state.label_buf else Phase.IDLE)
            elif state.label_buf:
                state.set_phase(Phase.EDITING)
                state.edit_cursor = len(state.label_buf) - 1
        elif state.phase == Phase.EDITING:
            if key in (81, ord("a")):
                state.edit_cursor = max(0, state.edit_cursor - 1)
            elif key in (83, ord("d")):
                state.edit_cursor = min(len(state.label_buf)-1, state.edit_cursor+1)
            elif key in (255, 8):
                if state.label_buf:
                    removed = state.label_buf.pop(state.edit_cursor)
                    state.edit_cursor = min(state.edit_cursor, max(len(state.label_buf)-1, 0))
                    log.info("✏️  Dihapus: %s", removed)
                if not state.label_buf:
                    state.set_phase(Phase.IDLE)
            elif key == 13:
                state.set_phase(Phase.TRANSLATING)
                if translator.ready:
                    translator.translate(list(state.label_buf), on_done=on_translated)
                else:
                    state.translation = " ".join(state.label_buf)
                    state.set_phase(Phase.SPEAKING)

        elapsed = time.time() - loop_start
        if elapsed < frame_budget:
            time.sleep(frame_budget - elapsed)

    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    state.export_transcript()
    log.info("SignBridge AI v4 ditutup.")


if __name__ == "__main__":
    main()