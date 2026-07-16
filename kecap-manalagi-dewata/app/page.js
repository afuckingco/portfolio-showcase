"use client";
import { useEffect, useRef, useState } from "react";

function useReveal() {
  const ref = useRef(null);
  useEffect(() => {
    const els = document.querySelectorAll(".reveal");
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.15 }
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);
  return ref;
}

export default function Home() {
  const revealRoot = useReveal();
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({
    nama: "",
    instansi: "",
    keperluan: "Pemesanan produk",
    pesan: "",
  });
  const [status, setStatus] = useState({ state: "idle", note: "" });

  useEffect(() => {
    fetch("/api/products")
      .then((r) => r.json())
      .then((d) => setProducts(d.products || []))
      .catch(() => setProducts([]));
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.nama || !form.pesan) return;
    setStatus({ state: "loading", note: "" });
    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Gagal mengirim pesan.");
      setStatus({
        state: "success",
        note: "Terima kasih, pesan Anda tercatat. Tim kami akan segera menghubungi.",
      });
      setForm({ nama: "", instansi: "", keperluan: "Pemesanan produk", pesan: "" });
    } catch (err) {
      setStatus({ state: "error", note: err.message });
    }
  }

  return (
    <div ref={revealRoot}>
      <header>
        <nav>
          <div className="brand">
            <svg className="mark" viewBox="0 0 40 40" fill="none">
              <path d="M20 3C20 3 9 17 9 25a11 11 0 0 0 22 0C31 17 20 3 20 3Z" fill="#c8860d" />
              <path d="M20 12C20 12 14 20 14 25a6 6 0 0 0 12 0c0-5-6-13-6-13Z" fill="#1b120d" opacity="0.35" />
            </svg>
            <div>
              PT Kecap Manalagi Dewata
              <small>Denpasar, Bali · Kecap Manis &amp; Kecap Asin</small>
            </div>
          </div>
          <div className="navlinks">
            <a href="#tentang">Tentang</a>
            <a href="#produk">Produk</a>
            <a href="#proses">Proses</a>
            <a href="#mitra">Mitra</a>
            <a href="#kontak">Kontak</a>
          </div>
          <a href="#kontak" className="nav-cta">Hubungi Kami</a>
        </nav>
      </header>

      <section className="hero">
        <svg className="hero-drop" viewBox="0 0 400 460" fill="none" aria-hidden="true">
          <path d="M200 20C200 20 60 210 60 300a140 140 0 0 0 280 0C340 210 200 20 200 20Z" fill="url(#g1)" />
          <path d="M200 90C200 90 120 190 120 260a80 80 0 0 0 160 0c0-70-80-170-80-170Z" fill="#1b120d" opacity="0.25" />
          <defs>
            <linearGradient id="g1" x1="60" y1="20" x2="340" y2="440" gradientUnits="userSpaceOnUse">
              <stop stopColor="#e6a934" />
              <stop offset="1" stopColor="#7a4a06" />
            </linearGradient>
          </defs>
        </svg>
        <div className="wrap hero-inner">
          <span className="eyebrow">PT Kecap Manalagi Dewata — Denpasar, Bali</span>
          <h1>Legit gula aren, <em>gurih</em> tauco pilihan, dari pabrik ke meja makan.</h1>
          <p className="lede">
            Kami memproduksi kecap manis dan kecap asin dengan bahan baku tauco dan gula
            aren pilihan di Padangsambian Kaja, Denpasar Barat — untuk dapur rumah, warung,
            hingga restoran di seluruh Bali.
          </p>
          <div className="cta-row">
            <a href="#produk" className="btn btn-primary">Lihat Produk Kami</a>
            <a href="#kontak" className="btn btn-ghost">Jadi Mitra Distribusi</a>
          </div>
          <div className="hero-stats">
            <div><div className="num">33</div><div className="lbl">karyawan bagian produksi</div></div>
            <div><div className="num">1</div><div className="lbl">pabrik di Denpasar Barat</div></div>
            <div><div className="num">2</div><div className="lbl">lini produk: manis &amp; asin</div></div>
          </div>
        </div>
      </section>

      <div className="ticker-band" aria-hidden="true">
        <div className="ticker-track">
          {Array.from({ length: 2 }).map((_, i) => (
            <span key={i} style={{ display: "contents" }}>
              <span>TAUCO &amp; KEDELAI PILIHAN</span>
              <span>GULA AREN ASLI BALI</span>
              <span>DIPRODUKSI DI DENPASAR BARAT</span>
              <span>KECAP MANIS &amp; KECAP ASIN</span>
            </span>
          ))}
        </div>
      </div>

      <section className="about" id="tentang">
        <div className="wrap about-grid">
          <div className="about-art reveal">
            <svg viewBox="0 0 420 460" fill="none">
              <rect x="40" y="120" width="150" height="300" rx="14" fill="#241811" />
              <rect x="40" y="120" width="150" height="300" rx="14" fill="url(#bg2)" opacity="0.9" />
              <rect x="70" y="70" width="90" height="60" rx="10" fill="#1b120d" />
              <rect x="90" y="40" width="50" height="40" rx="8" fill="#1b120d" />
              <ellipse cx="115" cy="40" rx="25" ry="9" fill="#c8860d" />
              <rect x="60" y="200" width="110" height="4" fill="#c8860d" opacity="0.5" />
              <rect x="60" y="230" width="80" height="4" fill="#c8860d" opacity="0.5" />
              <path d="M240 200c40-20 90-10 110 25s0 90-45 100-100-10-95-55c3-30 0-50 30-70Z" fill="#9c3428" opacity="0.9" />
              <circle cx="330" cy="150" r="6" fill="#c8860d" />
              <circle cx="350" cy="180" r="4" fill="#e6a934" />
              <circle cx="310" cy="120" r="3" fill="#e6a934" />
              <defs>
                <linearGradient id="bg2" x1="40" y1="120" x2="190" y2="420" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#c8860d" /><stop offset="1" stopColor="#7a4a06" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div className="about-copy reveal">
            <span className="kicker">Tentang Kami</span>
            <h2>Kecap yang diracik dari tauco, bukan jalan pintas</h2>
            <p>
              PT Kecap Manalagi Dewata berproduksi di Jalan Gunung Catur, Padangsambian
              Kaja, Denpasar Barat. Berbeda dari kebanyakan kecap pabrikan, bahan baku
              utama kami adalah <strong>tauco</strong> — pasta kedelai fermentasi — yang
              diolah bersama gula aren hingga jadi kecap manis dan kecap asin.
            </p>
            <p>
              Proses ini melibatkan puluhan karyawan produksi yang mengawasi tiap tahap,
              dari pengolahan tauco, pemasakan dengan gula aren, sampai pembotolan —
              bukan lini otomatis yang berjalan tanpa pengawasan.
            </p>
            <p>
              Produk kami dipakai oleh dapur rumah tangga, warung, dan usaha kuliner di
              Denpasar dan sekitarnya, dengan dua varian utama: kecap manis dan kecap asin.
            </p>
            <div className="signature-line">"Kecap yang jujur itu butuh waktu, bukan jalan pintas."</div>
          </div>
        </div>
      </section>

      <section className="products" id="produk">
        <div className="wrap">
          <div className="section-head reveal">
            <span className="kicker">Produk</span>
            <h2>Dua rasa dasar, satu <em>bahan baku</em> yang sama</h2>
            <p>Setiap varian dimasak dengan takaran gula aren dan tauco yang berbeda, disesuaikan untuk kebutuhan dapur yang berbeda pula.</p>
          </div>
          <div className="product-grid">
            {products.map((p) => (
              <div className="product-card reveal" key={p.id}>
                <span className="tag">{p.tag}</span>
                <h3>{p.name}</h3>
                <p>{p.description}</p>
                <div className="viscosity">
                  <div className="row"><span>Kekentalan</span><span>{p.viscosityLabel}</span></div>
                  <div className="bar"><div className="fill" style={{ width: `${p.viscosityPct}%` }} /></div>
                </div>
              </div>
            ))}
            {products.length === 0 && (
              <p style={{ color: "var(--ink-soft)" }}>Memuat produk…</p>
            )}
          </div>
        </div>
      </section>

      <section className="process" id="proses">
        <div className="wrap">
          <div className="section-head reveal">
            <span className="kicker">Proses</span>
            <h2>Lima tahap, tidak ada yang <em>dilewati</em></h2>
            <p>Berikut tahapan yang dilalui setiap batch sebelum sampai ke botol.</p>
          </div>
          <div className="process-list">
            {[
              ["01", "Pengolahan tauco", "Tauco sebagai bahan baku utama disiapkan dan dikontrol jumlahnya sesuai kebutuhan produksi harian."],
              ["02", "Perebusan & fermentasi", "Bahan baku direbus dan difermentasi untuk membentuk rasa dasar kecap."],
              ["03", "Perendaman air garam", "Hasil fermentasi direndam dalam larutan garam untuk menguatkan rasa dasar."],
              ["04", "Pemasakan dengan gula aren", "Sari bahan baku disaring lalu dimasak bersama gula aren hingga kental sesuai varian produk."],
              ["05", "Penyaringan & pembotolan", "Kecap disaring ulang, didinginkan, lalu dibotolkan di fasilitas kami di Denpasar Barat."],
            ].map(([num, title, desc]) => (
              <div className="p-step reveal" key={num}>
                <div className="num">{num}</div>
                <div>
                  <h4>{title}</h4>
                  <p>{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="why" id="mitra">
        <div className="wrap">
          <div className="section-head reveal">
            <span className="kicker">Kenapa Memilih Kami</span>
            <h2>Kualitas yang bisa dicek, bukan sekadar diklaim</h2>
          </div>
          <div className="why-grid reveal">
            {[
              ["Gula aren asli", "Dimasak bersama gula aren, bukan campuran gula pasir atau pemanis sintetis."],
              ["Bahan baku tauco", "Tauco sebagai bahan baku utama diawasi ketat mulai dari pembelian hingga pengolahan."],
              ["Diawasi langsung", "33 karyawan bagian produksi mengawasi tiap tahap pengolahan, bukan lini otomatis tanpa pengawasan."],
              ["Melayani Bali", "Melayani kebutuhan kecap untuk dapur rumah tangga, warung, hingga usaha kuliner di Denpasar dan sekitarnya."],
            ].map(([title, desc]) => (
              <div className="why-item" key={title}>
                <svg className="drop-ico" viewBox="0 0 24 24" fill="none"><path d="M12 2C12 2 5 11 5 15a7 7 0 0 0 14 0c0-4-7-13-7-13Z" fill="#9c3428" /></svg>
                <h4>{title}</h4>
                <p>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="distro">
        <div className="wrap reveal">
          <span className="kicker" style={{ color: "var(--amber-light)" }}>Mitra &amp; Distribusi</span>
          <h2>Ingin jadi <em>mitra</em> di wilayah Anda?</h2>
          <p>Kami terbuka untuk kemitraan distribusi dan pemesanan dalam jumlah besar. Hubungi kami untuk skema harga dan sampel produk.</p>
          <div className="cta-row">
            <a href="#kontak" className="btn btn-primary">Ajukan Kemitraan</a>
            <a href="https://www.instagram.com/kecap_manalagi9x/" target="_blank" rel="noreferrer" className="btn btn-ghost">Kunjungi Instagram Kami</a>
          </div>
        </div>
      </section>

      <section className="contact" id="kontak">
        <div className="wrap">
          <div className="section-head reveal">
            <span className="kicker">Kontak</span>
            <h2>Pesan produk, atau tanya apa saja</h2>
          </div>
          <div className="contact-grid">
            <div className="reveal">
              <div className="info-block">
                <span className="lbl">Pabrik</span>
                <span className="val">Jl. Gunung Catur No. 9X, Padangsambian Kaja, Denpasar Barat, Kota Denpasar, Bali</span>
              </div>
              <div className="info-block">
                <span className="lbl">Telepon</span>
                <span className="val"><a href="tel:+623617453323">(0361) 7453323</a></span>
              </div>
              <div className="info-block">
                <span className="lbl">Instagram</span>
                <span className="val"><a href="https://www.instagram.com/kecap_manalagi9x/" target="_blank" rel="noreferrer">@kecap_manalagi9x</a></span>
              </div>
              <div className="info-block">
                <span className="lbl">Jam Operasional</span>
                <span className="val">Senin–Sabtu, 08.00–17.00 WITA</span>
              </div>
            </div>
            <form className="reveal" onSubmit={handleSubmit}>
              <div className="field">
                <label htmlFor="nama">Nama</label>
                <input id="nama" type="text" placeholder="Nama lengkap Anda" required
                  value={form.nama} onChange={(e) => setForm({ ...form, nama: e.target.value })} />
              </div>
              <div className="field">
                <label htmlFor="instansi">Nama Usaha / Instansi</label>
                <input id="instansi" type="text" placeholder="Restoran, katering, toko, dll (opsional)"
                  value={form.instansi} onChange={(e) => setForm({ ...form, instansi: e.target.value })} />
              </div>
              <div className="field">
                <label htmlFor="keperluan">Keperluan</label>
                <select id="keperluan" value={form.keperluan}
                  onChange={(e) => setForm({ ...form, keperluan: e.target.value })}>
                  <option>Pemesanan produk</option>
                  <option>Kemitraan distribusi</option>
                  <option>Pertanyaan umum</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="pesan">Pesan</label>
                <textarea id="pesan" placeholder="Ceritakan kebutuhan Anda, termasuk perkiraan jumlah pesanan bila ada" required
                  value={form.pesan} onChange={(e) => setForm({ ...form, pesan: e.target.value })} />
              </div>
              <button type="submit" className="btn btn-primary" disabled={status.state === "loading"}>
                {status.state === "loading" ? "Mengirim…" : "Kirim Pesan"}
              </button>
              {status.note && (
                <span className="form-note" style={{ color: status.state === "error" ? "var(--temple-red)" : "var(--ink-soft)" }}>
                  {status.note}
                </span>
              )}
            </form>
          </div>
        </div>
      </section>

      <footer>
        <div className="wrap">
          <div className="foot-grid">
            <div className="foot-brand">
              PT Kecap Manalagi Dewata
              <p>Kecap manis dan kecap asin, diproduksi di Padangsambian Kaja, Denpasar Barat, Bali.</p>
            </div>
            <div className="foot-cols">
              <div className="foot-col">
                <h5>Navigasi</h5>
                <a href="#tentang">Tentang Kami</a>
                <a href="#produk">Produk</a>
                <a href="#proses">Proses Produksi</a>
                <a href="#kontak">Kontak</a>
              </div>
              <div className="foot-col">
                <h5>Kontak</h5>
                <span>(0361) 7453323</span>
                <a href="https://www.instagram.com/kecap_manalagi9x/" target="_blank" rel="noreferrer">@kecap_manalagi9x</a>
                <span>Denpasar Barat, Bali</span>
              </div>
            </div>
          </div>
          <div className="foot-bottom">
            <span>© 2026 PT Kecap Manalagi Dewata.</span>
            <span>Diproduksi di Denpasar, Bali.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
