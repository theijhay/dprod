#!/usr/bin/env python3
"""Test OmniCoreAgent integration with dprod."""

import os
import sys
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_imports():
    """Test that all OmniCore modules can be imported."""
    print("🧪 Testing OmniCore imports...")
    
    try:
        from omnicoreagent import (
            OmniAgent,
            BackgroundAgentManager,
            BackgroundOmniAgent,
            MemoryRouter,
            EventRouter,
            ToolRegistry,
            Tool
        )
        print("✅ All OmniCore modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

async def test_dprod_services():
    """Test that dprod AI services can be imported."""
    print("\n🧪 Testing dprod AI services...")
    
    try:
        from services.ai.core.omnicore_service import DprodOmniAgentService
        from services.ai.core.background_agent_service import DprodBackgroundAgents
        print("✅ All dprod AI services imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

async def test_tool_registry():
    """Test creating and registering tools."""
    print("\n🧪 Testing ToolRegistry...")
    
    try:
        from omnicoreagent import ToolRegistry
        
        registry = ToolRegistry()
        
        # Register a simple test tool
        def test_tool() -> str:
            """A simple test tool."""
            return "Hello from test tool!"
        
        registry.register_tool(
            name="test_tool",
            description="A simple test tool",
            inputSchema={"type": "object", "properties": {}}
        )(test_tool)
        
        # Verify it was registered
        tools = registry.list_tools()
        tool_names = [tool.name for tool in tools]
        if "test_tool" in tool_names:
            print(f"✅ Tool registered successfully: {tool_names}")
            return True
        else:
            print(f"❌ Tool not found in registry: {tool_names}")
            return False
            
    except Exception as e:
        print(f"❌ Tool registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_memory_router():
    """Test MemoryRouter initialization."""
    print("\n🧪 Testing MemoryRouter...")
    
    try:
        from omnicoreagent import MemoryRouter
        
        # Test in-memory storage
        memory = MemoryRouter(memory_store_type="in_memory")
        print("✅ MemoryRouter initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ MemoryRouter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_event_router():
    """Test EventRouter initialization."""
    print("\n🧪 Testing EventRouter...")
    
    try:
        from omnicoreagent import EventRouter
        
        # Test in-memory event store
        events = EventRouter(event_store_type="in_memory")
        print("✅ EventRouter initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ EventRouter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_background_agent_manager():
    """Test BackgroundAgentManager initialization."""
    print("\n🧪 Testing BackgroundAgentManager...")
    
    try:
        from omnicoreagent import BackgroundAgentManager, MemoryRouter, EventRouter
        
        memory = MemoryRouter(memory_store_type="in_memory")
        events = EventRouter(event_store_type="in_memory")
        
        manager = BackgroundAgentManager(memory, events)
        await manager.start()
        
        print("✅ BackgroundAgentManager initialized and started successfully")
        
        # Clean up
        await manager.shutdown()
        print("✅ BackgroundAgentManager shut down successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ BackgroundAgentManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("=" * 60)
    print("🤖 OmniCoreAgent Integration Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(await test_imports())
    results.append(await test_dprod_services())
    results.append(await test_tool_registry())
    results.append(await test_memory_router())
    results.append(await test_event_router())
    results.append(await test_background_agent_manager())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
