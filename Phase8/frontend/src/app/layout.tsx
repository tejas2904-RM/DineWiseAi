import type { Metadata, Viewport } from 'next';
import './globals.css';
import { ThemeProvider } from '@/lib/theme-provider';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { MobileTabBar } from '@/components/MobileTabBar';
import { InstallPrompt } from '@/components/InstallPrompt';

export const metadata: Metadata = {
  title: 'DineWise AI — Smart Restaurant Recommendations',
  description:
    'Personalized AI restaurant recommendations with explanations, history, and favorites.',
  manifest: '/manifest.json',
  applicationName: 'DineWise AI',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'DineWise AI',
  },
  icons: {
    icon: '/icon.svg',
    apple: '/icon.svg',
  },
};

export const viewport: Viewport = {
  themeColor: '#10b981',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossOrigin=""
        />
      </head>
      <body>
        <ThemeProvider>
          <a
            href="#main"
            className="absolute left-2 top-2 -translate-y-20 focus:translate-y-0 transition-transform z-50 btn btn-primary"
          >
            Skip to content
          </a>
          <div className="min-h-screen flex flex-col">
            <Navbar />
            <main
              id="main"
              className="flex-1 w-full max-w-[480px] md:max-w-[1100px] mx-auto px-4 py-5 space-y-4"
            >
              <InstallPrompt />
              {children}
            </main>
            <Footer />
            <MobileTabBar />
          </div>
        </ThemeProvider>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js').catch(function() {});
                });
              }
            `,
          }}
        />
      </body>
    </html>
  );
}
