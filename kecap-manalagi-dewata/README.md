# Kecap Manalagi Dewata — Situs Fullstack

Situs untuk PT Kecap Manalagi Dewata (Denpasar, Bali), dibangun dengan Next.js 14 (App Router).

## Struktur

app/
  page.js              -> Halaman utama (frontend)
  layout.js            -> Root layout + font
  globals.css          -> Semua styling
  admin/page.js         -> Halaman untuk melihat pesan masuk
  api/products/route.js -> GET /api/products - data produk
  api/contact/route.js  -> GET & POST /api/contact - pesan/pemesanan
data/
  products.json         -> Sumber data produk

## Menjalankan secara lokal

npm install
npm run dev

Buka http://localhost:3000 untuk situs, dan http://localhost:3000/admin untuk melihat pesan yang masuk dari form kontak.

## Build produksi

npm run build
npm run start

## Catatan penting: penyimpanan pesan

app/api/contact/route.js saat ini menyimpan pesan ke /tmp/kmd-messages.json di server.
Ini tidak permanen kalau dideploy ke platform serverless (Vercel dkk) — data hilang saat
instance daur ulang. Untuk produksi sungguhan, ganti readStore() / writeStore() di file
tersebut dengan koneksi ke database sungguhan (Postgres, Supabase, MongoDB, dll).

## Deploy

Proyek ini auto-terdeteksi sebagai aplikasi Next.js oleh Vercel dan Netlify — tinggal hubungkan
repo ini ke salah satu platform tersebut.

## Data perusahaan

Alamat, telepon, dan Instagram di situs ini diambil dari sumber publik (direktori bisnis,
jurnal ilmiah tentang PT Kecap Manalagi Dewata). Cek ulang dan sesuaikan jika ada perubahan.
