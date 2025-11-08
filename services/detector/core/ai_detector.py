"""AI-enhanced project detector with verification and learning capabilities."""

from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from services.shared.core.schemas import ProjectConfig
from services.detector.core.detector import ProjectDetector
from services.ai.core.project_analyzer_agent import ProjectAnalyzerAgent
from services.ai.core.ai_logger import AILogger


class AIEnhancedDetector:
    """
    Enhanced detector that combines rule-based detection with AI verification.
    
    This detector uses the traditional rule-based ProjectDetector as the
    primary detection mechanism, then uses the AI agent to:
    1. Verify the detection was correct
    2. Suggest optimizations to the configuration
    3. Learn from successful/failed deployments
    """
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """Initialize the AI-enhanced detector."""
        self.rule_detector = ProjectDetector()
        self.db_session = db_session
        self.ai_agent = ProjectAnalyzerAgent(db_session) if db_session else None
        self.ai_logger = AILogger(db_session) if db_session else None
    
    async def detect_project(
        self,
        project_path: Path,
        project_id: Optional[str] = None,
        deployment_id: Optional[str] = None,
        use_ai: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Detect project with optional AI enhancement.
        
        Args:
            project_path: Path to the project directory
            project_id: Optional project ID for tracking
            deployment_id: Optional deployment ID for tracking
            use_ai: Whether to use AI enhancement (default True)
            
        Returns:
            Enhanced project configuration with AI insights
        """
        # Use rule-based detector as baseline
        rule_config = self.rule_detector.detect_project(project_path)
        
        if not rule_config:
            print("❌ Rule-based detection failed")
            return None
        
        print(f"✅ Rule-based detector identified: {rule_config.type.value}")
        
        # If AI is disabled or unavailable, return rule-based result
        if not use_ai or not self.ai_agent:
            return {
                'detection_method': 'rule-based',
                'config': rule_config,
                'ai_verified': False
            }
        
        # Use AI to verify and enhance
        try:
            print("🤖 Running AI verification...")
            ai_result = await self.ai_agent.analyze_project(
                project_path=str(project_path),
                project_id=project_id,
                deployment_id=deployment_id
            )
            
            # Compare rule-based and AI results
            agreement = self._compare_results(rule_config, ai_result)
            
            if agreement['matches']:
                print(f"✅ AI agrees with rule-based detection (confidence: {ai_result.get('confidence', 0):.2%})")
            else:
                print(f"⚠️  AI suggests different configuration:")
                print(f"   Rule-based: {rule_config.type.value}")
                print(f"   AI suggests: {ai_result.get('project_type', 'unknown')}")
                print(f"   AI confidence: {ai_result.get('confidence', 0):.2%}")
            
            # Return enhanced result with both analyses
            return {
                'detection_method': 'ai-enhanced',
                'rule_based_config': rule_config,
                'ai_analysis': ai_result,
                'agreement': agreement,
                'ai_verified': True,
                'decision_id': ai_result.get('decision_id'),
                'recommended_config': self._merge_configs(rule_config, ai_result, agreement)
            }
            
        except Exception as e:
            print(f"⚠️  AI verification failed: {str(e)}")
            print("   Falling back to rule-based detection")
            return {
                'detection_method': 'rule-based-fallback',
                'config': rule_config,
                'ai_verified': False,
                'ai_error': str(e)
            }
    
    async def verify_deployment_outcome(
        self,
        decision_id: str,
        was_successful: bool,
        feedback: Optional[str] = None
    ):
        """
        Record deployment outcome to improve future decisions.
        
        Args:
            decision_id: The AI decision ID from detection
            was_successful: Whether the deployment succeeded
            feedback: Optional feedback about the deployment
        """
        if not self.ai_logger:
            return
        
        try:
            await self.ai_logger.log_decision_verification(
                decision_id=decision_id,
                was_correct=was_successful,
                verification_source="outcome",
                override_reason=feedback
            )
            print(f"✅ Logged deployment outcome for decision {decision_id}")
        except Exception as e:
            print(f"⚠️  Failed to log outcome: {str(e)}")
    
    def _compare_results(
        self,
        rule_config: ProjectConfig,
        ai_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare rule-based and AI results."""
        rule_type = rule_config.type.value
        ai_type = ai_result.get('project_type', 'unknown')
        
        # Check if they agree on project type
        matches = (rule_type.lower() == ai_type.lower())
        
        # Calculate confidence delta
        ai_confidence = ai_result.get('confidence', 0.0)
        
        return {
            'matches': matches,
            'rule_type': rule_type,
            'ai_type': ai_type,
            'ai_confidence': ai_confidence,
            'recommendation': 'use_rule_based' if not matches and ai_confidence < 0.8 else 'use_ai'
        }
    
    def _merge_configs(
        self,
        rule_config: ProjectConfig,
        ai_result: Dict[str, Any],
        agreement: Dict[str, Any]
    ) -> ProjectConfig:
        """
        Merge rule-based and AI configurations.
        
        For now, we trust rule-based when there's disagreement with low AI confidence.
        As AI confidence improves, we can shift to trusting AI more.
        """
        if agreement['matches'] or agreement['recommendation'] == 'use_rule_based':
            return rule_config
        
        # If AI has high confidence and disagrees, we could create a hybrid config
        # For now, still prefer rule-based for safety
        return rule_config
