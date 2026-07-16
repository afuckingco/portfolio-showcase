"use client";
import { useEffect, useState } from "react";

export default function AdminPage() {
  const [messages, setMessages] = useState(null);

  useEffect(() => {
    fetch("/api/contact")
      .then((r) => r.json())
      .then((d) => setMessages(d.messages || []))
      .catch(() => setMessages([]));
  }, []);

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "48px 24px", fontFamily: "var(--body)" }}>
      <h1 style={{ fontFamily: "var(--display)", fontSize: "1.8rem", marginBottom: 8 }}>
        Pesan Masuk — PT Kecap Manalagi Dewata
      </h1>
      <p style={{ color: "var(--ink-soft)", marginBottom: 28, fontSize: "0.85rem" }}>
        Data disimpan sementara di server (reset saat instance serverless daur ulang).
        Untuk penyimpanan permanen, sambungkan endpoint ini ke database (Postgres/Supabase/dll).
      </p>
      {messages === null && <p>Memuat…</p>}
      {messages && messages.length === 0 && <p>Belum ada pesan masuk.</p>}
      {messages && messages.map((m) => (
        <div key={m.id} style={{ border: "1px solid var(--line)", borderRadius: 12, padding: 20, marginBottom: 14, background: "var(--rice-cream)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", color: "var(--ink-soft)", marginBottom: 8 }}>
            <span>{m.keperluan}</span>
            <span>{new Date(m.createdAt).toLocaleString("id-ID")}</span>
          </div>
          <strong>{m.nama}</strong>{m.instansi ? ` — ${m.instansi}` : ""}
          <p style={{ marginTop: 8 }}>{m.pesan}</p>
        </div>
      ))}
    </div>
  );
}
