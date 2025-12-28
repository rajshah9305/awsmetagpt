# System Architecture

## Overview

The MetaGPT + E2B Integration System is a production-ready, modular application that generates complete applications using multi-agent AI orchestration and provides live sandbox execution environments.

## Architecture Principles

- **Modular Design**: Each component has a single responsibility
- **Dependency Injection**: Services are injected rather than directly imported
- **Clean Separation**: Clear boundaries between API, business logic, and data layers
- **Error Handling**: Comprehensive exception hierarchy and error recovery
- **Scalability**: Designed for horizontal scaling and high availability

## System Components

### 1. Core Layer (`app/core/`)

#### Configuration System (`config_clean.py`)
- Modular configuration with separate sections
- Environment variable validation
- Type safety with Pydantic
- Production/development mode detection

#### Exception Hierarchy (`exceptions.py`)
- Custom exception classes for different error types
- Structured error information with details
- Consistent error handling across the system

#### Logging System (`logging.py`)
- Centralized logging configuration
- Structured logging with context
- File and console output
- Log level management

### 2. Orchestration Layer (`app/services/orchestration/`)

#### Task Scheduler (`task_scheduler.py`)
- Dependency-aware task scheduling
- Priority-based execution ordering
- Cycle detection and validation
- Retry mechanism for failed tasks

#### Agent State Manager (`agent_state_manager.py`)
- Agent lifecycle management
- State transition tracking
- Performance metrics collection
- Cleanup and resource management

#### MetaGPT Executor (`metagpt_executor.py`)
- MetaGPT integration and configuration
- Model management and switching
- Artifact processing and enhancement
- Streaming execution support

#### Artifact Processor (`artifact_processor.py`)
- File content analysis and validation
- Project structure determination
- Quality scoring and metadata extraction
- Security scanning and sanitization

#### Main Orchestrator (`orchestrator.py`)
- Coordinates all orchestration components
- Session management and lifecycle
- Real-time progress tracking
- Background task management

### 3. Sandbox Layer (`app/services/sandbox/`)

#### Sandbox Manager (`sandbox_manager.py`)
- E2B sandbox lifecycle management
- Resource allocation and monitoring
- Multi-tenant isolation
- Automatic cleanup and scaling

#### Process Manager (`process_manager.py`)
- Process execution and monitoring
- Log streaming and buffering
- Resource limit enforcement
- Health checking and recovery

#### File Manager (`file_manager.py`)
- Secure file operations
- Project type detection
- Path sanitization and validation
- Structure analysis and optimization

#### Application Runners (`application_runners.py`)
- Framework-specific execution strategies
- Dependency installation automation
- Build process management
- Preview URL generation

### 4. API Layer (`app/api/`)

#### Clean Routes (`routes_clean.py`)
- RESTful API endpoints
- Request/response validation
- Proper HTTP status codes
- Comprehensive error handling

#### Middleware (`middleware.py`)
- Rate limiting and throttling
- Request validation and sanitization
- Security headers and CORS
- Error response standardization

#### Dependencies (`dependencies.py`)
- Dependency injection container
- Service lifecycle management
- Health checking and validation
- Request context management

### 5. Data Models (`app/models/`)

#### Schemas (`schemas.py`)
- Pydantic models for validation
- Request/response structures
- Enum definitions and constraints
- Serialization and deserialization

### 6. Frontend Layer (`src/`)

#### Component Architecture
- **Pages**: Route-level components
- **Components**: Reusable UI components
- **Services**: API client and utilities
- **Hooks**: Custom React hooks for state management

#### Modular Sandbox Components
- **SandboxController**: Orchestrates sandbox operations
- **LogViewer**: Real-time log streaming and display
- **FileManager**: File upload and management
- **ProcessControl**: Process lifecycle management

## Data Flow

### 1. Generation Request Flow

```
Client Request → API Validation → Orchestrator → Task Scheduler
                                      ↓
Agent State Manager ← MetaGPT Executor ← Task Assignment
                                      ↓
Artifact Processor ← Generation Results ← MetaGPT Execution
                                      ↓
Client Response ← API Response ← Session Update
```

### 2. Sandbox Execution Flow

```
Artifacts → File Manager → Sandbox Manager → E2B Creation
                              ↓
Process Manager ← Application Runner ← Project Detection
                              ↓
Log Streaming ← Process Execution ← Dependency Installation
                              ↓
Preview URL ← Application Start ← Health Monitoring
```

### 3. Real-time Communication Flow

```
WebSocket Connection → Connection Manager → Session Tracking
                              ↓
Progress Updates ← Event Broadcasting ← State Changes
                              ↓
Client Updates ← Message Routing ← Real-time Events
```

## Scalability Considerations

### Horizontal Scaling
- Stateless service design
- Session data externalization
- Load balancer compatibility
- Database connection pooling

### Resource Management
- Configurable resource limits
- Automatic cleanup processes
- Memory usage monitoring
- Process lifecycle management

### Performance Optimization
- Async/await throughout
- Connection pooling
- Caching strategies
- Lazy loading patterns

## Security Features

### Input Validation
- Pydantic model validation
- File content sanitization
- Path traversal prevention
- Size limit enforcement

### Access Control
- Rate limiting per client
- Resource quota management
- Sandbox isolation
- Process privilege separation

### Error Handling
- Information disclosure prevention
- Graceful degradation
- Audit logging
- Recovery mechanisms

## Monitoring and Observability

### Logging
- Structured logging format
- Correlation ID tracking
- Performance metrics
- Error aggregation

### Health Checks
- Service availability monitoring
- Resource usage tracking
- Dependency health validation
- Automatic recovery triggers

### Metrics Collection
- Request/response metrics
- Resource utilization
- Error rates and patterns
- Performance benchmarks

## Deployment Architecture

### Development Environment
- Local development server
- Hot reloading support
- Test automation
- Debug logging

### Production Environment
- Container orchestration
- Load balancing
- SSL termination
- Database clustering

### Infrastructure Components
- Web server (Nginx/Apache)
- Application server (Uvicorn/Gunicorn)
- Database (PostgreSQL/Redis)
- Message queue (Redis/RabbitMQ)
- File storage (S3/MinIO)

## Extension Points

### Custom Agents
- Agent role definitions
- Task type extensions
- Workflow customization
- Plugin architecture

### Application Runners
- Framework support addition
- Build process customization
- Deployment target integration
- Runtime environment configuration

### API Extensions
- Custom endpoint addition
- Middleware integration
- Authentication providers
- Webhook support

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.8+)
- **AI Integration**: MetaGPT, AWS Bedrock
- **Sandbox**: E2B Cloud Sandboxes
- **Validation**: Pydantic
- **Async**: asyncio, aiofiles
- **Testing**: pytest, pytest-asyncio

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Hooks
- **HTTP Client**: Axios
- **UI Components**: Lucide React

### Infrastructure
- **Web Server**: Uvicorn/Gunicorn
- **Database**: PostgreSQL (future)
- **Cache**: Redis (future)
- **Storage**: Local filesystem/S3
- **Monitoring**: Custom metrics

## Configuration Management

### Environment Variables
- Modular configuration sections
- Type validation and conversion
- Default value management
- Production/development modes

### Feature Flags
- Service enable/disable toggles
- Experimental feature control
- A/B testing support
- Runtime configuration changes

### Resource Limits
- Configurable quotas and limits
- Dynamic scaling parameters
- Performance tuning options
- Security constraint management