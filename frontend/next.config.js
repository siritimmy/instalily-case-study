/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.partselect.com",
      },
    ],
  },
};

module.exports = nextConfig;
