"""
╔══════════════════════════════════════════════════════╗
║       SignBridge — Trainer Model LSTM v1.0           ║
║   Melatih model gesture dari data yang sudah direkam ║
╚══════════════════════════════════════════════════════╝

Cara pakai:
  python train_model.py

Hasil:
  models/hand_lstm_model.h5     ← model untuk signbridge_v4.py
  models/label_encoder.pkl      ← encoder kelas
  models/training_report.txt    ← laporan akurasi
"""

from __future__ import annotations

import os, sys, json, time
from pathlib import Path
from typing import List, Tuple

import numpy as np

# Cek dependency
try:
    import tensorflow as tf
    tf.get_logger().setLevel("ERROR")
except ImportError:
    print("❌ TensorFlow tidak terinstall. Jalankan:")
    print("   pip install tensorflow")
    sys.exit(1)

try:
    import joblib
except ImportError:
    print("❌ joblib tidak terinstall. Jalankan:")
    print("   pip install joblib")
    sys.exit(1)

try:
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix
except ImportError:
    print("❌ scikit-learn tidak terinstall. Jalankan:")
    print("   pip install scikit-learn")
    sys.exit(1)

# ── Konfigurasi (harus sama dengan collect_data.py & signbridge_v4.py) ────────
DATA_DIR    = Path("data/raw")
MODEL_DIR   = Path("models")
SEQ_LEN     = 30
EPOCHS      = 80
BATCH_SIZE  = 32
VAL_SPLIT   = 0.15
TEST_SPLIT  = 0.10
DELTA_FEAT  = True    # harus sama dengan CFG.delta_features di signbridge_v4.py


# ─────────────────────────────────────────────────────────────────────────────
def load_dataset() -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """Muat semua file .npy dari data/raw/<gesture>/."""
    gestures = sorted([d.name for d in DATA_DIR.iterdir() if d.is_dir()])
    if not gestures:
        print(f"❌ Tidak ada data di {DATA_DIR}. Jalankan collect_data.py dulu.")
        sys.exit(1)

    print(f"Ditemukan {len(gestures)} gesture: {gestures}\n")

    X, y = [], []
    for gesture in gestures:
        files = sorted((DATA_DIR / gesture).glob("*.npy"))
        if not files:
            print(f"  ⚠  {gesture}: tidak ada file — dilewati")
            continue
        for fp in files:
            seq = np.load(str(fp))           # shape: (SEQ_LEN, 126)
            if seq.shape != (SEQ_LEN, 126):
                print(f"  ⚠  {fp.name}: shape salah {seq.shape} — dilewati")
                continue
            X.append(seq)
            y.append(gesture)
        print(f"  ✓ {gesture:<22} {len(files)} sampel")

    print(f"\n  Total sekuens valid: {len(X)}\n")
    return np.array(X, dtype=np.float32), np.array(y), gestures


def add_delta_features(X: np.ndarray) -> np.ndarray:
    """
    Tambahkan fitur delta (selisih antar frame).
    Input : (N, SEQ_LEN, 126)
    Output: (N, SEQ_LEN, 252)
    Harus konsisten dengan cara SignBridge v4 memproses fitur.
    """
    deltas = np.zeros_like(X)
    deltas[:, 1:, :] = X[:, 1:, :] - X[:, :-1, :]
    return np.concatenate([X, deltas], axis=-1)


def augment(X: np.ndarray, y: np.ndarray,
            factor: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """
    Augmentasi sederhana: noise kecil + time-shift untuk perbanyak data.
    factor=3 → dataset 3x lebih besar.
    """
    Xa, ya = [X], [y]
    for _ in range(factor - 1):
        noise = np.random.normal(0, 0.005, X.shape).astype(np.float32)
        # Shift waktu ±1-3 frame secara acak per sampel
        shifted = np.zeros_like(X)
        for i in range(len(X)):
            shift = np.random.randint(-3, 4)
            if shift > 0:
                shifted[i, shift:, :] = X[i, :-shift, :]
            elif shift < 0:
                shifted[i, :shift, :] = X[i, -shift:, :]
            else:
                shifted[i] = X[i]
        Xa.append(shifted + noise)
        ya.append(y)
    return np.concatenate(Xa), np.concatenate(ya)


def build_model(input_shape: Tuple, n_classes: int) -> tf.keras.Model:
    """
    Arsitektur LSTM dua lapis + Attention sederhana + Dense head.
    Seimbang antara akurasi dan kecepatan inferensi real-time.
    """
    inp = tf.keras.Input(shape=input_shape, name="keypoints")

    # LSTM stack
    x = tf.keras.layers.LSTM(128, return_sequences=True,
                              dropout=0.2, recurrent_dropout=0.1)(inp)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.LSTM(64, return_sequences=True,
                              dropout=0.2, recurrent_dropout=0.1)(x)
    x = tf.keras.layers.BatchNormalization()(x)

    # Attention sederhana (bobot per timestep)
    attn = tf.keras.layers.Dense(1, activation="tanh")(x)          # (B, T, 1)
    attn = tf.keras.layers.Softmax(axis=1)(attn)                    # normalize
    x    = tf.keras.layers.Multiply()([x, attn])                    # weighted
    x    = tf.keras.layers.Lambda(lambda t: tf.reduce_sum(t, axis=1))(x)  # sum

    # Classification head
    x = tf.keras.layers.Dense(128, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    x = tf.keras.layers.Dense(64, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    out = tf.keras.layers.Dense(n_classes, activation="softmax", name="gesture")(x)

    model = tf.keras.Model(inp, out, name="SignBridge_LSTM")
    return model


# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("═══ SignBridge Model Trainer ═══\n")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    print("▶ Memuat dataset...")
    X_raw, y_str, gestures = load_dataset()

    # 2. Encode label
    le = LabelEncoder()
    le.fit(gestures)
    y = le.transform(y_str)
    n_classes = len(le.classes_)
    print(f"Kelas: {list(le.classes_)}")
    print(f"Distribusi: { {g: int((y_str == g).sum()) for g in le.classes_} }\n")

    # 3. Delta features
    if DELTA_FEAT:
        print("▶ Menambahkan fitur delta...")
        X = add_delta_features(X_raw)
    else:
        X = X_raw
    feat_dim = X.shape[-1]
    print(f"Shape fitur: {X.shape}  (N, {SEQ_LEN}, {feat_dim})\n")

    # 4. Augmentasi
    print("▶ Augmentasi data...")
    X, y = augment(X, y, factor=3)
    print(f"Setelah augmentasi: {X.shape[0]} sampel\n")

    # 5. Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SPLIT, random_state=42, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=VAL_SPLIT / (1 - TEST_SPLIT),
        random_state=42, stratify=y_train)

    print(f"Train : {len(X_train)} sampel")
    print(f"Val   : {len(X_val)} sampel")
    print(f"Test  : {len(X_test)} sampel\n")

    # 6. Build model
    print("▶ Membangun model...")
    model = build_model((SEQ_LEN, feat_dim), n_classes)
    model.summary()
    print()

    # 7. Compile
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    # 8. Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=15,
            restore_best_weights=True, verbose=1),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=7,
            min_lr=1e-5, verbose=1),
        tf.keras.callbacks.ModelCheckpoint(
            str(MODEL_DIR / "best_checkpoint.h5"),
            monitor="val_accuracy", save_best_only=True, verbose=0),
    ]

    # 9. Training
    print("▶ Mulai training...\n")
    t0 = time.time()
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )
    elapsed = time.time() - t0
    print(f"\nTraining selesai dalam {elapsed/60:.1f} menit\n")

    # 10. Evaluasi
    print("▶ Evaluasi di data test...\n")
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Accuracy : {acc*100:.2f}%")
    print(f"Test Loss     : {loss:.4f}\n")

    y_pred = np.argmax(model.predict(X_test, verbose=0), axis=1)
    report = classification_report(
        y_test, y_pred,
        target_names=le.classes_,
        digits=3,
    )
    print(report)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print("Confusion Matrix:")
    print("  " + "  ".join(f"{c[:5]:>5}" for c in le.classes_))
    for i, row in enumerate(cm):
        print(f"{le.classes_[i][:5]:>5}", " ".join(f"{v:>6}" for v in row))
    print()

    # 11. Simpan model & encoder
    model_path = MODEL_DIR / "hand_lstm_model.h5"
    enc_path   = MODEL_DIR / "label_encoder.pkl"
    model.save(str(model_path))
    joblib.dump(le, str(enc_path))
    print(f"✅ Model disimpan  : {model_path}")
    print(f"✅ Encoder disimpan: {enc_path}")

    # 12. Laporan teks
    report_path = MODEL_DIR / "training_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("═══ SignBridge Training Report ═══\n\n")
        f.write(f"Tanggal    : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Gesture    : {list(le.classes_)}\n")
        f.write(f"Sampel     : {X.shape[0]} (setelah augmentasi)\n")
        f.write(f"Fitur      : {feat_dim} (delta={'ya' if DELTA_FEAT else 'tidak'})\n")
        f.write(f"Epochs     : {len(history.history['loss'])} / {EPOCHS}\n")
        f.write(f"Durasi     : {elapsed/60:.1f} menit\n")
        f.write(f"\nTest Accuracy : {acc*100:.2f}%\n")
        f.write(f"Test Loss     : {loss:.4f}\n\n")
        f.write(report)
    print(f"✅ Laporan disimpan : {report_path}\n")

    # 13. Petunjuk selanjutnya
    if acc >= 0.90:
        grade = "SANGAT BAGUS 🎉"
    elif acc >= 0.75:
        grade = "CUKUP BAIK 👍"
    else:
        grade = "PERLU LEBIH BANYAK DATA ⚠️"

    print("═══ Ringkasan ═══")
    print(f"  Akurasi test : {acc*100:.1f}%  → {grade}")
    print()
    if acc < 0.75:
        print("  Tips meningkatkan akurasi:")
        print("  • Rekam lebih banyak sampel (target 150-200 per gesture)")
        print("  • Variasikan posisi tangan, sudut, dan jarak ke kamera")
        print("  • Pastikan pencahayaan cukup saat merekam")
        print("  • Hapus sampel yang blur/salah dengan tombol D di collect_data.py")
    print()
    print("  Jalankan SignBridge:")
    print("  python signbridge_v4.py\n")


if __name__ == "__main__":
    main()