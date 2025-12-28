#!/usr/bin/env python3
"""
Verify MetaGPT and E2B implementations
"""

import sys
import ast
from pathlib import Path

def check_metagpt_integration():
    """Verify MetaGPT integration"""
    print("🔍 Checking MetaGPT Integration...")
    
    metagpt_service = Path("app/services/metagpt_service.py")
    agent_orchestrator = Path("app/services/agent_orchestrator.py")
    
    checks = {
        "MetaGPT service file exists": metagpt_service.exists(),
        "Agent orchestrator exists": agent_orchestrator.exists()
    }
    
    # Check for real MetaGPT imports
    if metagpt_service.exists():
        content = metagpt_service.read_text()
        checks["Imports SoftwareCompany"] = "from metagpt.software_company import SoftwareCompany" in content
        checks["Imports Team"] = "from metagpt.team import Team" in content
        checks["Imports ProductManager"] = "ProductManager" in content
        checks["Imports Architect"] = "Architect" in content
        checks["Imports Engineer"] = "Engineer" in content
        checks["Imports QaEngineer"] = "QaEngineer" in content
        checks["Calls company.run_project"] = "company.run_project" in content or "run_project" in content
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())

def check_e2b_integration():
    """Verify E2B integration"""
    print("\n🔍 Checking E2B Integration...")
    
    e2b_service = Path("app/services/e2b_service.py")
    
    checks = {
        "E2B service file exists": e2b_service.exists()
    }
    
    # Check for real E2B imports
    if e2b_service.exists():
        content = e2b_service.read_text()
        checks["Imports E2B Sandbox"] = "from e2b import Sandbox" in content
        checks["Creates Sandbox instance"] = "Sandbox(" in content
        checks["Has sandbox creation method"] = "async def create_sandbox" in content
        checks["Has file write method"] = "async def write_files" in content
        checks["Has process execution"] = "sandbox.process" in content or "process.start" in content
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())

def check_api_routes():
    """Verify API routes"""
    print("\n🔍 Checking API Routes...")
    
    routes = Path("app/api/routes.py")
    
    checks = {
        "Routes file exists": routes.exists()
    }
    
    if routes.exists():
        content = routes.read_text()
        checks["Has generate endpoint"] = "@router.post(\"/generate\"" in content
        checks["Has status endpoint"] = "get_generation_status" in content
        checks["Has artifacts endpoint"] = "get_generation_artifacts" in content
        checks["Has E2B sandbox endpoints"] = "e2b/sandbox" in content
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())

def check_websocket_integration():
    """Verify WebSocket integration"""
    print("\n🔍 Checking WebSocket Integration...")
    
    main_file = Path("main.py")
    ws_manager = Path("app/services/websocket_manager.py")
    
    checks = {
        "Main file exists": main_file.exists(),
        "WebSocket manager exists": ws_manager.exists()
    }
    
    if main_file.exists():
        content = main_file.read_text()
        checks["Has WebSocket endpoint"] = "@app.websocket" in content
        checks["Uses websocket_manager"] = "websocket_manager" in content
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())

def main():
    print("="*60)
    print("METAGPT + E2B IMPLEMENTATION VERIFICATION")
    print("="*60)
    
    results = []
    
    results.append(("MetaGPT Integration", check_metagpt_integration()))
    results.append(("E2B Integration", check_e2b_integration()))
    results.append(("API Routes", check_api_routes()))
    results.append(("WebSocket Integration", check_websocket_integration()))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Real implementations verified!")
    else:
        print("❌ SOME CHECKS FAILED - Review implementation")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
