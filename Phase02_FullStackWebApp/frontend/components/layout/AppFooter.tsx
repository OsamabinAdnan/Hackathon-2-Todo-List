'use client';

import { Github, Linkedin, Twitter } from 'lucide-react';

export function AppFooter() {

  const socialLinks = [
    {
      icon: Linkedin,
      url: 'https://www.linkedin.com/in/osama-bin-adnan/',
      label: 'LinkedIn',
      color: 'hover:text-blue-600 dark:hover:text-blue-400',
      bgColor: 'hover:bg-blue-50 dark:hover:bg-blue-950/30',
    },
    {
      icon: Github,
      url: 'https://github.com/OsamabinAdnan',
      label: 'GitHub',
      color: 'hover:text-gray-800 dark:hover:text-white',
      bgColor: 'hover:bg-gray-100 dark:hover:bg-gray-800',
    },
    {
      icon: Twitter,
      url: 'https://x.com/osamabinadnan1',
      label: 'X (Twitter)',
      color: 'hover:text-blue-400 dark:hover:text-blue-300',
      bgColor: 'hover:bg-blue-50 dark:hover:bg-blue-950/30',
    },
  ];

  return (
    <footer className="mt-auto border-t border-gray-200 dark:border-gray-800 bg-white/30 dark:bg-gray-950/50 backdrop-blur-sm transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Brand Section */}
          <div>
            <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-linear-to-r from-primary to-purple-600 mb-3">
              Taskify
            </h3>
            <p className="text-sm leading-relaxed text-gray-600 dark:text-gray-400">
              A powerful multi-user task management application with advanced features for organizing your work efficiently.
            </p>
          </div>

          {/* Links Section */}
          <div>
            <h4 className="font-semibold mb-4 text-gray-900 dark:text-gray-200">
              Quick Links
            </h4>
            <ul className="space-y-2">
              {[
                { href: '/', label: 'Home' },
                { href: '/login', label: 'Sign In' },
                { href: '/signup', label: 'Sign Up' },
              ].map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-sm transition-colors duration-200 inline-block text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-primary"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Social Links Section */}
          <div>
            <h4 className="font-semibold mb-4 text-gray-900 dark:text-gray-200">
              Connect With Me
            </h4>
            <div className="flex gap-4">
              {socialLinks.map((social) => {
                const Icon = social.icon;
                return (
                  <a
                    key={social.label}
                    href={social.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`p-3 rounded-lg transition-all duration-200 bg-gray-100/50 text-gray-600 dark:bg-gray-800/50 dark:text-gray-400 ${social.color} ${social.bgColor} hover:scale-110`}
                    title={social.label}
                    aria-label={social.label}
                  >
                    <Icon className="h-5 w-5" />
                  </a>
                );
              })}
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="h-px mb-6 bg-gray-200 dark:bg-gray-800" />

        {/* Bottom Section */}
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-sm text-gray-600 dark:text-gray-500">
            © 2024 Taskify. All rights reserved.
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-500">
            Built by <span className="font-semibold text-primary">Osama Bin Adnan</span>
          </p>
        </div>
      </div>
    </footer>
  );
}
