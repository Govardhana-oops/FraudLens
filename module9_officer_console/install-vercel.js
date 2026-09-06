const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('--- STARTING VERCEL INSTALL SCRIPT (MODULE9) ---');

let frontendDir = '';
if (fs.existsSync(path.resolve(__dirname, '..', 'fraudlens-new-frontend', 'package.json'))) {
  frontendDir = path.resolve(__dirname, '..', 'fraudlens-new-frontend');
} else if (fs.existsSync(path.resolve(__dirname, 'fraudlens-new-frontend', 'package.json'))) {
  frontendDir = path.resolve(__dirname, 'fraudlens-new-frontend');
}

if (frontendDir) {
  console.log('Installing dependencies in:', frontendDir);
  execSync('npm install', { cwd: frontendDir, stdio: 'inherit' });
} else {
  console.log('Installing dependencies in current directory');
  execSync('npm install', { stdio: 'inherit' });
}
console.log('--- VERCEL INSTALL SCRIPT COMPLETE ---');
