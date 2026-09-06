const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('--- STARTING VERCEL BUILD SCRIPT (MODULE9) ---');
console.log('Current working directory:', process.cwd());
console.log('Script directory:', __dirname);

let frontendDir = '';
if (fs.existsSync(path.resolve(__dirname, '..', 'fraudlens-new-frontend', 'package.json'))) {
  frontendDir = path.resolve(__dirname, '..', 'fraudlens-new-frontend');
} else if (fs.existsSync(path.resolve(__dirname, 'fraudlens-new-frontend', 'package.json'))) {
  frontendDir = path.resolve(__dirname, 'fraudlens-new-frontend');
}

if (!frontendDir) {
  console.error('ERROR: Could not locate fraudlens-new-frontend directory!');
  process.exit(1);
}

console.log('Found frontend directory:', frontendDir);

try {
  console.log('1. Running npm install in frontend directory...');
  execSync('npm install', { cwd: frontendDir, stdio: 'inherit' });

  console.log('2. Running npm run build in frontend directory...');
  execSync('npm run build', { cwd: frontendDir, stdio: 'inherit' });

  const distDir = path.resolve(frontendDir, 'dist');
  console.log('3. Dist directory successfully built at:', distDir);

  const targets = [
    path.resolve(__dirname, 'dist'),
    path.resolve(__dirname, '..', 'dist'),
    path.resolve(__dirname)
  ];

  for (const target of targets) {
    try {
      fs.cpSync(distDir, target, { recursive: true, force: true });
      console.log('Synced dist ->', target);
    } catch (err) {
      console.warn('Could not sync to:', target, err.message);
    }
  }

  console.log('--- VERCEL BUILD SCRIPT COMPLETE ---');
} catch (err) {
  console.error('Build execution failed:', err);
  process.exit(1);
}
