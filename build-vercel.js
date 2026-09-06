const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('--- STARTING VERCEL BUILD SCRIPT ---');
console.log('Current working directory:', process.cwd());
console.log('Script directory:', __dirname);

let frontendDir = '';
if (fs.existsSync(path.resolve(__dirname, 'fraudlens-new-frontend', 'package.json'))) {
  frontendDir = path.resolve(__dirname, 'fraudlens-new-frontend');
} else if (fs.existsSync(path.resolve(__dirname, '..', 'fraudlens-new-frontend', 'package.json'))) {
  frontendDir = path.resolve(__dirname, '..', 'fraudlens-new-frontend');
} else if (fs.existsSync(path.resolve(__dirname, 'package.json')) && fs.existsSync(path.resolve(__dirname, 'src'))) {
  frontendDir = __dirname;
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
  if (!fs.existsSync(distDir)) {
    console.error('ERROR: Dist directory was not created at:', distDir);
    process.exit(1);
  }

  console.log('3. Dist directory successfully built at:', distDir);

  const targets = [
    path.resolve(__dirname, 'dist'),
    path.resolve(__dirname, '..', 'dist'),
    path.resolve(frontendDir, 'dist'),
    path.resolve(__dirname, 'module9_officer_console', 'dist'),
    path.resolve(__dirname, '..', 'module9_officer_console', 'dist'),
    path.resolve(__dirname, 'public'),
    path.resolve(__dirname, '..', 'public')
  ];

  for (const target of targets) {
    try {
      const parent = path.dirname(target);
      if (fs.existsSync(parent) && target !== distDir) {
        fs.cpSync(distDir, target, { recursive: true, force: true });
        console.log('Synced dist ->', target);
      }
    } catch (err) {
      console.warn('Could not sync to:', target, err.message);
    }
  }

  console.log('--- VERCEL BUILD SCRIPT COMPLETE ---');
} catch (err) {
  console.error('Build execution failed:', err);
  process.exit(1);
}
