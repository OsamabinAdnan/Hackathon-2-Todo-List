'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AnimatedCard, AnimatedPage } from '@/components/ui/animate';

const toastSuccessClassNames = {
  toast: 'glass-toast-success font-mono',
  title: 'glass-toast-title font-mono',
  description: 'glass-toast-description font-mono',
};

const toastErrorClassNames = {
  toast: 'glass-toast-error font-mono',
  title: 'glass-toast-title font-mono',
  description: 'glass-toast-description font-mono',
};

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  useEffect(() => {
    // Check if user is already signed in
    const token = localStorage.getItem('token');
    if (token) {
      router.push('/already-signed-in');
    } else {
      setIsCheckingAuth(false);
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      // Call FastAPI login endpoint directly
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        const errorMessage = data.detail || 'Login failed';
        setError(errorMessage);
        toast.error('Login Failed', {
          description: errorMessage,
          unstyled: true,
          classNames: toastErrorClassNames,
        });
        return;
      }

      // Store user data and JWT token
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Dispatch custom auth event to update navbar
      window.dispatchEvent(new CustomEvent('auth-change', {
        detail: {
          type: 'LOGIN',
          user: data.user
        }
      }));

      toast.success('Welcome Back!', {
        description: `Good to see you again, ${data.user.name}!`,
        duration: 5000,
        unstyled: true,
        classNames: toastSuccessClassNames,
      });

      setTimeout(() => {
        router.push('/dashboard');
      }, 1500);

    } catch (err: any) {
      const errorMessage = err.message || 'An error occurred during login';
      setError(errorMessage);
      toast.error('Login Failed', {
        description: errorMessage,
        unstyled: true,
        classNames: toastErrorClassNames,
      });
      console.error('Login error:', err);
    }
  };

  if (isCheckingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Checking authentication...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950 flex flex-col">
      {/* Main Content */}
      <AnimatedPage>
        <div className="min-h-screen flex items-center justify-center p-3 xs:p-4">
          <AnimatedCard delay={0.1} className="w-full max-w-md glass-card p-4 xs:p-6 sm:p-8">
            <div className="text-center mb-4 xs:mb-6">
              <h1 className="text-3xl xs:text-4xl font-bold font-mono text-primary mb-1 xs:mb-2">Taskify</h1>
              <h2 className="text-xl xs:text-2xl font-semibold font-mono text-foreground">Welcome Back</h2>
              <p className="text-sm font-mono text-muted-foreground mt-1">Sign in to your account</p>
            </div>

            {error && (
              <div className="mb-3 p-2.5 bg-destructive/20 text-destructive rounded-lg text-xs xs:text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4 xs:space-y-5">
              <div>
                <Label htmlFor="email" className="text-sm font-mono text-foreground">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="mt-1 bg-background/50 border-border/50 text-foreground font-mono rounded-lg py-2 px-3 w-full focus:ring-2 focus:ring-primary text-sm placeholder:font-mono"
                  placeholder="your@email.com"
                />
              </div>

              <div className="relative">
                <Label htmlFor="password" className="text-sm font-mono text-foreground">Password</Label>
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="mt-1 bg-background/50 border-border/50 text-foreground font-mono rounded-lg py-2 px-3 w-full focus:ring-2 focus:ring-primary text-sm pr-10 placeholder:font-mono"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 mt-3 text-muted-foreground hover:text-foreground transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>

              <Button
                type="submit"
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90 py-2 px-4 rounded-lg transition-all duration-200 text-sm font-bold font-mono"
              >
                Sign In
              </Button>
            </form>

            <div className="mt-4 xs:mt-6 text-center">
              <p className="text-xs xs:text-sm font-mono text-muted-foreground">
                Don&apos;t have an account?{' '}
                <Link href="/signup" className="text-primary hover:underline font-bold font-mono">
                  Sign up
                </Link>
              </p>
            </div>
          </AnimatedCard>
        </div>
      </AnimatedPage>
    </div>
  );
}
