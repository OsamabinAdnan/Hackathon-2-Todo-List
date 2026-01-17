'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { AnimatedCard, AnimatedPage } from '@/components/ui/animate';
import { CheckCircle2Icon, LayoutDashboardIcon, SettingsIcon, LogOutIcon } from 'lucide-react';

export default function AlreadySignedInPage() {
  const router = useRouter();
  const [userName, setUserName] = useState<string>('');
  const [isSignedIn, setIsSignedIn] = useState<boolean>(false);

  useEffect(() => {
    // Check if user is signed in
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');

    if (token && userStr) {
      setIsSignedIn(true);
      try {
        const user = JSON.parse(userStr);
        setUserName(user.name || 'User');
      } catch {
        setUserName('User');
      }
    } else {
      // If not signed in, redirect to login
      router.push('/login');
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/login');
  };

  if (!isSignedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950 flex flex-col">
      <AnimatedPage>
        <div className="min-h-screen flex items-center justify-center p-3 xs:p-4">
          <AnimatedCard delay={0.1} className="w-full max-w-lg glass-card p-6 xs:p-8 sm:p-10">
            <div className="text-center">
              {/* Success Icon */}
              <div className="mx-auto w-20 h-20 xs:w-24 xs:h-24 rounded-full bg-success/10 flex items-center justify-center mb-6 border-2 border-success/20">
                <CheckCircle2Icon className="h-10 w-10 xs:h-12 xs:w-12 text-success" />
              </div>

              {/* Title */}
              <h1 className="text-2xl xs:text-3xl font-bold text-foreground mb-2">
                Already Signed In
              </h1>

              {/* Welcome Message */}
              <p className="text-base xs:text-lg text-muted-foreground mb-2">
                Welcome back, <span className="text-primary font-semibold">{userName}</span>!
              </p>

              <p className="text-sm text-muted-foreground mb-8">
                You're already logged into your account. Choose an option below to continue.
              </p>

              {/* Action Buttons */}
              <div className="space-y-3">
                <Link href="/dashboard" className="block">
                  <Button
                    className="w-full bg-primary text-primary-foreground hover:bg-primary/90 py-6 px-6 rounded-xl transition-all duration-200 font-bold shadow-lg hover:shadow-primary/25 flex items-center justify-center gap-3"
                  >
                    <LayoutDashboardIcon className="h-5 w-5" />
                    Go to Dashboard
                  </Button>
                </Link>

                <Link href="/dashboard/settings" className="block">
                  <Button
                    variant="outline"
                    className="w-full border-border/50 hover:bg-accent py-6 px-6 rounded-xl transition-all duration-200 font-bold flex items-center justify-center gap-3"
                  >
                    <SettingsIcon className="h-5 w-5" />
                    Account Settings
                  </Button>
                </Link>

                <Button
                  onClick={handleLogout}
                  variant="outline"
                  className="w-full border-destructive/50 text-destructive hover:bg-destructive/10 hover:border-destructive py-6 px-6 rounded-xl transition-all duration-200 font-bold flex items-center justify-center gap-3"
                >
                  <LogOutIcon className="h-5 w-5" />
                  Sign Out
                </Button>
              </div>

              {/* Additional Info */}
              <div className="mt-8 pt-6 border-t border-border/30">
                <p className="text-xs text-muted-foreground">
                  Need to switch accounts?{' '}
                  <button
                    onClick={handleLogout}
                    className="text-primary hover:underline font-semibold"
                  >
                    Sign out first
                  </button>
                </p>
              </div>
            </div>
          </AnimatedCard>
        </div>
      </AnimatedPage>
    </div>
  );
}
