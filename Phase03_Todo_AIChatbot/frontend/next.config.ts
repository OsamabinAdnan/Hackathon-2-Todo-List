import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  serverExternalPackages: ["vitest"],
  typescript: {
    ignoreBuildErrors: true, // Temporarily ignore build errors during build
  },
};

export default nextConfig;
