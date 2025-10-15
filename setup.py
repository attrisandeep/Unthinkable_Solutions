#!/usr/bin/env python
"""
Quick setup script for KnowledgeExplorer backend
"""

import os
import sys
from pathlib import Path


def main():
    print("🚀 KnowledgeExplorer Backend Setup\n")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Create .env if it doesn't exist
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_path.exists() and env_example_path.exists():
        print("\n📝 Creating .env file from .env.example...")
        env_path.write_text(env_example_path.read_text())
        print("✅ Created .env file")
        print("⚠️  Please edit .env and add your API keys!")
    elif env_path.exists():
        print("\n✅ .env file already exists")
    else:
        print("\n⚠️  .env.example not found")
    
    # Create uploads directory
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    print(f"\n✅ Created uploads directory: {uploads_dir.absolute()}")
    
    # Check if dependencies are installed
    print("\n📦 Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn installed")
    except ImportError:
        print("❌ Dependencies not installed")
        print("\nRun: pip install -r requirements.txt")
        return
    
    # Summary
    print("\n" + "="*60)
    print("✨ Setup Complete!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Edit .env and add your API keys:")
    print("   - GROQ_API_KEY")
    print("   - PINECONE_API_KEY")
    print("   - JINA_API_KEY (optional)")
    print("\n2. Start the server:")
    print("   python main.py")
    print("\n3. Test the API:")
    print("   http://localhost:8000/health")
    print("\n4. Read the docs:")
    print("   - BACKEND_README.md")
    print("   - frontend-integration.md")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
