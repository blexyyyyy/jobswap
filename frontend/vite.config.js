import { resolve } from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
    root: '.',             // Root relative to frontend/
    base: '/',             // Base public path
    server: {
        port: 3000,
        open: true,
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
                secure: false,
            },
        },
    },
    build: {
        outDir: 'dist',
        rollupOptions: {
            input: {
                main: resolve(__dirname, 'index.html'),
                login: resolve(__dirname, 'login.html'),
                profile: resolve(__dirname, 'profile.html'),
                dashboard: resolve(__dirname, 'dashboard.html'),
                applied: resolve(__dirname, 'applied.html'),
            },
        },
    },
});
