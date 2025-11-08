"""Test script to demonstrate AI agent logging system."""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.api.core.db.database import get_db
from services.detector.core.ai_detector import AIEnhancedDetector


async def test_ai_enhanced_detection():
    """Test the AI-enhanced detector with different project types."""
    
    print("=" * 80)
    print("🤖 AI-ENHANCED DETECTOR DEMONSTRATION")
    print("=" * 80)
    print()
    print("This test demonstrates the AI agent integration:")
    print("  1. Rule-based detection (fast, reliable baseline)")
    print("  2. AI verification and enhancement (learns from deployments)")
    print("  3. Decision logging and performance tracking")
    print("  4. Deployment outcome verification")
    print()
    
    # Test cases with different project types
    test_projects = [
        {
            'path': '/home/dev-soft/dprod/examples/nodejs',
            'project_id': None,  # No real project in DB for testing
            'deployment_id': None,  # No real deployment in DB for testing
            'description': 'Node.js Express Application',
            'expected_success': True
        },
        {
            'path': '/home/dev-soft/dprod/examples/python',
            'project_id': None,
            'deployment_id': None,
            'description': 'Python Flask Application',
            'expected_success': True
        },
        {
            'path': '/home/dev-soft/dprod/examples/static',
            'project_id': None,
            'deployment_id': None,
            'description': 'Static HTML Website',
            'expected_success': True
        }
    ]
    
    # Get database session
    async for db in get_db():
        detector = AIEnhancedDetector(db_session=db)
        
        decision_ids = []
        
        for i, test_project in enumerate(test_projects, 1):
            print(f"\n{'=' * 80}")
            print(f"TEST CASE {i}: {test_project['description']}")
            print(f"{'=' * 80}")
            print(f"📂 Project Path: {test_project['path']}")
            print(f"🆔 Project ID: {test_project['project_id']}")
            print(f"🚀 Deployment ID: {test_project['deployment_id']}")
            print()
            
            try:
                # Run AI-enhanced detection
                result = await detector.detect_project(
                    project_path=Path(test_project['path']),
                    project_id=test_project['project_id'],
                    deployment_id=test_project['deployment_id'],
                    use_ai=True
                )
                
                if result:
                    print("✅ DETECTION COMPLETE")
                    print()
                    print("📊 DETECTION RESULTS:")
                    print(f"  • Detection Method: {result.get('detection_method', 'unknown')}")
                    print(f"  • AI Verified: {result.get('ai_verified', False)}")
                    
                    if 'agreement' in result:
                        agreement = result['agreement']
                        print(f"  • Agreement: {'✅ Yes' if agreement['matches'] else '⚠️  No'}")
                        print(f"  • Rule-based Type: {agreement['rule_type']}")
                        print(f"  • AI Type: {agreement['ai_type']}")
                        print(f"  • AI Confidence: {agreement['ai_confidence']:.2%}")
                    
                    if 'decision_id' in result:
                        decision_ids.append({
                            'id': result['decision_id'],
                            'success': test_project['expected_success']
                        })
                        print(f"  • Decision ID: {result['decision_id']}")
                    
                    print()
                    
                    if 'ai_analysis' in result:
                        ai_analysis = result['ai_analysis']
                        print("🔧 AI-SUGGESTED BUILD CONFIGURATION:")
                        
                        if 'build_config' in ai_analysis:
                            build_config = ai_analysis['build_config']
                            
                            if 'build_steps' in build_config:
                                print("  Build Steps:")
                                for step in build_config['build_steps']:
                                    print(f"    • {step.get('command', 'N/A')}")
                            
                            if 'environment_variables' in build_config:
                                print("  Environment Variables:")
                                for key, value in build_config['environment_variables'].items():
                                    print(f"    • {key}={value}")
                            
                            if 'estimated_duration' in build_config:
                                duration = build_config['estimated_duration']
                                print(f"  Estimated Build Time: {duration}s ({duration/60:.1f} minutes)")
                    
                    print()
                else:
                    print("❌ DETECTION FAILED")
                    print()
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                import traceback
                traceback.print_exc()
                print()
        
        # Simulate deployment outcomes
        print(f"\n{'=' * 80}")
        print("🔄 SIMULATING DEPLOYMENT OUTCOMES")
        print(f"{'=' * 80}")
        print()
        
        for decision in decision_ids:
            print(f"Recording outcome for decision {decision['id']}...")
            await detector.verify_deployment_outcome(
                decision_id=decision['id'],
                was_successful=decision['success'],
                feedback="Simulated deployment for testing"
            )
            print(f"  ✅ {'Success' if decision['success'] else 'Failure'} recorded")
        
        print()
        print(f"\n{'=' * 80}")
        print("📊 SUMMARY")
        print(f"{'=' * 80}")
        print(f"✓ Analyzed {len(test_projects)} projects")
        print(f"✓ Logged {len(decision_ids)} AI decisions to database")
        print(f"✓ Recorded {len(decision_ids)} deployment outcomes")
        print(f"✓ Performance metrics tracked for learning")
        print()
        print("🌐 API Endpoints (require authentication):")
        print("  📊 Metrics:      http://localhost:8000/api/v1/ai/metrics")
        print("  📋 Decisions:    http://localhost:8000/api/v1/ai/decisions")
        print("  📈 Performance:  http://localhost:8000/api/v1/ai/performance")
        print("  🎯 Patterns:     http://localhost:8000/api/v1/ai/patterns")
        print()
        print("💡 The AI agent will learn from these outcomes to improve future detections!")
        print()
        print("=" * 80)
        
        break  # Exit after first db session


async def test_standalone_analyzer():
    """Test the standalone project analyzer (without rule-based comparison)."""
    
    print("\n" + "=" * 80)
    print("🔬 STANDALONE AI ANALYZER TEST")
    print("=" * 80)
    print()
    
    from services.ai.core.project_analyzer_agent import ProjectAnalyzerAgent
    
    async for db in get_db():
        agent = ProjectAnalyzerAgent(db_session=db)
        
        # Test with a Next.js project if it exists
        test_path = "/home/dev-soft/dprod/tools/frontend"
        
        print(f"Analyzing: {test_path}")
        print()
        
        try:
            result = await agent.analyze_project(
                project_path=test_path,
                project_id=None,  # No real project in DB for testing
                deployment_id=None  # No real deployment in DB for testing
            )
            
            print("✅ Analysis complete!")
            print(f"  • Type: {result.get('project_type', 'unknown')}")
            print(f"  • Framework: {result.get('framework', 'none')}")
            print(f"  • Confidence: {result.get('confidence', 0):.2%}")
            print(f"  • Tokens Used: {result.get('tokens_used', 0)}")
            print(f"  • Cost: ${result.get('cost_usd', 0):.6f}")
            print()
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        break


async def main():
    """Run all tests."""
    # Test 1: AI-Enhanced Detector (rule-based + AI)
    await test_ai_enhanced_detection()
    
    # Test 2: Standalone AI Analyzer
    await test_standalone_analyzer()


if __name__ == "__main__":
    asyncio.run(main())
