import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CardioInsight — Explainable AI-Based ECG Clinical Decision Support System',
  description: 'AI-assisted 12-lead electrocardiogram analysis and clinical decision support using XGBoost and SHAP explainability.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-slate-50">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="h-full font-sans antialiased text-slate-900 bg-slate-50 dark:bg-slate-950 selection:bg-sky-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
