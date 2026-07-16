import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

// Serverless instances have a read-only project directory, so writes go to
// /tmp. That storage is per-instance and NOT durable across cold starts —
// swap this for a real database (Postgres, Supabase, etc.) for production use.
const STORE_PATH = path.join("/tmp", "kmd-messages.json");

function readStore() {
  try {
    return JSON.parse(fs.readFileSync(STORE_PATH, "utf-8"));
  } catch {
    return [];
  }
}

function writeStore(list) {
  fs.writeFileSync(STORE_PATH, JSON.stringify(list, null, 2));
}

export async function GET() {
  return NextResponse.json({ messages: readStore() });
}

export async function POST(request) {
  const body = await request.json().catch(() => null);

  if (!body || !body.nama || !body.pesan) {
    return NextResponse.json(
      { error: "Nama dan pesan wajib diisi." },
      { status: 400 }
    );
  }

  const entry = {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
    nama: String(body.nama).slice(0, 120),
    instansi: String(body.instansi || "").slice(0, 120),
    keperluan: String(body.keperluan || "Pertanyaan umum").slice(0, 60),
    pesan: String(body.pesan).slice(0, 2000),
    createdAt: new Date().toISOString(),
  };

  const list = readStore();
  list.unshift(entry);
  writeStore(list.slice(0, 200));

  return NextResponse.json({ ok: true, entry });
}
