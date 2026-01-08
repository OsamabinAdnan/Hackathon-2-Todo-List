import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig(async () => {
  const { default: react } = await import('@vitejs/plugin-react');

  return {
    plugins: [react()],
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['__tests__/setup.ts'],
      coverage: {
        provider: 'v8',
        reporter: ['text', 'html', 'lcov'],
        exclude: ['node_modules/', '__tests__/', '.next/', 'out/', '*.config.*'],
        thresholds: {
          lines: 70,
          functions: 70,
          branches: 70,
          statements: 70,
        },
      },
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './'),
      },
    },
  };
});
