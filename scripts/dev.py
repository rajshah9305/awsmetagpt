#!/usr/bin/env python3
"""
Development server script with hot reloading
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


class DevServer:
    """Development server manager"""
    
    def __init__(self):
        self.processes = []
        self.running = True
    
    def start_backend(self):
        """Start backend server"""
        print("🐍 Starting backend server...")
        
        # Activate virtual environment and start server
        if os.name == 'nt':  # Windows
            cmd = ["venv\\Scripts\\python", "main_clean.py"]
        else:  # Unix/Linux/macOS
            cmd = ["venv/bin/python", "main_clean.py"]
        
        env = os.environ.copy()
        env["DEBUG"] = "true"
        env["LOG_LEVEL"] = "DEBUG"
        
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        self.processes.append(("Backend", process))
        
        # Stream output
        for line in iter(process.stdout.readline, ''):
            if not self.running:
                break
            print(f"[Backend] {line.rstrip()}")
    
    def start_frontend(self):
        """Start frontend development server"""
        print("⚛️ Starting frontend server...")
        
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        self.processes.append(("Frontend", process))
        
        # Stream output
        for line in iter(process.stdout.readline, ''):
            if not self.running:
                break
            print(f"[Frontend] {line.rstrip()}")
    
    def start_test_watcher(self):
        """Start test watcher"""
        print("🧪 Starting test watcher...")
        
        if os.name == 'nt':  # Windows
            cmd = ["venv\\Scripts\\python", "-m", "pytest", "tests/", "--tb=short", "-v"]
        else:  # Unix/Linux/macOS
            cmd = ["venv/bin/python", "-m", "pytest", "tests/", "--tb=short", "-v"]
        
        while self.running:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print("✅ All tests passed")
                else:
                    print("❌ Some tests failed:")
                    print(result.stdout)
                    print(result.stderr)
            except subprocess.TimeoutExpired:
                print("⏰ Tests timed out")
            except Exception as e:
                print(f"🚨 Test error: {e}")
            
            # Wait before running tests again
            time.sleep(10)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down development servers...")
        self.running = False
        
        for name, process in self.processes:
            print(f"Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Force killing {name}...")
                process.kill()
        
        sys.exit(0)
    
    def run(self, watch_tests=False):
        """Run development servers"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🚀 Starting development environment...")
        print("Press Ctrl+C to stop all servers")
        print("=" * 50)
        
        # Start servers in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self.start_backend),
                executor.submit(self.start_frontend)
            ]
            
            if watch_tests:
                futures.append(executor.submit(self.start_test_watcher))
            
            try:
                # Wait for all servers
                for future in futures:
                    future.result()
            except KeyboardInterrupt:
                self.signal_handler(signal.SIGINT, None)


def check_prerequisites():
    """Check if prerequisites are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    if not Path("venv").exists():
        print("❌ Virtual environment not found. Run 'python scripts/setup.py' first")
        return False
    
    # Check Node.js
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js not found. Please install Node.js 16+")
        return False
    
    # Check npm dependencies
    if not Path("node_modules").exists():
        print("❌ Node modules not found. Run 'npm install'")
        return False
    
    # Check .env file
    if not Path(".env").exists():
        print("❌ .env file not found. Run 'python scripts/setup.py' first")
        return False
    
    print("✅ All prerequisites met")
    return True


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Development server for MetaGPT + E2B system")
    parser.add_argument("--watch-tests", action="store_true", help="Enable test watcher")
    parser.add_argument("--setup", action="store_true", help="Run setup first")
    
    args = parser.parse_args()
    
    if args.setup:
        print("🔧 Running setup...")
        setup_result = subprocess.run([sys.executable, "scripts/setup.py"])
        if setup_result.returncode != 0:
            print("❌ Setup failed")
            sys.exit(1)
    
    if not check_prerequisites():
        print("\n💡 Run 'python scripts/setup.py' to set up the environment")
        sys.exit(1)
    
    # Start development server
    dev_server = DevServer()
    dev_server.run(watch_tests=args.watch_tests)


if __name__ == "__main__":
    main()