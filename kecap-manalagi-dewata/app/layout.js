import "./globals.css";

export const metadata = {
  title: "PT Kecap Manalagi Dewata — Kecap Manis Asli Bali",
  description:
    "PT Kecap Manalagi Dewata memproduksi kecap manis dan kecap asin di Denpasar, Bali, dengan bahan baku tauco dan gula aren pilihan.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="id">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="true" />
        <link
          href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,500&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
