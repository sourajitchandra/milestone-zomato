/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow requests to the Railway backend during SSR / API routes
  async rewrites() {
    return [];
  },
};

module.exports = nextConfig;
