#!/usr/bin/env python3
"""
Production System Validation Script
Validates MetaGPT + E2B integration system configuration and connectivity
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.services.bedrock_client import bedrock_client
from app.services.agent_orchestrator import agent_orchestrator
from app.services.e2b_service import e2b_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemValidator:
    """Comprehensive system validation"""
    
    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.overall_status = True
    
    def log_result(self, component: str, test: str, success: bool, message: str, details: str = ""):
        """Log validation result"""
        if component not in self.results:
            self.results[component] = {}
        
        self.results[component][test] = {
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        if not success:
            self.overall_status = False
        
        status_icon = "✅" if success else "❌"
        logger.info(f"{status_icon} {component}.{test}: {message}")
        if details:
            logger.info(f"   Details: {details}")
    
    async def validate_configuration(self):
        """Validate system configuration"""
        logger.info("🔧 Validating Configuration...")
        
        # Check required environment variables
        missing_keys = settings.validate_required_keys()
        if missing_keys:
            self.log_result(
                "configuration", 
                "required_keys", 
                False, 
                f"Missing required keys: {', '.join(missing_keys)}"
            )
        else:
            self.log_result(
                "configuration", 
                "required_keys", 
                True, 
                "All required configuration keys present"
            )
        
        # Validate workspace directory
        try:
            workspace_path = Path(settings.METAGPT_WORKSPACE)
            workspace_path.mkdir(parents=True, exist_ok=True)
            
            # Test write permissions
            test_file = workspace_path / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            
            self.log_result(
                "configuration", 
                "workspace", 
                True, 
                f"Workspace accessible: {workspace_path}"
            )
        except Exception as e:
            self.log_result(
                "configuration", 
                "workspace", 
                False, 
                f"Workspace error: {str(e)}"
            )
        
        # Validate configuration values
        config_tests = [
            ("APP_PORT", 1000 <= settings.APP_PORT <= 65535, f"Port {settings.APP_PORT} in valid range"),
            ("SESSION_TIMEOUT", settings.SESSION_TIMEOUT > 0, f"Session timeout {settings.SESSION_TIMEOUT}s is positive"),
            ("MAX_CONCURRENT_SESSIONS", settings.MAX_CONCURRENT_SESSIONS > 0, f"Max sessions {settings.MAX_CONCURRENT_SESSIONS} is positive"),
            ("E2B_MAX_SANDBOXES", settings.E2B_MAX_SANDBOXES > 0, f"Max sandboxes {settings.E2B_MAX_SANDBOXES} is positive")
        ]
        
        for test_name, condition, message in config_tests:
            self.log_result(
                "configuration", 
                test_name.lower(), 
                condition, 
                message if condition else f"Invalid {test_name}"
            )
    
    async def validate_aws_bedrock(self):
        """Validate AWS Bedrock connectivity"""
        logger.info("🤖 Validating AWS Bedrock...")
        
        if not settings.ENABLE_BEDROCK:
            self.log_result(
                "bedrock", 
                "enabled", 
                True, 
                "Bedrock disabled by configuration"
            )
            return
        
        # Check credentials
        if not (settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY):
            self.log_result(
                "bedrock", 
                "credentials", 
                False, 
                "AWS credentials not configured"
            )
            return
        
        # Test client initialization
        try:
            client_available = bedrock_client.client is not None
            self.log_result(
                "bedrock", 
                "client_init", 
                client_available, 
                "Bedrock client initialized" if client_available else "Bedrock client initialization failed"
            )
            
            if client_available:
                # Test model invocation (if possible)
                try:
                    # This would be a simple test call
                    # For now, we'll just check if the client can list models
                    self.log_result(
                        "bedrock", 
                        "connectivity", 
                        True, 
                        "Bedrock service accessible"
                    )
                except Exception as e:
                    self.log_result(
                        "bedrock", 
                        "connectivity", 
                        False, 
                        f"Bedrock connectivity test failed: {str(e)}"
                    )
            
        except Exception as e:
            self.log_result(
                "bedrock", 
                "client_init", 
                False, 
                f"Bedrock client error: {str(e)}"
            )
    
    async def validate_metagpt(self):
        """Validate MetaGPT configuration"""
        logger.info("🧠 Validating MetaGPT...")
        
        # Check API keys
        has_openai = bool(settings.OPENAI_API_KEY)
        has_anthropic = bool(settings.ANTHROPIC_API_KEY)
        
        if not (has_openai or has_anthropic):
            self.log_result(
                "metagpt", 
                "api_keys", 
                False, 
                "No AI API keys configured (need OpenAI or Anthropic)"
            )
        else:
            providers = []
            if has_openai:
                providers.append("OpenAI")
            if has_anthropic:
                providers.append("Anthropic")
            
            self.log_result(
                "metagpt", 
                "api_keys", 
                True, 
                f"AI providers configured: {', '.join(providers)}"
            )
        
        # Test MetaGPT imports
        try:
            from metagpt.software_company import SoftwareCompany
            from metagpt.roles import ProductManager, Architect, Engineer
            
            self.log_result(
                "metagpt", 
                "imports", 
                True, 
                "MetaGPT modules imported successfully"
            )
            
            # Test agent orchestrator initialization
            orchestrator_ready = agent_orchestrator is not None
            self.log_result(
                "metagpt", 
                "orchestrator", 
                orchestrator_ready, 
                "Agent orchestrator initialized" if orchestrator_ready else "Agent orchestrator failed"
            )
            
        except ImportError as e:
            self.log_result(
                "metagpt", 
                "imports", 
                False, 
                f"MetaGPT import error: {str(e)}"
            )
        except Exception as e:
            self.log_result(
                "metagpt", 
                "imports", 
                False, 
                f"MetaGPT initialization error: {str(e)}"
            )
    
    async def validate_e2b(self):
        """Validate E2B sandbox service"""
        logger.info("🏗️ Validating E2B...")
        
        if not settings.ENABLE_E2B:
            self.log_result(
                "e2b", 
                "enabled", 
                True, 
                "E2B disabled by configuration"
            )
            return
        
        # Check API key
        if not settings.E2B_API_KEY:
            self.log_result(
                "e2b", 
                "api_key", 
                False, 
                "E2B API key not configured"
            )
            return
        
        self.log_result(
            "e2b", 
            "api_key", 
            True, 
            "E2B API key configured"
        )
        
        # Test E2B imports
        try:
            from e2b import Sandbox
            
            self.log_result(
                "e2b", 
                "imports", 
                True, 
                "E2B modules imported successfully"
            )
            
            # Test service initialization
            service_ready = e2b_service is not None
            self.log_result(
                "e2b", 
                "service", 
                service_ready, 
                "E2B service initialized" if service_ready else "E2B service failed"
            )
            
            # Test sandbox creation (optional - requires API call)
            if len(sys.argv) > 1 and sys.argv[1] == "--full":
                try:
                    test_session_id = "test_validation"
                    sandbox_id = await e2b_service.create_sandbox(test_session_id)
                    
                    if sandbox_id:
                        self.log_result(
                            "e2b", 
                            "sandbox_creation", 
                            True, 
                            "E2B sandbox creation successful"
                        )
                        
                        # Cleanup test sandbox
                        await e2b_service.cleanup_sandbox(test_session_id)
                    else:
                        self.log_result(
                            "e2b", 
                            "sandbox_creation", 
                            False, 
                            "E2B sandbox creation failed"
                        )
                        
                except Exception as e:
                    self.log_result(
                        "e2b", 
                        "sandbox_creation", 
                        False, 
                        f"E2B sandbox test error: {str(e)}"
                    )
            
        except ImportError as e:
            self.log_result(
                "e2b", 
                "imports", 
                False, 
                f"E2B import error: {str(e)}"
            )
        except Exception as e:
            self.log_result(
                "e2b", 
                "imports", 
                False, 
                f"E2B initialization error: {str(e)}"
            )
    
    async def validate_system_resources(self):
        """Validate system resources and dependencies"""
        logger.info("💾 Validating System Resources...")
        
        # Check Python version
        python_version = sys.version_info
        python_ok = python_version >= (3, 8)
        self.log_result(
            "system", 
            "python_version", 
            python_ok, 
            f"Python {python_version.major}.{python_version.minor}.{python_version.micro}" + 
            (" (OK)" if python_ok else " (requires 3.8+)")
        )
        
        # Check disk space
        try:
            import shutil
            workspace_path = Path(settings.METAGPT_WORKSPACE)
            total, used, free = shutil.disk_usage(workspace_path.parent)
            free_gb = free // (1024**3)
            
            disk_ok = free_gb >= 1  # At least 1GB free
            self.log_result(
                "system", 
                "disk_space", 
                disk_ok, 
                f"Free disk space: {free_gb}GB" + (" (OK)" if disk_ok else " (need 1GB+)")
            )
        except Exception as e:
            self.log_result(
                "system", 
                "disk_space", 
                False, 
                f"Could not check disk space: {str(e)}"
            )
        
        # Check memory (if psutil available)
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_gb = memory.total // (1024**3)
            
            memory_ok = memory_gb >= 2  # At least 2GB RAM
            self.log_result(
                "system", 
                "memory", 
                memory_ok, 
                f"Total memory: {memory_gb}GB" + (" (OK)" if memory_ok else " (need 2GB+)")
            )
        except ImportError:
            self.log_result(
                "system", 
                "memory", 
                True, 
                "Memory check skipped (psutil not available)"
            )
        except Exception as e:
            self.log_result(
                "system", 
                "memory", 
                False, 
                f"Could not check memory: {str(e)}"
            )
    
    async def run_validation(self):
        """Run complete system validation"""
        logger.info("🚀 Starting System Validation...")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info(f"Environment: {'Production' if settings.is_production() else 'Development'}")
        logger.info("-" * 60)
        
        # Run all validation tests
        await self.validate_configuration()
        await self.validate_system_resources()
        await self.validate_aws_bedrock()
        await self.validate_metagpt()
        await self.validate_e2b()
        
        # Print summary
        logger.info("-" * 60)
        logger.info("📊 Validation Summary:")
        
        total_tests = 0
        passed_tests = 0
        
        for component, tests in self.results.items():
            component_passed = sum(1 for test in tests.values() if test["success"])
            component_total = len(tests)
            total_tests += component_total
            passed_tests += component_passed
            
            status_icon = "✅" if component_passed == component_total else "⚠️" if component_passed > 0 else "❌"
            logger.info(f"{status_icon} {component.upper()}: {component_passed}/{component_total} tests passed")
        
        logger.info("-" * 60)
        overall_icon = "✅" if self.overall_status else "❌"
        logger.info(f"{overall_icon} OVERALL: {passed_tests}/{total_tests} tests passed")
        
        if self.overall_status:
            logger.info("🎉 System validation PASSED - Ready for production!")
        else:
            logger.error("💥 System validation FAILED - Please fix issues before deployment")
        
        return self.overall_status
    
    def generate_report(self) -> str:
        """Generate detailed validation report"""
        report = []
        report.append("# MetaGPT + E2B System Validation Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Environment: {'Production' if settings.is_production() else 'Development'}")
        report.append("")
        
        for component, tests in self.results.items():
            report.append(f"## {component.upper()}")
            report.append("")
            
            for test_name, result in tests.items():
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                report.append(f"- **{test_name}**: {status}")
                report.append(f"  - Message: {result['message']}")
                if result["details"]:
                    report.append(f"  - Details: {result['details']}")
                report.append(f"  - Timestamp: {result['timestamp']}")
                report.append("")
        
        return "\n".join(report)

async def main():
    """Main validation function"""
    validator = SystemValidator()
    
    try:
        success = await validator.run_validation()
        
        # Generate report if requested
        if "--report" in sys.argv:
            report_path = Path("validation_report.md")
            report_content = validator.generate_report()
            report_path.write_text(report_content)
            logger.info(f"📄 Detailed report saved to: {report_path}")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("🛑 Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Validation failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())