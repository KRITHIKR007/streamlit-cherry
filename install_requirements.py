import subprocess
import sys
import os

def install_requirements():
    try:
        print("⏳ Updating pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
        
        if not os.path.exists(requirements_path):
            print("❌ requirements.txt not found!")
            return False
            
        print("⏳ Installing requirements...")
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "-r", 
            requirements_path
        ])
        
        print("✅ Installation complete!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during installation: {e}")
        return False

if __name__ == "__main__":
    try:
        success = install_requirements()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
