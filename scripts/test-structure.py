#!/usr/bin/env python3
"""Simple test to verify the new structure works."""

import os
import sys
from pathlib import Path

def test_structure():
    """Test that the new structure is in place."""
    print("🧪 Testing Dprod Structure...")
    
    # Test that services directory exists
    services_dir = Path("services")
    if not services_dir.exists():
        print("❌ services/ directory not found")
        return False
    print("✅ services/ directory exists")
    
    # Test that tools directory exists
    tools_dir = Path("tools")
    if not tools_dir.exists():
        print("❌ tools/ directory not found")
        return False
    print("✅ tools/ directory exists")
    
    # Test that examples directory exists
    examples_dir = Path("examples")
    if not examples_dir.exists():
        print("❌ examples/ directory not found")
        return False
    print("✅ examples/ directory exists")
    
    # Test service structure
    expected_services = ["api", "orchestrator", "detector", "shared"]
    for service in expected_services:
        service_path = services_dir / service
        if not service_path.exists():
            print(f"❌ services/{service}/ not found")
            return False
        print(f"✅ services/{service}/ exists")
        
        # Test core directory
        core_path = service_path / "core"
        if not core_path.exists():
            print(f"❌ services/{service}/core/ not found")
            return False
        print(f"✅ services/{service}/core/ exists")
    
    # Test tools structure
    expected_tools = ["cli", "frontend"]
    for tool in expected_tools:
        tool_path = tools_dir / tool
        if not tool_path.exists():
            print(f"❌ tools/{tool}/ not found")
            return False
        print(f"✅ tools/{tool}/ exists")
    
    # Test examples structure
    expected_examples = ["nodejs", "python", "go", "static"]
    for example in expected_examples:
        example_path = examples_dir / example
        if not example_path.exists():
            print(f"❌ examples/{example}/ not found")
            return False
        print(f"✅ examples/{example}/ exists")
    
    # Test that old packages directory is gone
    packages_dir = Path("packages")
    if packages_dir.exists():
        print("❌ Old packages/ directory still exists")
        return False
    print("✅ Old packages/ directory removed")
    
    # Test CLI structure
    cli_src = tools_dir / "cli" / "src"
    if not cli_src.exists():
        print("❌ tools/cli/src/ not found")
        return False
    print("✅ tools/cli/src/ exists")
    
    # Test CLI binary
    cli_bin = tools_dir / "cli" / "bin" / "dprod"
    if not cli_bin.exists():
        print("❌ tools/cli/bin/dprod not found")
        return False
    print("✅ tools/cli/bin/dprod exists")
    
    print("\n🎉 All structure tests passed!")
    print("\n📋 New Structure Summary:")
    print("  • services/ - Backend services (api, orchestrator, detector, shared)")
    print("  • tools/ - Development tools (cli, frontend)")
    print("  • examples/ - Example projects for testing")
    print("  • core/ - Main business logic (replaced src/)")
    print("  • Purpose-based organization - Clear separation of concerns")
    
    return True

if __name__ == "__main__":
    success = test_structure()
    sys.exit(0 if success else 1)
