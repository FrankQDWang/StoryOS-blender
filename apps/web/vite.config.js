import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({publicDir:'../../public',plugins:[react()],build:{outDir:'dist/client'},server:{host:'127.0.0.1',port:4173,strictPort:true}});
