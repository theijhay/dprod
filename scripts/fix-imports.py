#!/usr/bin/env python3
"""Script to fix import paths after restructuring."""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix import paths in a single file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix relative imports
    # from ..database -> from ...db.database
    content = re.sub(r'from \.\.database', 'from ...db.database', content)
    content = re.sub(r'from \.\.auth', 'from ...auth', content)
    content = re.sub(r'from \.\.routes', 'from ...v1.routes', content)
    content = re.sub(r'from \.\.services', 'from ...v1.services', content)
    
    # Fix other common patterns
    content = re.sub(r'from \.\.config', 'from ...utils.config', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed imports in {file_path}")

def main():
    """Fix all import paths in the services directory."""
    services_dir = Path("services")
    
    for py_file in services_dir.rglob("*.py"):
        if py_file.is_file():
            try:
                fix_imports_in_file(py_file)
            except Exception as e:
                print(f"❌ Error fixing {py_file}: {e}")

if __name__ == "__main__":
    main()
