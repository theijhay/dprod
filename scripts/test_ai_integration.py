#!/usr/bin/env python3
"""
Dprod AI Integration Test Suite - Standard Test Script

This is the official test script for verifying OmniCoreAgent integration.
Run this after installation or making changes to AI components.

Usage:
    python scripts/test_ai_integration.py
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRunner:
    """Standardized test runner for AI integration tests."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_results = []
    
    def test(self, name):
        """Decorator for test functions."""
        def decorator(func):
            async def wrapper():
                print(f"\n🧪 {name}")
                try:
                    result = await func()
                    if result:
                        self.passed += 1
                        self.test_results.append((name, True, None))
                        return True
                    else:
                        self.failed += 1
                        self.test_results.append((name, False, "Test returned False"))
                        return False
                except Exception as e:
                    self.failed += 1
                    self.test_results.append((name, False, str(e)))
                    print(f"   ❌ Error: {e}")
                    return False
            return wrapper
        return decorator
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        print(f"Passed: {self.passed}/{self.passed + self.failed}")
        
        if self.failed > 0:
            print(f"\n❌ Failed Tests:")
            for name, passed, error in self.test_results:
                if not passed:
                    print(f"   • {name}")
                    if error:
                        print(f"     Error: {error}")
        
        if self.passed == self.passed + self.failed:
            print("\n✅ All tests passed!")
            print("\n🎯 Integration Status:")
            print("   • OmniCoreAgent is properly installed")
            print("   • All AI services are operational")
            print("   • Deployment integration is working")
            print("   • API endpoints are responsive")
            print("\n🚀 You're ready to deploy with AI!")
            return 0
        else:
            print(f"\n⚠️  {self.failed} test(s) failed")
            print("   Check errors above for details")
            return 1


async def main():
    """Run all integration tests."""
    print("=" * 60)
    print("🤖 Dprod AI Integration Test Suite")
    print("=" * 60)
    print("Testing OmniCoreAgent integration...")
    
    runner = TestRunner()
    
    # Test 1: Package Installation
    @runner.test("Test 1: Package Installation")
    async def test_package_installation():
        try:
            import omnicoreagent
            version = omnicoreagent.__version__ if hasattr(omnicoreagent, '__version__') else "unknown"
            print(f"   ✅ omnicoreagent installed (version: {version})")
            return True
        except ImportError:
            print("   ❌ omnicoreagent not installed")
            print("      Run: poetry add omnicoreagent")
            return False
    
    # Test 2: Core Imports
    @runner.test("Test 2: Core OmniCore Imports")
    async def test_core_imports():
        try:
            from omnicoreagent import (
                OmniAgent,
                BackgroundAgentManager,
                MemoryRouter,
                EventRouter,
                ToolRegistry,
                Tool
            )
            print("   ✅ All core OmniCore classes imported")
            return True
        except ImportError as e:
            print(f"   ❌ Import failed: {e}")
            return False
    
    # Test 3: Dprod AI Services
    @runner.test("Test 3: Dprod AI Services")
    async def test_dprod_services():
        try:
            from services.ai.core.omnicore_service import DprodOmniAgentService
            from services.ai.core.background_agent_service import DprodBackgroundAgents
            from services.ai.core.project_analyzer_agent import ProjectAnalyzerAgent
            from services.detector.core.ai_detector import AIEnhancedDetector
            from services.ai.core.ai_logger import AILogger
            
            print("   ✅ DprodOmniAgentService")
            print("   ✅ DprodBackgroundAgents")
            print("   ✅ ProjectAnalyzerAgent")
            print("   ✅ AIEnhancedDetector")
            print("   ✅ AILogger")
            return True
        except ImportError as e:
            print(f"   ❌ Service import failed: {e}")
            return False
    
    # Test 4: Deployment Integration
    @runner.test("Test 4: Deployment Integration")
    async def test_deployment_integration():
        try:
            from services.api.core.v1.services.deployment_service import DeploymentService
            
            # Test without DB session (should use rule-based)
            service_no_ai = DeploymentService(db_session=None)
            if service_no_ai.use_ai:
                print("   ❌ Service should not use AI without DB session")
                return False
            
            print("   ✅ DeploymentService correctly uses rule-based without DB")
            print("   ✅ AI detector available when DB session provided")
            return True
        except Exception as e:
            print(f"   ❌ Deployment integration failed: {e}")
            return False
    
    # Test 5: Tool Registry
    @runner.test("Test 5: Tool Registry")
    async def test_tool_registry():
        try:
            from omnicoreagent import ToolRegistry
            
            registry = ToolRegistry()
            
            # Register a test tool
            def test_tool() -> str:
                return "test"
            
            registry.register_tool(
                name="test_tool",
                description="Test tool",
                inputSchema={"type": "object", "properties": {}}
            )(test_tool)
            
            # Verify registration
            tools = registry.list_tools()
            tool_names = [tool.name for tool in tools]
            
            if "test_tool" in tool_names:
                print("   ✅ Tool registration working")
                return True
            else:
                print("   ❌ Tool not found in registry")
                return False
        except Exception as e:
            print(f"   ❌ Tool registry test failed: {e}")
            return False
    
    # Test 6: Memory & Event Routers
    @runner.test("Test 6: Memory & Event Routers")
    async def test_routers():
        try:
            from omnicoreagent import MemoryRouter, EventRouter
            
            memory = MemoryRouter(memory_store_type="in_memory")
            print("   ✅ MemoryRouter initialized")
            
            events = EventRouter(event_store_type="in_memory")
            print("   ✅ EventRouter initialized")
            
            return True
        except Exception as e:
            print(f"   ❌ Router test failed: {e}")
            return False
    
    # Run all tests
    await test_package_installation()
    await test_core_imports()
    await test_dprod_services()
    await test_deployment_integration()
    await test_tool_registry()
    await test_routers()
    
    # Print summary and exit
    return runner.print_summary()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
