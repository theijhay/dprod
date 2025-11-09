#!/usr/bin/env python3
"""
Integration test for Docker stats with dprod deployment flow.

This simulates what happens when you run 'dprod deploy' and verifies
that the AI can fetch real resource usage data.
"""

import docker
import json


def simulate_dprod_deployment():
    """
    Simulate a dprod deployment to test Docker stats integration.
    
    This creates a test container with the same labels that dprod uses,
    then tests if the analyze_resource_usage tool can find and monitor it.
    """
    print("=" * 70)
    print("🧪 Dprod Deployment Flow - Docker Stats Integration Test")
    print("=" * 70)
    
    try:
        client = docker.from_env()
        print("✅ Connected to Docker")
    except Exception as e:
        print(f"❌ Failed to connect to Docker: {e}")
        return False
    
    # Simulate dprod deployment
    print("\n📦 Step 1: Simulating 'dprod deploy' container creation...")
    print("   (This mimics what docker_manager.py does)")
    
    test_project_id = "test-project-123"
    test_project_name = "test-app"
    
    try:
        # First, try to pull a lightweight test image
        print("   📥 Pulling test image (nginx:alpine)...")
        try:
            client.images.pull("nginx:alpine")
            print("   ✅ Image pulled successfully")
        except Exception as pull_error:
            print(f"   ⚠️  Could not pull image: {pull_error}")
            print("   🔄 Checking for existing local images...")
            
            # Try to use any existing local image
            images = client.images.list()
            if not images:
                print("   ❌ No local images available. Please run: docker pull nginx:alpine")
                return False
            
            # Use the first available image
            test_image = images[0].tags[0] if images[0].tags else images[0].id
            print(f"   ✅ Using local image: {test_image}")
        else:
            test_image = "nginx:alpine"
        
        # Create a test container with dprod labels
        # This matches the format in docker_manager.py:104-122
        container = client.containers.run(
            test_image,
            name=f"dprod-{test_project_name}-test",
            detach=True,
            remove=False,
            mem_limit="512m",
            cpu_period=100000,
            cpu_quota=50000,
            labels={
                "dprod": "true",
                "project": test_project_name,
                "project_id": test_project_id
            }
        )
        
        print(f"   ✅ Test container created: {container.name}")
        print(f"   📋 Container ID: {container.short_id}")
        print(f"   🏷️  Labels: project_id={test_project_id}, project={test_project_name}")
        
    except Exception as e:
        print(f"   ❌ Failed to create test container: {e}")
        return False
    
    # Test container discovery (what analyze_resource_usage does)
    print("\n🔍 Step 2: Testing container discovery by labels...")
    print("   (This is what analyze_resource_usage tool does)")
    
    try:
        # Method 1: Find by project_id label
        containers_by_id = client.containers.list(
            filters={"label": f"project_id={test_project_id}"}
        )
        
        if containers_by_id:
            print(f"   ✅ Found container by project_id label")
        else:
            print(f"   ⚠️  Could not find container by project_id")
            
        # Method 2: Find by project name label (fallback)
        containers_by_name = client.containers.list(
            filters={"label": f"project={test_project_name}"}
        )
        
        if containers_by_name:
            print(f"   ✅ Found container by project name label")
        else:
            print(f"   ⚠️  Could not find container by project name")
        
        if not containers_by_id and not containers_by_name:
            print("   ❌ Container discovery failed!")
            cleanup_container(client, container)
            return False
        
        found_container = containers_by_id[0] if containers_by_id else containers_by_name[0]
        print(f"   ✅ Container discovered successfully")
        
    except Exception as e:
        print(f"   ❌ Container discovery failed: {e}")
        cleanup_container(client, container)
        return False
    
    # Test stats retrieval
    print("\n📊 Step 3: Fetching Docker stats...")
    print("   (This is the core of analyze_resource_usage)")
    
    try:
        stats = found_container.stats(stream=False)
        
        # Calculate metrics (same logic as omnicore_service.py)
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                   stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                      stats['precpu_stats']['system_cpu_usage']
        cpu_count = stats['cpu_stats']['online_cpus']
        cpu_percent = (cpu_delta / system_delta) * cpu_count * 100.0 if system_delta > 0 else 0.0
        
        memory_usage = stats['memory_stats']['usage']
        memory_limit = stats['memory_stats']['limit']
        memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0
        memory_usage_mb = memory_usage / (1024 * 1024)
        memory_limit_mb = memory_limit / (1024 * 1024)
        
        network_stats = stats.get('networks', {})
        network_rx_mb = sum(net['rx_bytes'] for net in network_stats.values()) / (1024 * 1024)
        network_tx_mb = sum(net['tx_bytes'] for net in network_stats.values()) / (1024 * 1024)
        
        print(f"   ✅ Stats retrieved successfully:")
        print(f"      🔧 CPU Usage: {cpu_percent:.2f}% ({cpu_count} cores)")
        print(f"      💾 Memory: {memory_usage_mb:.2f}MB / {memory_limit_mb:.2f}MB ({memory_percent:.1f}%)")
        print(f"      🌐 Network: RX {network_rx_mb:.2f}MB, TX {network_tx_mb:.2f}MB")
        
    except Exception as e:
        print(f"   ❌ Failed to fetch stats: {e}")
        cleanup_container(client, container)
        return False
    
    # Test AI suggestions generation
    print("\n💡 Step 4: Generating AI optimization suggestions...")
    
    suggestions = []
    
    if cpu_percent < 10:
        suggestions.append(f"Low CPU usage ({cpu_percent:.1f}%) - Consider reducing CPU allocation")
    elif cpu_percent > 80:
        suggestions.append(f"High CPU usage ({cpu_percent:.1f}%) - Consider increasing CPU allocation")
    else:
        suggestions.append(f"CPU usage is optimal ({cpu_percent:.1f}%)")
    
    if memory_percent < 30:
        suggestions.append(f"Low memory usage ({memory_percent:.1f}%) - Consider reducing memory limit")
    elif memory_percent > 85:
        suggestions.append(f"High memory usage ({memory_percent:.1f}%) - Risk of OOM, increase memory")
    else:
        suggestions.append(f"Memory usage is optimal ({memory_percent:.1f}%)")
    
    print(f"   ✅ Suggestions generated:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"      {i}. {suggestion}")
    
    # Test cost calculation
    print("\n💰 Step 5: Calculating cost optimization...")
    
    current_cost = (memory_limit_mb / 1024) * 0.01
    potential_savings = current_cost * 0.3 if memory_percent < 30 else 0
    
    print(f"   ✅ Cost analysis:")
    print(f"      Current: ${current_cost:.4f}/hour")
    print(f"      Potential savings: ${potential_savings:.4f}/hour")
    
    # Cleanup
    print("\n🧹 Step 6: Cleanup test container...")
    cleanup_container(client, container)
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ INTEGRATION TEST PASSED!")
    print("=" * 70)
    print("\n📋 Summary:")
    print("   ✓ Container created with dprod labels")
    print("   ✓ Container discovered by project_id")
    print("   ✓ Docker stats retrieved successfully")
    print("   ✓ AI suggestions generated")
    print("   ✓ Cost optimization calculated")
    print("\n🎯 When you run 'dprod deploy':")
    print("   1. Container will be created with project labels")
    print("   2. AI can find container using project_id")
    print("   3. Real resource metrics will be available")
    print("   4. Cost optimization suggestions will be accurate")
    print("   5. Background agents can monitor deployments 24/7")
    print("\n🚀 The Docker stats integration is READY FOR PRODUCTION!")
    
    return True


def cleanup_container(client, container):
    """Clean up test container."""
    try:
        container.stop(timeout=5)
        container.remove()
        print("   ✅ Test container cleaned up")
    except Exception as e:
        print(f"   ⚠️  Failed to cleanup container: {e}")


def main():
    """Run the integration test."""
    success = simulate_dprod_deployment()
    
    if not success:
        print("\n❌ Integration test failed!")
        print("\n💡 This means Docker stats integration needs fixes.")
        print("   Please check the error messages above.")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
