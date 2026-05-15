const path = require("path");

/** @type {import('next').NextConfig} */
const nextConfig = {
  outputFileTracingRoot: path.resolve(__dirname),
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
      {
        source: "/health",
        destination: "http://localhost:8000/health",
      },
      {
        source: "/docs",
        destination: "http://localhost:8000/docs",
      },
      {
        source: "/openapi.json",
        destination: "http://localhost:8000/openapi.json",
      },
    ];
  },
};

module.exports = nextConfig;

