"""
MetaGPT service for multi-agent app generation
"""

import asyncio
import uuid
from typing import Dict, List, Optional, AsyncGenerator
import logging
from datetime import datetime

from app.models.schemas import (
    GenerationRequest, AgentRole, GeneratedArtifact, 
    AgentUpdate, AppType, BedrockModel
)
from app.services.bedrock_client import bedrock_client
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)

class MetaGPTService:
    """Service for orchestrating MetaGPT agents with Bedrock models"""
    
    def __init__(self):
        self.active_generations: Dict[str, Dict] = {}
    
    async def generate_app(
        self, 
        request: GenerationRequest, 
        client_id: Optional[str] = None
    ) -> str:
        """Start app generation process"""
        generation_id = str(uuid.uuid4())
        
        # Store generation info
        self.active_generations[generation_id] = {
            "request": request,
            "status": "started",
            "progress": 0,
            "artifacts": [],
            "client_id": client_id,
            "created_at": datetime.now()
        }
        
        # Start generation in background
        asyncio.create_task(self._run_generation(generation_id))
        
        return generation_id
    
    async def _run_generation(self, generation_id: str):
        """Run the complete generation process"""
        try:
            generation_data = self.active_generations[generation_id]
            request = generation_data["request"]
            client_id = generation_data.get("client_id")
            
            # Update status
            await self._update_progress(generation_id, "initializing", 5, "Initializing agents...")
            
            # Run agents in sequence
            agents_to_run = request.active_agents
            total_agents = len(agents_to_run)
            
            for i, agent_role in enumerate(agents_to_run):
                progress = 10 + (i * 80 // total_agents)
                await self._run_agent(generation_id, agent_role, progress)
            
            # Finalize
            await self._update_progress(generation_id, "completed", 100, "Generation completed!")
            
        except Exception as e:
            logger.error(f"Generation {generation_id} failed: {e}")
            await self._update_progress(generation_id, "failed", 0, f"Generation failed: {str(e)}")
    
    async def _run_agent(self, generation_id: str, agent_role: AgentRole, base_progress: int):
        """Run a specific agent"""
        generation_data = self.active_generations[generation_id]
        request = generation_data["request"]
        client_id = generation_data.get("client_id")
        
        # Update progress
        await self._update_progress(
            generation_id, 
            "running", 
            base_progress, 
            f"Running {agent_role.value.replace('_', ' ').title()}...",
            current_agent=agent_role.value
        )
        
        # Send agent-specific update
        if client_id:
            await websocket_manager.send_agent_update(
                client_id,
                agent_role.value,
                "running",
                current_task=f"Starting {agent_role.value.replace('_', ' ').title()} analysis...",
                progress=base_progress
            )
            
            # Send thinking update
            await websocket_manager.send_agent_update(
                client_id,
                agent_role.value,
                "running",
                thinking=f"Analyzing requirements and preparing {agent_role.value.replace('_', ' ')} deliverables..."
            )
        
        # Simulate streaming content generation
        if client_id:
            await self._simulate_streaming_generation(client_id, agent_role, request)
        
        # Generate agent-specific content
        artifact = await self._generate_agent_artifact(request, agent_role)
        
        if artifact:
            generation_data["artifacts"].append(artifact)
            
            # Send artifact update
            if client_id:
                await websocket_manager.send_artifact_update(
                    client_id,
                    {
                        "id": f"{agent_role.value}_{generation_id}",
                        "name": artifact.name,
                        "type": artifact.type,
                        "content": artifact.content,
                        "agent_role": agent_role.value,
                        "status": "completed",
                        "progress": 100
                    }
                )
            
            # Send completion update
            if client_id:
                await websocket_manager.send_agent_update(
                    client_id,
                    agent_role.value,
                    "completed",
                    current_task=f"{agent_role.value.replace('_', ' ').title()} completed",
                    progress=base_progress + 10
                )
    
    async def _simulate_streaming_generation(self, client_id: str, agent_role: AgentRole, request: GenerationRequest):
        """Simulate streaming content generation for real-time preview"""
        artifact_name = self._get_artifact_name(agent_role)
        
        # Simulate streaming chunks
        streaming_chunks = [
            f"# {artifact_name}\n\n",
            f"## Overview\n\nAnalyzing requirements for {request.app_type.value}...\n\n",
            f"### Key Requirements\n- {request.requirement[:50]}...\n\n",
            "### Analysis in Progress\n\nGenerating detailed analysis...\n\n",
            "### Recommendations\n\nPreparing recommendations based on requirements...\n\n"
        ]
        
        accumulated_content = ""
        for i, chunk in enumerate(streaming_chunks):
            accumulated_content += chunk
            await websocket_manager.send_streaming_content(
                client_id,
                accumulated_content,
                agent_role.value,
                artifact_name
            )
            # Small delay to simulate real streaming
            await asyncio.sleep(0.5)
    
    def _get_artifact_name(self, agent_role: AgentRole) -> str:
        """Get artifact name for agent role"""
        artifact_names = {
            AgentRole.PRODUCT_MANAGER: "Product Requirements Document",
            AgentRole.ARCHITECT: "System Architecture Design",
            AgentRole.PROJECT_MANAGER: "Project Plan & Timeline",
            AgentRole.ENGINEER: "Technical Implementation",
            AgentRole.QA_ENGINEER: "Test Strategy & Cases",
            AgentRole.DEVOPS: "Deployment & Infrastructure"
        }
        return artifact_names.get(agent_role, "Document")
    
    async def _generate_agent_artifact(
        self, 
        request: GenerationRequest, 
        agent_role: AgentRole
    ) -> Optional[GeneratedArtifact]:
        """Generate artifact for specific agent role"""
        
        # Define agent-specific prompts
        prompts = {
            AgentRole.PRODUCT_MANAGER: self._get_pm_prompt(request),
            AgentRole.ARCHITECT: self._get_architect_prompt(request),
            AgentRole.PROJECT_MANAGER: self._get_project_manager_prompt(request),
            AgentRole.ENGINEER: self._get_engineer_prompt(request),
            AgentRole.QA_ENGINEER: self._get_qa_prompt(request),
            AgentRole.DEVOPS: self._get_devops_prompt(request)
        }
        
        prompt = prompts.get(agent_role)
        if not prompt:
            return None
        
        # Generate content using Bedrock
        content = await bedrock_client.invoke_model(
            request.preferred_model,
            prompt,
            max_tokens=3000
        )
        
        if not content:
            return None
        
        # Create artifact
        artifact_names = {
            AgentRole.PRODUCT_MANAGER: "Product Requirements Document",
            AgentRole.ARCHITECT: "System Architecture Design",
            AgentRole.PROJECT_MANAGER: "Project Plan & Timeline",
            AgentRole.ENGINEER: "Technical Implementation",
            AgentRole.QA_ENGINEER: "Test Strategy & Cases",
            AgentRole.DEVOPS: "Deployment & Infrastructure"
        }
        
        return GeneratedArtifact(
            name=artifact_names[agent_role],
            type="document",
            content=content,
            agent_role=agent_role
        )
    
    def _get_pm_prompt(self, request: GenerationRequest) -> str:
        """Generate Product Manager prompt"""
        return f"""
As a Product Manager, analyze this requirement and create a comprehensive Product Requirements Document (PRD):

Requirement: {request.requirement}
App Type: {request.app_type.value}
Additional Requirements: {request.additional_requirements or 'None'}

Please provide:
1. Executive Summary
2. User Stories (with acceptance criteria)
3. Functional Requirements
4. Non-functional Requirements
5. Success Metrics
6. Risk Assessment
7. Competitive Analysis (brief)

Format as a structured document with clear sections.
"""
    
    def _get_architect_prompt(self, request: GenerationRequest) -> str:
        """Generate System Architect prompt"""
        return f"""
As a System Architect, design the technical architecture for this application:

Requirement: {request.requirement}
App Type: {request.app_type.value}
Tech Preferences: {', '.join(request.tech_stack_preferences or [])}

Please provide:
1. High-level Architecture Overview
2. Technology Stack Recommendations
3. System Components & Services
4. Data Architecture & Database Design
5. API Design Patterns
6. Security Considerations
7. Scalability & Performance Strategy
8. Integration Points

Include architectural diagrams in text format where helpful.
"""
    
    def _get_project_manager_prompt(self, request: GenerationRequest) -> str:
        """Generate Project Manager prompt"""
        return f"""
As a Project Manager, create a detailed project plan for this application:

Requirement: {request.requirement}
App Type: {request.app_type.value}

Please provide:
1. Project Timeline & Milestones
2. Task Breakdown Structure
3. Resource Requirements
4. Risk Management Plan
5. Communication Plan
6. Quality Assurance Process
7. Delivery Schedule
8. Success Criteria & KPIs

Format as a actionable project plan.
"""
    
    def _get_engineer_prompt(self, request: GenerationRequest) -> str:
        """Generate Engineer prompt"""
        return f"""
As a Software Engineer, provide technical implementation details for this application:

Requirement: {request.requirement}
App Type: {request.app_type.value}
Tech Preferences: {', '.join(request.tech_stack_preferences or [])}

Please provide:
1. Detailed Technical Specifications
2. Code Structure & Organization
3. Key Algorithms & Logic
4. Database Schema Design
5. API Endpoints Specification
6. Third-party Integrations
7. Performance Optimization Strategies
8. Code Examples (pseudo-code or actual code snippets)

Focus on practical implementation details.
"""
    
    def _get_qa_prompt(self, request: GenerationRequest) -> str:
        """Generate QA Engineer prompt"""
        return f"""
As a QA Engineer, create a comprehensive testing strategy for this application:

Requirement: {request.requirement}
App Type: {request.app_type.value}

Please provide:
1. Test Strategy Overview
2. Test Cases (Unit, Integration, E2E)
3. Performance Testing Plan
4. Security Testing Approach
5. User Acceptance Testing Criteria
6. Test Automation Strategy
7. Bug Tracking & Reporting Process
8. Quality Metrics & KPIs

Include specific test scenarios and edge cases.
"""
    
    def _get_devops_prompt(self, request: GenerationRequest) -> str:
        """Generate DevOps prompt"""
        return f"""
As a DevOps Engineer, design the deployment and infrastructure strategy for this application:

Requirement: {request.requirement}
App Type: {request.app_type.value}

Please provide:
1. Infrastructure Architecture
2. Deployment Strategy (CI/CD)
3. Environment Configuration
4. Monitoring & Logging Setup
5. Backup & Disaster Recovery
6. Security & Compliance
7. Scaling Strategy
8. Cost Optimization

Include specific tools and technologies recommendations.
"""
    
    async def _update_progress(
        self, 
        generation_id: str, 
        status: str, 
        progress: int, 
        message: str,
        current_agent: Optional[str] = None,
        estimated_time: Optional[str] = None
    ):
        """Update generation progress"""
        if generation_id in self.active_generations:
            self.active_generations[generation_id].update({
                "status": status,
                "progress": progress,
                "last_message": message,
                "current_agent": current_agent,
                "updated_at": datetime.now()
            })
            
            # Send WebSocket update if client connected
            client_id = self.active_generations[generation_id].get("client_id")
            if client_id:
                # Calculate estimated time based on progress
                if not estimated_time and progress > 0:
                    start_time = self.active_generations[generation_id].get("created_at")
                    if start_time:
                        elapsed = (datetime.now() - start_time).total_seconds()
                        if progress > 10:  # Only estimate after some progress
                            total_estimated = (elapsed / progress) * 100
                            remaining = total_estimated - elapsed
                            estimated_time = f"{int(remaining // 60)}m {int(remaining % 60)}s"
                
                await websocket_manager.send_progress_update(
                    client_id,
                    generation_id,
                    status,
                    progress,
                    message,
                    current_agent,
                    estimated_time
                )
    
    def get_generation_status(self, generation_id: str) -> Optional[Dict]:
        """Get current generation status"""
        return self.active_generations.get(generation_id)
    
    def get_generation_artifacts(self, generation_id: str) -> List[GeneratedArtifact]:
        """Get generated artifacts for a generation"""
        generation_data = self.active_generations.get(generation_id)
        if generation_data:
            return generation_data.get("artifacts", [])
        return []

# Global instance
metagpt_service = MetaGPTService()