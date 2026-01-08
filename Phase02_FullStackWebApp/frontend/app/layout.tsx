import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";
import { NotificationProvider } from "@/context/notification-context";
import { ThemeProvider } from "next-themes";
import QueryProvider from "@/components/providers/QueryProvider";
import { BackgroundGlow } from "@/components/background-glow";
import { AppNavbar } from "@/components/layout/AppNavbar";
import { AppFooter } from "@/components/layout/AppFooter";
import { Toaster } from "sonner";
import NextTopLoader from "nextjs-toploader";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Taskify - Smart Task Management",
    template: "%s | Taskify"
  },
  description: "Powerful multi-user task management application with advanced features, recurring tasks, and beautiful UI",
  keywords: ["task management", "productivity", "todo app", "recurring tasks", "priority management", "task tracker"],
  authors: [{ name: "Osama bin Adnan", url: "https://github.com/OsamabinAdnan" }],
  creator: "Osama bin Adnan",
  publisher: "Osama bin Adnan",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://taskify-osamabinadnan.vercel.app/'),
  alternates: {
    canonical: '/',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://taskify-osamabinadnan.vercel.app/',
    title: 'Taskify - Smart Task Management',
    description: 'Powerful multi-user task management application with advanced features, recurring tasks, and beautiful UI',
    siteName: 'Taskify',
    images: [],
  },
  twitter: {
    card: 'summary',
    title: 'Taskify - Smart Task Management',
    description: 'Powerful multi-user task management application with advanced features, recurring tasks, and beautiful UI',
  },
  icons: {
    icon: '/todo_icon.png',
  },
  manifest: '/site.webmanifest',
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#FAFAFF' },
    { media: '(prefers-color-scheme: dark)', color: '#0B0A14' },
  ],
  colorScheme: 'dark light',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: 'cover',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased flex flex-col",
          inter.variable,
          jetbrainsMono.variable
        )}
        suppressHydrationWarning
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <NextTopLoader
            color="hsl(var(--primary))"
            initialPosition={0.08}
            crawlSpeed={200}
            height={3}
            crawl={true}
            showSpinner={false}
            easing="ease"
            speed={200}
            shadow="0 0 10px hsl(var(--primary)),0 0 5px hsl(var(--primary))"
            zIndex={1600}
            showAtBottom={false}
          />
          <BackgroundGlow />
          <AppNavbar />
          <Toaster
            position="top-right"
            theme="system"
            visibleToasts={5}
            richColors={false}
            closeButton={true}
            toastOptions={{
              unstyled: true,
              classNames: {
                toast: 'glass-toast',
                title: 'glass-toast-title',
                description: 'glass-toast-description',
                closeButton: 'glass-toast-close',
              },
            }}
          />
          <QueryProvider>
            <NotificationProvider>
              <div className="flex flex-col flex-1">
                {children}
              </div>
              <AppFooter />
            </NotificationProvider>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
