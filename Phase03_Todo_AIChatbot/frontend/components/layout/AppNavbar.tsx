'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { LogOutIcon } from 'lucide-react';

export function AppNavbar() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userName, setUserName] = useState<string>('User');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  // Load user and check authentication on mount
  useEffect(() => {
    setIsMounted(true);
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);

    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        setUserName(user.name || 'User');
      } catch (error) {
        console.error('Failed to parse user data:', error);
      }
    }

    // Listen for custom auth events (for same-tab auth state changes)
    const handleAuthChange = (e: CustomEvent) => {
      if (e.detail.type === 'LOGIN') {
        setIsAuthenticated(true);
        setUserName(e.detail.user?.name || 'User');
      } else if (e.detail.type === 'LOGOUT') {
        setIsAuthenticated(false);
        setUserName('User');
      }
    };

    window.addEventListener('auth-change', handleAuthChange as EventListener);

    return () => {
      window.removeEventListener('auth-change', handleAuthChange as EventListener);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    // Dispatch custom auth event to update navbar
    window.dispatchEvent(new CustomEvent('auth-change', {
      detail: {
        type: 'LOGOUT'
      }
    }));

    window.location.href = '/login';
  };

  // Close sidebar when route changes
  useEffect(() => {
    setSidebarOpen(false);
  }, [pathname]);

  // Close sidebar when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const sidebar = document.getElementById('app-sidebar');
      const hamburgerButton = document.querySelector('.hamburger-button');

      if (sidebarOpen &&
          sidebar &&
          !sidebar.contains(event.target as Node) &&
          !hamburgerButton?.contains(event.target as Node)) {
        setSidebarOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [sidebarOpen]);

  // Don't render until component is mounted (prevents hydration mismatch)
  if (!isMounted) {
    return null;
  }

  return (
    <>
      {/* Mobile Sidebar (only show when authenticated) */}
      {isAuthenticated && (
        <motion.div
          id="app-sidebar"
          className={`fixed inset-y-0 z-40 flex w-[90vw] max-w-[320px] min-w-[280px] flex-col glass-sidebar transition-transform duration-300 ease-in-out lg:hidden ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
          initial={{ x: -320 }}
          animate={{ x: sidebarOpen ? 0 : -320 }}
          transition={{ duration: 0.3, ease: 'easeInOut' }}
        >
          <div className="flex flex-col grow pt-5 pb-4 overflow-y-auto">
            <div className="flex items-center justify-between px-4">
              <motion.h1
                className="text-2xl font-bold font-mono text-primary"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
              >
                <Link href="/dashboard">Taskify</Link>
              </motion.h1>
              <motion.button
                onClick={() => setSidebarOpen(false)}
                className="p-2 rounded-lg bg-destructive/10 text-destructive hover:bg-destructive/20 hover:text-destructive border border-destructive/20 hover:border-destructive/40 transition-all"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                aria-label="Close sidebar"
                title="Close sidebar"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </motion.button>
            </div>

            {/* User Profile Section - Mobile */}
            <motion.div
              className="px-4 mt-4 pb-4 border-b border-border/30"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <p className="text-sm font-semibold font-mono text-primary">Hello!</p>
              <p className="text-base font-bold font-mono text-foreground truncate">{userName}</p>
            </motion.div>

            <div className="mt-5 flex-1 flex flex-col overflow-y-auto">
              <nav className="flex-1 px-2 space-y-1">
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <Link
                    href="/dashboard"
                    className={`${
                      pathname === '/dashboard'
                        ? 'bg-primary text-primary-foreground shadow-lg'
                        : 'text-foreground hover:bg-primary/10 hover:text-primary'
                    } group flex items-center px-3 py-2 text-sm font-medium font-mono rounded-lg transition-all duration-200`}
                    onClick={() => setSidebarOpen(false)}
                  >
                    Dashboard
                  </Link>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.25 }}
                >
                  <Link
                    href="/dashboard/settings"
                    className={`${
                      pathname === '/dashboard/settings'
                        ? 'bg-primary text-primary-foreground shadow-lg'
                        : 'text-foreground hover:bg-primary/10 hover:text-primary'
                    } group flex items-center px-3 py-2 text-sm font-medium font-mono rounded-lg transition-all duration-200`}
                    onClick={() => setSidebarOpen(false)}
                  >
                    Settings
                  </Link>
                </motion.div>

                <motion.button
                  onClick={() => {
                    handleLogout();
                    setSidebarOpen(false);
                  }}
                  className="w-full text-left text-red-600 dark:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 group flex items-center gap-2 px-3 py-2 text-sm font-medium font-mono rounded-lg transition-all duration-200"
                  title="Logout"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                  whileHover={{ x: 5 }}
                >
                  <LogOutIcon className="h-4 w-4" />
                  Logout
                </motion.button>
              </nav>
            </div>
          </div>
        </motion.div>
      )}

      {/* Mobile header with hamburger */}
      <motion.div
        className="lg:hidden fixed top-0 left-0 right-0 z-30 bg-card border-b-2 border-primary/30"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
      >
        <div className="flex items-center justify-between h-14 xs:h-16 px-2 xs:px-4">
          {isAuthenticated ? (
            <>
              <motion.button
                type="button"
                className="hamburger-button inline-flex items-center justify-center rounded-lg bg-primary p-1.5 xs:p-2 text-primary-foreground hover:bg-primary-hover focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <span className="sr-only">Open sidebar</span>
                <svg
                  className="h-5 w-5 xs:h-6 xs:w-6"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </motion.button>
              <motion.div
                className="flex flex-col items-center min-w-0 flex-1 mx-2"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
              >
                <h1 className="text-base xs:text-lg sm:text-xl font-bold font-mono text-primary truncate max-w-full">
                  <Link href="/dashboard">Taskify</Link>
                </h1>
                <p className="text-[10px] xs:text-xs text-muted-foreground truncate max-w-full font-mono">Hello, {userName}!</p>
              </motion.div>
            </>
          ) : (
            <>
              <motion.h1
                className="text-base xs:text-lg sm:text-xl font-bold text-primary"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
              >
                <Link href="/">Taskify</Link>
              </motion.h1>
              <div className="flex-1"></div>
            </>
          )}
          <motion.div
            className="shrink-0"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15 }}
          >
            <ThemeToggle />
          </motion.div>
        </div>
      </motion.div>

      {/* Desktop header */}
      <motion.div
        className="hidden lg:block fixed top-0 left-0 right-0 z-30"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
      >
        <header className="glass-header">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-6">
              <motion.h1
                className="text-2xl font-bold font-mono text-primary"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Link href="/">Taskify</Link>
              </motion.h1>
              {/* User Profile Section - Desktop (only show when authenticated) */}
              {isAuthenticated && (
                <motion.div
                  className="flex items-center gap-2 pl-6 border-l border-border/30"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.15 }}
                >
                  <p className="text-base font-bold font-mono text-primary">Hello!</p>
                  <p className="text-base font-bold font-mono text-foreground">{userName}</p>
                </motion.div>
              )}
            </div>
            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                // Authenticated navigation
                <>
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                  >
                    <Link
                      href="/dashboard"
                      className={`px-4 py-2 text-sm font-medium font-mono rounded-lg transition-all duration-200 ${
                        pathname === '/dashboard'
                          ? 'bg-primary text-primary-foreground shadow-lg'
                          : 'text-foreground hover:bg-primary/10 hover:text-primary'
                      }`}
                    >
                      Dashboard
                    </Link>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.25 }}
                  >
                    <Link
                      href="/dashboard/settings"
                      className={`px-4 py-2 text-sm font-medium font-mono rounded-lg transition-all duration-200 ${
                        pathname === '/dashboard/settings'
                          ? 'bg-primary text-primary-foreground shadow-lg'
                          : 'text-foreground hover:bg-primary/10 hover:text-primary'
                      }`}
                    >
                      Settings
                    </Link>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                  >
                    <ThemeToggle />
                  </motion.div>

                  <motion.button
                    onClick={handleLogout}
                    className="p-2 text-red-600 dark:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 border border-red-600/20 dark:border-red-500/20 rounded-lg transition-all duration-200 group"
                    title="Logout"
                    aria-label="Logout"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.35 }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <LogOutIcon className="h-5 w-5" />
                  </motion.button>
                </>
              ) : (
                // Unauthenticated navigation
                <>
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                  >
                    <Link
                      href="/login"
                      className="px-4 py-2 text-sm font-medium font-mono text-foreground hover:text-primary transition-colors duration-200"
                    >
                      Sign In
                    </Link>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.25 }}
                  >
                    <Link
                      href="/signup"
                      className="px-6 py-2 text-sm font-bold font-mono text-primary-foreground bg-primary rounded-lg shadow-lg shadow-primary/30 hover:shadow-xl hover:shadow-primary/40 transition-all duration-200"
                    >
                      Get Started
                    </Link>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 }}
                  >
                    <ThemeToggle />
                  </motion.div>
                </>
              )}
            </div>
          </div>
        </header>
      </motion.div>

      {/* Add padding to page content to account for fixed navbar */}
      <div className="lg:pt-16 pt-14 xs:pt-16"></div>
    </>
  );
}
