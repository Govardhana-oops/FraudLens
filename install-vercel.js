const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('--- STARTING VERCEL INSTALL SCRIPT ---');
console.log('Current working directory:', process.cwd());

let frontendDir = '';
if (fs.existsSync(path.resolve(__dirname, 'fraudlens-new-frontend', 'package.json'))) {
  frontendDir = path.resolve(__dirname, 'fraudlens-new-frontend');
} else if (fs.existsSync(path.resolve(__dirname, '..', 'fraudlens-new-frontend', 'package.json'))) {
  frontendDir = path.resolve(__dirname, '..', 'fraudlens-new-frontend');
} else if (fs.existsSync(path.resolve(__dirname, 'package.json')) && fs.existsSync(path.resolve(__dirname, 'src'))) {
  frontendDir = __dirname;
}

if (frontendDir) {
  console.log('Installing dependencies in:', frontendDir);
  execSync('npm install', { cwd: frontendDir, stdio: 'inherit' });
} else {
  console.log('Installing dependencies in current directory');
  execSync('npm install', { stdio: 'inherit' });
}
console.log('--- VERCEL INSTALL SCRIPT COMPLETE ---');
