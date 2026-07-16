import os
import cv2
import mediapipe as mp
import numpy as np
import pickle

# Inisialisasi MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def extract_hand_keypoints(results):
    left = np.zeros(21*3)
    right = np.zeros(21*3)
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            points = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()
            if handedness.classification[0].label == 'Left':
                left = points
            else:
                right = points
    return np.concatenate([left, right])

def process_video(video_path, seq_len=30):
    cap = cv2.VideoCapture(video_path)
    buffer = []
    sequences = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
        kp = extract_hand_keypoints(result)
        buffer.append(kp)
        if len(buffer) == seq_len:
            sequences.append(np.array(buffer))
            buffer.pop(0)
    cap.release()
    return sequences

def main():
    raw_dir = "data/raw/wlasl100/WLASL100"
    labels_file = "data/raw/wlasl100/labels.txt"
    
    # Baca labels
    label_map = {}
    with open(labels_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                idx, word = parts[0], parts[1]
                label_map[idx] = word
            else:
                # Jika hanya satu kolom (nomor), maka kata default?
                pass
    
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    
    for folder_name in os.listdir(raw_dir):
        if not folder_name.isdigit():
            continue
        word = label_map.get(folder_name, folder_name)
        folder_path = os.path.join(raw_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue
        word_dir = os.path.join(processed_dir, word)
        os.makedirs(word_dir, exist_ok=True)
        video_files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
        for vf in video_files:
            video_path = os.path.join(folder_path, vf)
            print(f"Processing {word}/{vf}...")
            sequences = process_video(video_path)
            if sequences:
                out_file = os.path.join(word_dir, vf.replace('.mp4', '.pkl'))
                with open(out_file, 'wb') as f:
                    pickle.dump(sequences, f)
                print(f"  Saved {len(sequences)} sequences")
            else:
                print(f"  No sequences extracted")
    hands.close()
    print("Done.")

if __name__ == "__main__":
    main()