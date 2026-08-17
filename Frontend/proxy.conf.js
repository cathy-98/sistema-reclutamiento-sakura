const target = process.env.SAKURA_API_TARGET || 'http://localhost:8000';

module.exports = {
  '/api': {
    // Proxy interno: desarrollo local usa localhost:8000.
    // Docker sobreescribe SAKURA_API_TARGET=http://backend:8000 desde docker-compose.yml.
    target,
    secure: false,
    changeOrigin: true,
    logLevel: 'debug',
    pathRewrite: {
      '^/api': '',
    },
  },
};
