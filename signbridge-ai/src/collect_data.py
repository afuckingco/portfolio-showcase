"""
╔══════════════════════════════════════════════════════╗
║      SignBridge — Pengumpul Data Gesture v1.0        ║
║   Rekam keypoint tangan untuk training model LSTM    ║
╚══════════════════════════════════════════════════════╝

Cara pakai:
  python collect_data.py

Kontrol saat merekam:
  SPACE  — mulai/berhenti rekam satu sesi
  N      — gesture berikutnya
  R      — ulangi gesture ini (hapus data sesi ini)
  D      — hapus semua data gesture ini
  Q      — keluar & simpan

Hasil disimpan di: data/raw/<nama_gesture>/<index>.npy
"""

from __future__ import annotations

import os, sys, time, json
from pathlib import Path
from collections import deque
from typing import List, Optional

import cv2
import mediapipe as mp
import numpy as np

# ── Daftar kata/gesture yang mau direkam ──────────────────────────────────────
# Tambah atau kurangi sesuai kebutuhan
GESTURES = [
    "halo",
    "terima_kasih",
    "tolong",
    "maaf",
    "ya",
    "tidak",
    "nama_saya",
    "apa_kabar",
    "baik",
    "selamat_pagi",
    "selamat_siang",
    "selamat_malam",
    "sampai_jumpa",
    "saya_tidak_mengerti",
    "bisa_ulangi",
]

# ── Konfigurasi ───────────────────────────────────────────────────────────────
SEQ_LEN       = 30       # panjang sekuens (frame per sampel) — harus sama dengan model
SAMPLES_GOAL  = 120      # target sampel per gesture
DATA_DIR      = Path("data/raw")
CAM_IDX       = 0


# ─────────────────────────────────────────────────────────────────────────────
def extract_kp(result) -> np.ndarray:
    """Ekstrak keypoint kedua tangan (126 nilai: L63 + R63)."""
    L = np.zeros(63, dtype=np.float32)
    R = np.zeros(63, dtype=np.float32)
    if result.multi_hand_landmarks:
        for lm, hd in zip(result.multi_hand_landmarks, result.multi_handedness):
            pts = np.array(
                [[p.x, p.y, p.z] for p in lm.landmark], dtype=np.float32
            ).flatten()
            if hd.classification[0].label == "Left":
                L = pts
            else:
                R = pts
    return np.concatenate([L, R])


def count_existing(gesture: str) -> int:
    d = DATA_DIR / gesture
    if not d.exists():
        return 0
    return len(list(d.glob("*.npy")))


def save_sequence(gesture: str, seq: List[np.ndarray]) -> int:
    d = DATA_DIR / gesture
    d.mkdir(parents=True, exist_ok=True)
    idx = count_existing(gesture)
    np.save(str(d / f"{idx:05d}.npy"), np.array(seq, dtype=np.float32))
    return idx


def draw_ui(frame, gesture: str, g_idx: int, total_g: int,
            count: int, recording: bool, seq_buf: List, cooldown: bool):
    fh, fw = frame.shape[:2]

    # Panel atas
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (fw, 60), (14, 14, 20), -1)
    cv2.addWeighted(overlay, 0.80, frame, 0.20, 0, frame)

    # Nama gesture
    label = gesture.replace("_", " ").upper()
    cv2.putText(frame, f"Gesture [{g_idx+1}/{total_g}]: {label}",
                (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 200, 60), 2, cv2.LINE_AA)

    # Progres sampel
    bar_w = fw - 24
    filled = int(bar_w * min(count / SAMPLES_GOAL, 1.0))
    cv2.rectangle(frame, (12, 38), (12 + bar_w, 52), (40, 40, 55), -1)
    col_bar = (60, 220, 80) if count >= SAMPLES_GOAL else (50, 150, 255)
    if filled:
        cv2.rectangle(frame, (12, 38), (12 + filled, 52), col_bar, -1)
    cv2.putText(frame, f"{count}/{SAMPLES_GOAL} sampel",
                (14, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (200, 200, 210), 1, cv2.LINE_AA)

    # Status rekam
    if cooldown:
        status, sc = "Bersiap...", (40, 200, 255)
    elif recording:
        status, sc = f"● MEREKAM  [{len(seq_buf)}/{SEQ_LEN} frame]", (60, 60, 220)
    else:
        status, sc = "SPACE = mulai rekam", (130, 130, 140)

    cv2.putText(frame, status, (12, fh - 48),
                cv2.FONT_HERSHEY_SIMPLEX, 0.60, sc, 2, cv2.LINE_AA)

    # Selesai
    if count >= SAMPLES_GOAL:
        cv2.putText(frame, "✓ SELESAI — tekan N untuk lanjut",
                    (12, fh - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (60, 220, 80), 2, cv2.LINE_AA)
    else:
        cv2.putText(frame,
                    "N=lanjut  R=ulangi sesi  D=hapus semua  Q=keluar",
                    (12, fh - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (110, 110, 120), 1, cv2.LINE_AA)


# ─────────────────────────────────────────────────────────────────────────────
def main():
    mp_h   = mp.solutions.hands
    mp_drw = mp.solutions.drawing_utils
    hands  = mp_h.Hands(
        static_image_mode=False,
        min_detection_confidence=0.55,
        min_tracking_confidence=0.55,
        max_num_hands=2,
    )

    cap = cv2.VideoCapture(CAM_IDX)
    if not cap.isOpened():
        print("❌ Kamera tidak bisa dibuka"); sys.exit(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)

    g_idx     = 0
    recording = False
    seq_buf: List[np.ndarray] = []
    cooldown  = False
    cd_start  = 0.0

    print("\n═══ SignBridge Data Collector ═══")
    print(f"Gesture  : {len(GESTURES)} kata")
    print(f"Target   : {SAMPLES_GOAL} sampel per gesture")
    print(f"Simpan ke: {DATA_DIR.resolve()}\n")

    for g in GESTURES:
        n = count_existing(g)
        status = "✓" if n >= SAMPLES_GOAL else f"{n}/{SAMPLES_GOAL}"
        print(f"  {g:<20} {status}")
    print()

    while cap.isOpened() and g_idx < len(GESTURES):
        ret, frame = cap.read()
        if not ret:
            continue

        gesture = GESTURES[g_idx]
        count   = count_existing(gesture)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = hands.process(rgb)
        rgb.flags.writeable = True

        hand_visible = bool(result.multi_hand_landmarks)
        if hand_visible:
            for hl in result.multi_hand_landmarks:
                mp_drw.draw_landmarks(
                    frame, hl, mp_h.HAND_CONNECTIONS,
                    mp_drw.DrawingSpec((100, 230, 100), 2, 4),
                    mp_drw.DrawingSpec((200, 200, 200), 1),
                )

        # Cooldown sebelum rekam (beri waktu bersiap)
        if cooldown:
            if time.time() - cd_start >= 1.5:
                cooldown  = False
                recording = True
                seq_buf   = []

        # Rekam frame
        if recording and hand_visible:
            kp = extract_kp(result)
            seq_buf.append(kp)
            if len(seq_buf) >= SEQ_LEN:
                save_sequence(gesture, seq_buf)
                count = count_existing(gesture)
                seq_buf   = []
                recording = False
                print(f"  ✓ {gesture}  [{count}/{SAMPLES_GOAL}]")
                # Jika masih perlu sampel, langsung cooldown lagi
                if count < SAMPLES_GOAL:
                    cooldown = True
                    cd_start = time.time()
        elif recording and not hand_visible:
            # Tangan hilang saat merekam → reset buffer tapi tetap recording
            seq_buf = []

        draw_ui(frame, gesture, g_idx, len(GESTURES),
                count, recording, seq_buf, cooldown)

        cv2.imshow("SignBridge — Kumpul Data", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        elif key == ord(" "):   # SPACE — mulai rekam
            if not recording and not cooldown:
                cooldown = True
                cd_start = time.time()
                seq_buf  = []

        elif key == ord("r"):   # R — batalkan sesi ini
            recording = False
            cooldown  = False
            seq_buf   = []
            print(f"  ↩  Sesi dibatalkan")

        elif key == ord("d"):   # D — hapus semua data gesture ini
            d = DATA_DIR / gesture
            if d.exists():
                for f in d.glob("*.npy"):
                    f.unlink()
                print(f"  🗑  Semua data {gesture} dihapus")
            recording = False
            cooldown  = False
            seq_buf   = []

        elif key == ord("n"):   # N — gesture berikutnya
            if count >= SAMPLES_GOAL or key == ord("n"):
                recording = False
                cooldown  = False
                seq_buf   = []
                g_idx    += 1
                if g_idx < len(GESTURES):
                    print(f"\n▶ Pindah ke: {GESTURES[g_idx]}")

        # Auto-lanjut jika sudah cukup sampel dan tidak sedang rekam
        if count >= SAMPLES_GOAL and not recording and not cooldown:
            pass  # tunggu user tekan N

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

    # Ringkasan akhir
    print("\n═══ Ringkasan Data ═══")
    total = 0
    for g in GESTURES:
        n = count_existing(g)
        total += n
        bar = "█" * min(n, 20) + "░" * max(0, 20 - n)
        pct = n / SAMPLES_GOAL * 100
        print(f"  {g:<20} {bar} {n:>4}/{SAMPLES_GOAL}  ({pct:.0f}%)")
    print(f"\n  Total sekuens: {total}")
    print(f"  Siap training: {'YA ✅' if all(count_existing(g) >= SAMPLES_GOAL for g in GESTURES) else 'BELUM — lanjutkan rekam'}")
    print(f"\nJalankan berikutnya: python train_model.py\n")


if __name__ == "__main__":
    main()