# System Architecture - AI Agent Orchestration System

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │   Web    │  │  Mobile  │  │   CLI    │  │   API    │           │
│  │  Client  │  │   App    │  │   Tool   │  │ Clients  │           │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘           │
└────────┼─────────────┼─────────────┼─────────────┼─────────────────┘
         │             │             │             │
         └─────────────┴─────────────┴─────────────┘
                           │
                  HTTP/REST API (JSON)
                           │
┌──────────────────────────▼───────────────────────────────────────────┐
│                         API LAYER (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  • Request Validation (Pydantic)                                │ │
│  │  • Authentication & Authorization                               │ │
│  │  • Rate Limiting & CORS                                         │ │
│  │  • Request ID Tracking                                          │ │
│  │  • Error Handling & Response Serialization                     │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  Endpoints:                                                          │
│  ├─ POST /api/v1/documents/upload                                   │
│  ├─ GET  /api/v1/documents/{id}                                     │
│  ├─ GET  /api/v1/jobs/{job_id}                                      │
│  └─ GET  /health                                                     │
└───────────────────────────┬───────────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────────┐
│                   SERVICE/ORCHESTRATION LAYER                          │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────────────┐  │
│  │  PDF Service   │  │  Orchestration   │  │   Email Service     │  │
│  │                │  │     Service      │  │                     │  │
│  │ • Validation   │  │                  │  │ • SendGrid API      │  │
│  │ • Extraction   │  │ • Agent Coord.   │  │ • SMTP Fallback     │  │
│  │ • Metadata     │  │ • Workflow Mgmt  │  │ • Retry Logic       │  │
│  └────────────────┘  └──────────────────┘  └─────────────────────┘  │
└───────────────────────────┬───────────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────────┐
│                    AGENT/TOOLING LAYER (CrewAI)                        │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    CrewAI Orchestration                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐           │ │
│  │  │  PDF        │  │   Email     │  │    Email     │           │ │
│  │  │  Analyzer   │→ │  Composer   │→ │  Validator   │           │ │
│  │  │  Agent      │  │   Agent     │  │    Agent     │           │ │
│  │  │             │  │             │  │              │           │ │
│  │  │ LangChain   │  │ LangChain   │  │  LangChain   │           │ │
│  │  │ Mistral AI  │  │ Mistral AI  │  │  Mistral AI  │           │ │
│  │  └─────────────┘  └─────────────┘  └──────────────┘           │ │
│  │                                                                  │ │
│  │  Features:                                                       │ │
│  │  • Sequential task execution                                     │ │
│  │  • Deterministic JSON output                                     │ │
│  │  • Retry & timeout handling                                      │ │
│  │  • Structured logging                                            │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬───────────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────────┐
│              BACKGROUND TASK PROCESSING (Celery)                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                      Celery Workers                              │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │ │
│  │  │ Worker  │  │ Worker  │  │ Worker  │  │ Worker  │           │ │
│  │  │   #1    │  │   #2    │  │   #3    │  │   #4    │           │ │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │ │
│  │                                                                  │ │
│  │  • Task Queue Management (Redis)                                 │ │
│  │  • Job State Transitions                                         │ │
│  │  • Retry with Exponential Backoff                                │ │
│  │  • Concurrent Processing                                         │ │
│  │  • Dead Letter Queue                                             │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬───────────────────────────────────────────┘
                            │
         ┌──────────────────┴──────────────────┐
         │                                     │
┌────────▼────────┐                  ┌─────────▼────────┐
│  REDIS CACHE    │                  │  PERSISTENCE     │
│  & QUEUE        │                  │  LAYER           │
│                 │                  │                  │
│  • Broker       │                  │  PostgreSQL      │
│  • Result Store │                  │  ┌────────────┐  │
│  • Caching      │                  │  │  Users     │  │
│  • Locking      │                  │  │  Documents │  │
│                 │                  │  │  Jobs      │  │
└─────────────────┘                  │  │  Agents    │  │
                                     │  │  Emails    │  │
                                     │  │  Logs      │  │
                                     │  └────────────┘  │
                                     │                  │
                                     │  SQLAlchemy ORM  │
                                     │  Connection Pool │
                                     └──────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│  │   OpenAI    │    │  SendGrid   │    │    SMTP     │            │
│  │   API       │    │   Email     │    │   Server    │            │
│  │             │    │   Provider  │    │             │            │
│  └─────────────┘    └─────────────┘    └─────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Document Upload Flow
```
1. Client uploads PDF → API validates → Saves to disk
2. Create Document record in DB
3. Create Job record with PENDING status
4. Enqueue Celery task → Return job_id to client
5. Worker picks up task → Updates status to PROCESSING
6. Worker extracts PDF content → Passes to Orchestration Service
7. Orchestration runs 3 agents sequentially
8. Results saved to DB → Email sent
9. Job status → COMPLETED → Client polls for results
```

### Agent Orchestration Flow
```
PDF Content → PDF Analyzer Agent
              ↓ (JSON output)
              Email Composer Agent
              ↓ (Email draft)
              Email Validator Agent
              ↓ (Validation result)
              Email Service → SendGrid/SMTP
```

## Key Design Decisions

1. **Async API + Background Workers**: Keep API responsive
2. **PostgreSQL**: ACID compliance for critical data
3. **Redis**: Fast queue and caching
4. **Celery**: Reliable distributed task execution
5. **CrewAI**: Structured multi-agent workflows
6. **Structured Logging**: JSON logs for easy parsing
7. **State Machine**: Clear job state transitions
8. **Retry Logic**: Exponential backoff for resilience

## Deployment Architecture (Production)

```
                    Internet
                       │
                ┌──────▼──────┐
                │ Load Balancer│
                │   (NGINX)    │
                └──────┬──────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼───┐    ┌────▼───┐    ┌────▼───┐
   │ API #1 │    │ API #2 │    │ API #3 │
   └────┬───┘    └────┬───┘    └────┬───┘
        │              │              │
        └──────────────┴──────────────┘
                       │
              ┌────────┴────────┐
              │                 │
         ┌────▼────┐      ┌────▼────┐
         │  Redis  │      │PostgreSQL│
         │ Cluster │      │ Primary  │
         └─────────┘      │    +     │
                          │ Replicas │
                          └────┬─────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
              ┌─────▼─────┐         ┌────▼────┐
              │  Celery   │         │   S3    │
              │  Workers  │         │  File   │
              │(Auto-scale)│        │ Storage │
              └───────────┘         └─────────┘
```

This architecture provides:
- High availability
- Horizontal scalability
- Fault tolerance
- Observability
- Performance under load
