'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { CheckCircle2, Repeat, Tag, Moon, ArrowRight, Sparkles } from 'lucide-react';

// Register GSAP plugins
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

export default function HomePage() {
  const heroRef = useRef<HTMLDivElement>(null);
  const statsRef = useRef<HTMLDivElement>(null);
  const featuresRef = useRef<HTMLDivElement>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  // GSAP: Hero Timeline Animation
  useEffect(() => {
    if (!isClient || !heroRef.current) return;

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

      tl.from('.hero-title', {
        opacity: 0,
        y: 30,
        duration: 0.8,
        stagger: 0.2,
      })
        .from('.hero-subtitle', {
          opacity: 0,
          y: 20,
          duration: 0.6,
        }, '-=0.4')
        .from('.hero-buttons', {
          opacity: 0,
          y: 20,
          duration: 0.6,
        }, '-=0.3');
    }, heroRef);

    return () => ctx.revert();
  }, [isClient]);

  // GSAP: Stats Counter Animation
  useEffect(() => {
    if (!isClient || !statsRef.current) return;

    const ctx = gsap.context(() => {
      gsap.from('.stat-number', {
        textContent: 0,
        duration: 2,
        ease: 'power1.inOut',
        snap: { textContent: 1 },
        scrollTrigger: {
          trigger: statsRef.current,
          start: 'top 80%',
          toggleActions: 'play none none none',
        },
        stagger: 0.2,
      });
    }, statsRef);

    return () => ctx.revert();
  }, [isClient]);

  // GSAP: Feature Cards Scroll Animation with Stagger
  useEffect(() => {
    if (!isClient || !featuresRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo('.feature-card',
        {
          opacity: 0,
          y: 60,
        },
        {
          opacity: 1,
          y: 0,
          duration: 0.8,
          stagger: 0.15,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: featuresRef.current,
            start: 'top 75%',
            toggleActions: 'play none none none',
          },
        }
      );
    }, featuresRef);

    return () => ctx.revert();
  }, [isClient]);

  const features = [
    {
      icon: CheckCircle2,
      title: 'Task Management',
      description: 'Create, organize, and track your tasks with an intuitive interface',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: Repeat,
      title: 'Recurring Tasks',
      description: 'Set up daily, weekly, or monthly recurring tasks automatically',
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: Tag,
      title: 'Priority Tags',
      description: 'Organize tasks with priority levels and custom tags',
      color: 'from-orange-500 to-red-500',
    },
    {
      icon: Moon,
      title: 'Dark Mode',
      description: 'Beautiful dark mode for comfortable work at any time',
      color: 'from-indigo-500 to-purple-500',
    },
  ];

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950 overflow-hidden">

      {/* Hero Section */}
      <section ref={heroRef} className="relative min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 pt-20">
        {/* Animated Background Blobs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <motion.div
            className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.2, 1],
              x: [0, 50, 0],
              y: [0, 30, 0],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
          <motion.div
            className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.3, 1],
              x: [0, -50, 0],
              y: [0, -30, 0],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        </div>

        <div className="relative z-10 max-w-5xl mx-auto text-center">
          {/* Title */}
          <h1 className="hero-title text-5xl xs:text-6xl sm:text-7xl lg:text-8xl font-black text-foreground mb-6 leading-tight pt-8">
            <span className="hero-title bg-clip-text text-transparent bg-linear-to-r from-primary via-purple-600 to-pink-600">
              Taskify
            </span>
          </h1>

          <p className="hero-subtitle text-xl xs:text-2xl sm:text-3xl text-muted-foreground mb-4 font-medium">
            Your Smart Task Management Solution
          </p>

          <p className="hero-subtitle text-base xs:text-lg text-muted-foreground mb-12 max-w-2xl mx-auto">
            Organize your life with powerful features like recurring tasks, priority tags, and beautiful dark mode
          </p>

          {/* CTA Buttons */}
          <div className="hero-buttons flex flex-col sm:flex-row gap-4 justify-center items-center">
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Link
                href="/signup"
                className="inline-flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-xl font-bold text-lg shadow-lg shadow-primary/30 hover:shadow-xl hover:shadow-primary/40 transition-all duration-300"
              >
                Get Started Free
                <ArrowRight className="h-5 w-5" />
              </Link>
            </motion.div>

            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 px-8 py-4 glass-card rounded-xl font-bold text-lg hover:bg-card/60 transition-all duration-300"
              >
                Sign In
              </Link>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section ref={statsRef} className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
            {[
              { value: 10000, label: 'Active Users', suffix: '+' },
              { value: 50000, label: 'Tasks Completed', suffix: '+' },
              { value: 99, label: 'User Satisfaction', suffix: '%' },
            ].map((stat, index) => (
              <motion.div
                key={index}
                className="glass-card p-8 rounded-2xl text-center shadow-lg shadow-primary/10"
                whileHover={{ scale: 1.05, boxShadow: '0 20px 60px rgba(74, 90, 184, 0.2)' }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              >
                <div className="text-5xl font-black text-primary mb-2">
                  <span className="stat-number">{stat.value}</span>
                  {stat.suffix}
                </div>
                <div className="text-sm text-muted-foreground font-medium">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section ref={featuresRef} className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <motion.h2
              className="text-4xl sm:text-5xl font-black text-foreground mb-4"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              Powerful Features
            </motion.h2>
            <motion.p
              className="text-lg text-muted-foreground max-w-2xl mx-auto"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              Everything you need to stay organized and productive
            </motion.p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  className="feature-card glass-card p-8 rounded-2xl shadow-lg shadow-primary/10 hover:shadow-xl hover:shadow-primary/20 transition-all duration-300"
                  whileHover={{ y: -8 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                >
                  <div className={`inline-flex p-4 rounded-xl bg-linear-to-br ${feature.color} mb-6`}>
                    <Icon className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-foreground mb-3">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <motion.div
          className="max-w-4xl mx-auto glass-card p-12 rounded-3xl text-center shadow-2xl shadow-primary/20"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-4xl sm:text-5xl font-black text-foreground mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of users who are already managing their tasks more efficiently with Taskify
          </p>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 px-10 py-5 bg-primary text-primary-foreground rounded-xl font-bold text-xl shadow-lg shadow-primary/30 hover:shadow-xl hover:shadow-primary/40 transition-all duration-300"
            >
              Create Free Account
              <ArrowRight className="h-6 w-6" />
            </Link>
          </motion.div>
        </motion.div>
      </section>

    </div>
  );
}
