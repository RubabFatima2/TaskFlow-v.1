// import type { Metadata } from 'next';
// import { Inter } from 'next/font/google';
// import { AuthProvider } from '@/context/AuthContext';
// import ErrorBoundary from '@/components/ErrorBoundary';
// import './globals.css';

// const inter = Inter({ subsets: ['latin'] });

// export const metadata: Metadata = {
//   title: 'TaskFlow - Todo Application',
//   description: 'A full-stack todo application',
// };

// export default function RootLayout({
//   children,
// }: {
//   children: React.ReactNode;
// }) {
//   return (
//     <html lang="en">
//       <body className={inter.className}>
//         <ErrorBoundary>
//           <AuthProvider>
//             {children}
//           </AuthProvider>
//         </ErrorBoundary>
//       </body>
//     </html>
//   );
// }
import type { Metadata } from 'next';
import { Syne, DM_Sans } from 'next/font/google';
import { AuthProvider } from '@/context/AuthContext';
import ErrorBoundary from '@/components/ErrorBoundary';
import NotificationProvider from '@/components/providers/NotificationProvider';
import './globals.css';

/* ─── Fonts ─────────────────────────────────────────────── */
const syne = Syne({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--font-display',
  display: 'swap',
});

const dmSans = DM_Sans({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600'],
  style: ['normal', 'italic'],
  variable: '--font-body',
  display: 'swap',
});

/* ─── Metadata ───────────────────────────────────────────── */
export const metadata: Metadata = {
  title: {
    default: 'TaskFlow — Todo Application',
    template: '%s · TaskFlow',
  },
  description: 'A full-stack todo application built for clarity, speed, and focus.',
  icons: {
    icon: '/favicon.svg',
    shortcut: '/favicon.svg',
    apple: '/favicon.svg',
  },
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#f5f6fa' },
    { media: '(prefers-color-scheme: dark)',  color: '#0d0f1a' },
  ],
};

/* ─── Root Layout ────────────────────────────────────────── */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${syne.variable} ${dmSans.variable}`}
      suppressHydrationWarning
    >
      <body className={`${dmSans.className} antialiased`}>
        <ErrorBoundary>
          <AuthProvider>
            <NotificationProvider>
              {children}
            </NotificationProvider>
          </AuthProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}