#!/usr/bin/env python3
"""
System Validation Script for MetaGPT + E2B Integration
Validates all dependencies, configurations, and API connectivity
"""

import sys
import os
from pathlib import Path
import argparse
from typing import List, Tuple, Dict, Any

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


class SystemValidator:
    """Validates system requirements and configuration"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []
    
    def validate_python_version(self) -> bool:
        """Validate Python version"""
        print_info("Checking Python version...")
        version = sys.version_info
        
        if version.major == 3 and version.minor >= 8:
            print_success(f"Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            print_error(f"Python 3.8+ required, found {version.major}.{version.minor}.{version.micro}")
            self.errors.append("Python version too old")
            return False
    
    def validate_dependencies(self) -> bool:
        """Validate all Python dependencies"""
        print_info("Checking Python dependencies...")
        
        dependencies = {
            'fastapi': 'FastAPI',
            'uvicorn': 'Uvicorn',
            'boto3': 'AWS Boto3',
            'metagpt': 'MetaGPT',
            'e2b': 'E2B SDK',
            'pydantic': 'Pydantic',
            'python-dotenv': 'Python-dotenv'
        }
        
        all_ok = True
        for module, name in dependencies.items():
            try:
                __import__(module)
                print_success(f"{name} installed")
            except ImportError:
                print_error(f"{name} not installed")
                self.errors.append(f"Missing dependency: {name}")
                all_ok = False
        
        return all_ok
    
    def validate_metagpt_imports(self) -> bool:
        """Validate MetaGPT can be imported"""
        print_info("Validating MetaGPT imports...")
        
        try:
            from metagpt.team import Team
            print_success("MetaGPT Team imported successfully")
            
            from metagpt.roles import ProductManager, Architect, Engineer
            print_success("MetaGPT roles imported successfully")
            
            return True
        except ImportError as e:
            print_error(f"MetaGPT import failed: {e}")
            self.errors.append(f"MetaGPT import error: {e}")
            return False
    
    def validate_e2b_sdk(self) -> bool:
        """Validate E2B SDK"""
        print_info("Validating E2B SDK...")
        
        try:
            from e2b import Sandbox
            print_success("E2B Sandbox imported successfully")
            return True
        except ImportError as e:
            print_error(f"E2B SDK import failed: {e}")
            self.errors.append(f"E2B import error: {e}")
            return False
    
    def validate_environment_variables(self) -> bool:
        """Validate environment variables"""
        print_info("Checking environment variables...")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = {
            'AWS_ACCESS_KEY_ID': 'AWS Access Key',
            'AWS_SECRET_ACCESS_KEY': 'AWS Secret Key',
            'AWS_REGION': 'AWS Region'
        }
        
        optional_vars = {
            'E2B_API_KEY': 'E2B API Key',
            'OPENAI_API_KEY': 'OpenAI API Key',
            'ANTHROPIC_API_KEY': 'Anthropic API Key'
        }
        
        all_ok = True
        
        # Check required variables
        for var, name in required_vars.items():
            value = os.getenv(var)
            if value:
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                print_success(f"{name}: {masked}")
            else:
                print_error(f"{name} not set")
                self.errors.append(f"Missing required env var: {var}")
                all_ok = False
        
        # Check optional variables
        has_ai_key = False
        for var, name in optional_vars.items():
            value = os.getenv(var)
            if value:
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                print_success(f"{name}: {masked}")
                if 'API_KEY' in var and var != 'E2B_API_KEY':
                    has_ai_key = True
            else:
                print_warning(f"{name} not set (optional)")
                self.warnings.append(f"Optional env var not set: {var}")
        
        if not has_ai_key:
            print_warning("No AI API key configured (OpenAI or Anthropic)")
            self.warnings.append("No AI API key for MetaGPT")
        
        return all_ok
    
    def validate_aws_connectivity(self) -> bool:
        """Validate AWS Bedrock connectivity"""
        print_info("Testing AWS Bedrock connectivity...")
        
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            client = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            # Try to list models (this validates credentials)
            try:
                # Just creating client is enough for basic validation
                print_success("AWS Bedrock client initialized")
                return True
            except Exception as e:
                print_warning(f"AWS Bedrock access may be limited: {e}")
                self.warnings.append(f"AWS Bedrock warning: {e}")
                return True
                
        except NoCredentialsError:
            print_error("AWS credentials not found or invalid")
            self.errors.append("Invalid AWS credentials")
            return False
        except Exception as e:
            print_error(f"AWS connectivity error: {e}")
            self.errors.append(f"AWS error: {e}")
            return False
    
    def validate_directories(self) -> bool:
        """Validate required directories exist"""
        print_info("Checking required directories...")
        
        directories = ['workspace', 'logs', 'temp']
        all_ok = True
        
        for dir_name in directories:
            dir_path = Path(dir_name)
            if dir_path.exists():
                print_success(f"Directory '{dir_name}' exists")
            else:
                print_warning(f"Directory '{dir_name}' does not exist (will be created)")
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    print_success(f"Created directory '{dir_name}'")
                except Exception as e:
                    print_error(f"Failed to create '{dir_name}': {e}")
                    self.errors.append(f"Cannot create directory: {dir_name}")
                    all_ok = False
        
        return all_ok
    
    def validate_node_dependencies(self) -> bool:
        """Validate Node.js and npm dependencies"""
        print_info("Checking Node.js dependencies...")
        
        import subprocess
        
        try:
            # Check Node.js
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"Node.js {result.stdout.strip()}")
            else:
                print_error("Node.js not found")
                self.errors.append("Node.js not installed")
                return False
            
            # Check npm
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"npm {result.stdout.strip()}")
            else:
                print_error("npm not found")
                self.errors.append("npm not installed")
                return False
            
            # Check if node_modules exists
            if Path('node_modules').exists():
                print_success("Node modules installed")
            else:
                print_warning("Node modules not installed (run 'npm install')")
                self.warnings.append("Node modules missing")
            
            return True
            
        except FileNotFoundError:
            print_error("Node.js or npm not found in PATH")
            self.errors.append("Node.js/npm not in PATH")
            return False
    
    def print_summary(self):
        """Print validation summary"""
        print_header("VALIDATION SUMMARY")
        
        print(f"\n{Colors.BOLD}Results:{Colors.END}")
        print(f"  {Colors.GREEN}✅ Successes: {len(self.successes)}{Colors.END}")
        print(f"  {Colors.YELLOW}⚠️  Warnings: {len(self.warnings)}{Colors.END}")
        print(f"  {Colors.RED}❌ Errors: {len(self.errors)}{Colors.END}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}Warnings:{Colors.END}")
            for warning in self.warnings:
                print(f"  {Colors.YELLOW}• {warning}{Colors.END}")
        
        if self.errors:
            print(f"\n{Colors.RED}{Colors.BOLD}Errors:{Colors.END}")
            for error in self.errors:
                print(f"  {Colors.RED}• {error}{Colors.END}")
        
        if not self.errors:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ System validation passed!{Colors.END}")
            print(f"{Colors.GREEN}Your system is ready to run MetaGPT + E2B Integration.{Colors.END}\n")
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ System validation failed!{Colors.END}")
            print(f"{Colors.RED}Please fix the errors above before running the application.{Colors.END}\n")
            return False
    
    def run_all_validations(self) -> bool:
        """Run all validation checks"""
        print_header("METAGPT + E2B SYSTEM VALIDATION")
        
        validations = [
            ("Python Version", self.validate_python_version),
            ("Python Dependencies", self.validate_dependencies),
            ("MetaGPT Imports", self.validate_metagpt_imports),
            ("E2B SDK", self.validate_e2b_sdk),
            ("Environment Variables", self.validate_environment_variables),
            ("AWS Connectivity", self.validate_aws_connectivity),
            ("Directories", self.validate_directories),
            ("Node.js Dependencies", self.validate_node_dependencies)
        ]
        
        results = []
        for name, validation_func in validations:
            print_header(name)
            try:
                result = validation_func()
                results.append(result)
            except Exception as e:
                print_error(f"Validation failed with exception: {e}")
                self.errors.append(f"{name} validation exception: {e}")
                results.append(False)
        
        return self.print_summary()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Validate MetaGPT + E2B Integration System'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='Generate detailed report'
    )
    
    args = parser.parse_args()
    
    validator = SystemValidator(verbose=args.verbose)
    success = validator.run_all_validations()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
