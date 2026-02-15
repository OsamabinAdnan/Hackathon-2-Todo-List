'use client';

import { motion } from 'framer-motion';

export function BackgroundGlow() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {/* Primary glow orb - top left */}
      <motion.div
        className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] max-w-[500px] max-h-[500px] bg-primary/15 rounded-full blur-3xl"
        animate={{
          scale: [1, 1.2, 1],
          x: [0, 30, 0],
          y: [0, 20, 0],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />

      {/* Secondary glow orb - top right */}
      <motion.div
        className="absolute top-[20%] right-[-5%] w-[30vw] h-[30vw] max-w-[400px] max-h-[400px] bg-purple-500/10 rounded-full blur-3xl"
        animate={{
          scale: [1, 1.3, 1],
          x: [0, -40, 0],
          y: [0, -20, 0],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 1,
        }}
      />

      {/* Tertiary glow orb - bottom left */}
      <motion.div
        className="absolute bottom-[-10%] left-[20%] w-[35vw] h-[35vw] max-w-[450px] max-h-[450px] bg-indigo-500/10 rounded-full blur-3xl"
        animate={{
          scale: [1, 1.15, 1],
          x: [0, 50, 0],
          y: [0, 30, 0],
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 2,
        }}
      />

      {/* Quaternary glow orb - bottom right */}
      <motion.div
        className="absolute bottom-[10%] right-[10%] w-[25vw] h-[25vw] max-w-[350px] max-h-[350px] bg-pink-500/10 rounded-full blur-3xl"
        animate={{
          scale: [1, 1.25, 1],
          x: [0, -30, 0],
          y: [0, -25, 0],
        }}
        transition={{
          duration: 9,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 0.5,
        }}
      />

      {/* Subtle accent orb - center left */}
      <motion.div
        className="absolute top-1/2 left-[5%] w-[20vw] h-[20vw] max-w-[250px] max-h-[250px] bg-cyan-500/8 rounded-full blur-3xl"
        animate={{
          scale: [1, 1.1, 1],
          x: [0, 20, 0],
          y: [0, 15, 0],
        }}
        transition={{
          duration: 7,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 3,
        }}
      />

      {/* Subtle accent orb - center right */}
      <motion.div
        className="absolute top-[30%] right-[15%] w-[18vw] h-[18vw] max-w-[200px] max-h-[200px] bg-orange-500/8 rounded-full blur-3xl"
        animate={{
          scale: [1, 1.2, 1],
          x: [0, -25, 0],
          y: [0, 20, 0],
        }}
        transition={{
          duration: 11,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 1.5,
        }}
      />
    </div>
  );
}
