# API Usage Examples

## Complete API Reference with Examples

### Base URL
```
http://localhost:8000
```

---

## 1. Health Check

Check if the API is running and services are healthy.

### Request
```bash
curl -X GET http://localhost:8000/health
```

### Response
```json
{
  "status": "healthy",
  "service": "AI Agent Orchestration System",
  "version": "v1",
  "environment": "development",
  "checks": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

---

## 2. Upload PDF Document

Upload a PDF for processing and email generation.

### Request
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf" \
  -F "recipient_email=recipient@example.com" \
  -F "user_id=1"
```

### Python Example
```python
import requests

url = "http://localhost:8000/api/v1/documents/upload"

files = {
    'file': open('document.pdf', 'rb')
}
data = {
    'recipient_email': 'recipient@example.com',
    'user_id': 1
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### JavaScript/Node.js Example
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('document.pdf'));
form.append('recipient_email', 'recipient@example.com');
form.append('user_id', '1');

axios.post('http://localhost:8000/api/v1/documents/upload', form, {
  headers: form.getHeaders()
})
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

### Response
```json
{
  "document": {
    "id": 1,
    "user_id": 1,
    "filename": "20240306_145030_abc123_document.pdf",
    "original_filename": "document.pdf",
    "file_size": 245680,
    "mime_type": "application/pdf",
    "checksum": "a1b2c3d4e5f6...",
    "page_count": 5,
    "title": "Sample Document",
    "author": "John Doe",
    "is_processed": false,
    "created_at": "2024-03-06T14:50:30.123Z",
    "updated_at": "2024-03-06T14:50:30.123Z"
  },
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Document uploaded successfully. Processing in background."
}
```

---

## 3. Check Job Status (Quick)

Get a quick status update on a processing job.

### Request
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/{job_id}/status"
```

### Example
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000/status"
```

### Response - Pending
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "progress": 0,
  "message": "Job is queued for processing",
  "result": null
}
```

### Response - Processing
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PROCESSING",
  "progress": 50,
  "message": "Job is currently being processed",
  "result": null
}
```

### Response - Completed
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "COMPLETED",
  "progress": 100,
  "message": "Job completed successfully",
  "result": {
    "success": true,
    "execution_time_ms": 15420,
    "stages": {
      "pdf_analysis": {...},
      "email_composition": {...},
      "email_validation": {...},
      "email_delivery": {...}
    }
  }
}
```

### Response - Failed
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "FAILED",
  "progress": 100,
  "message": "Job failed: Mistral AI API key invalid",
  "result": null
}
```

---

## 4. Get Detailed Job Information

Get complete job details including agent outputs and logs.

### Request
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/{job_id}"
```

### Response
```json
{
  "id": 1,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "document_id": 1,
  "status": "COMPLETED",
  "retry_count": 0,
  "max_retries": 3,
  "started_at": "2024-03-06T14:50:31.000Z",
  "completed_at": "2024-03-06T14:50:46.420Z",
  "execution_time_ms": 15420,
  "result": {
    "success": true,
    "execution_time_ms": 15420,
    "stages": {...}
  },
  "error_message": null,
  "created_at": "2024-03-06T14:50:30.500Z",
  "updated_at": "2024-03-06T14:50:46.420Z",
  "agent_outputs": [
    {
      "agent_name": "PDF Analyzer",
      "agent_role": "pdf_analysis",
      "output_data": {
        "document_type": "resume",
        "summary": "Professional resume...",
        "key_entities": {...}
      },
      "execution_time_ms": 4500,
      "created_at": "2024-03-06T14:50:35.500Z"
    },
    {
      "agent_name": "Email Composer",
      "agent_role": "email_composition",
      "output_data": {
        "subject": "Resume Analysis: John Doe",
        "body": "Dear Hiring Manager...",
        "tone": "formal"
      },
      "execution_time_ms": 3200,
      "created_at": "2024-03-06T14:50:38.700Z"
    },
    {
      "agent_name": "Email Validator",
      "agent_role": "email_validation",
      "output_data": {
        "is_valid": true,
        "ready_to_send": true,
        "risk_level": "low"
      },
      "execution_time_ms": 1200,
      "created_at": "2024-03-06T14:50:39.900Z"
    }
  ],
  "email_records": [
    {
      "to_email": "recipient@example.com",
      "subject": "Resume Analysis: John Doe",
      "status": "SENT",
      "sent_at": "2024-03-06T14:50:45.000Z",
      "error_message": null
    }
  ],
  "execution_logs": [
    {
      "level": "INFO",
      "step": "job_started",
      "message": "Processing started for document 1",
      "metadata": {},
      "created_at": "2024-03-06T14:50:31.000Z"
    },
    {
      "level": "INFO",
      "step": "pdf_extracted",
      "message": "Extracted 5 pages",
      "metadata": {"page_count": 5},
      "created_at": "2024-03-06T14:50:33.000Z"
    },
    {
      "level": "INFO",
      "step": "job_completed",
      "message": "Job completed with status: COMPLETED",
      "metadata": {},
      "created_at": "2024-03-06T14:50:46.420Z"
    }
  ]
}
```

---

## 5. Get Document Details

Retrieve information about an uploaded document.

### Request
```bash
curl -X GET "http://localhost:8000/api/v1/documents/{document_id}"
```

### Response
```json
{
  "id": 1,
  "user_id": 1,
  "filename": "20240306_145030_abc123_document.pdf",
  "original_filename": "document.pdf",
  "file_size": 245680,
  "mime_type": "application/pdf",
  "checksum": "a1b2c3d4e5f6...",
  "page_count": 5,
  "title": "Sample Document",
  "author": "John Doe",
  "is_processed": true,
  "created_at": "2024-03-06T14:50:30.123Z",
  "updated_at": "2024-03-06T14:50:46.420Z"
}
```

---

## 6. List Documents

Get a paginated list of documents for a user.

### Request
```bash
curl -X GET "http://localhost:8000/api/v1/documents/?user_id=1&skip=0&limit=10"
```

### Response
```json
[
  {
    "id": 3,
    "filename": "latest_document.pdf",
    "file_size": 156789,
    "page_count": 3,
    "is_processed": true,
    "created_at": "2024-03-06T15:30:00.000Z",
    ...
  },
  {
    "id": 2,
    "filename": "another_document.pdf",
    "file_size": 234567,
    "page_count": 7,
    "is_processed": true,
    "created_at": "2024-03-06T14:00:00.000Z",
    ...
  },
  {
    "id": 1,
    "filename": "document.pdf",
    "file_size": 245680,
    "page_count": 5,
    "is_processed": true,
    "created_at": "2024-03-06T14:50:30.000Z",
    ...
  }
]
```

---

## 7. List Jobs

Get a list of jobs with optional filters.

### Request
```bash
# All jobs
curl -X GET "http://localhost:8000/api/v1/jobs/"

# Filter by user
curl -X GET "http://localhost:8000/api/v1/jobs/?user_id=1"

# Filter by status
curl -X GET "http://localhost:8000/api/v1/jobs/?status=COMPLETED"

# Combined filters with pagination
curl -X GET "http://localhost:8000/api/v1/jobs/?user_id=1&status=COMPLETED&skip=0&limit=20"
```

### Response
```json
[
  {
    "id": 3,
    "job_id": "uuid-3",
    "user_id": 1,
    "document_id": 3,
    "status": "COMPLETED",
    "execution_time_ms": 12000,
    "created_at": "2024-03-06T15:30:00.000Z",
    ...
  },
  {
    "id": 2,
    "job_id": "uuid-2",
    "user_id": 1,
    "document_id": 2,
    "status": "COMPLETED",
    "execution_time_ms": 18500,
    "created_at": "2024-03-06T14:00:00.000Z",
    ...
  }
]
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "File must be a PDF"
}
```

### 404 Not Found
```json
{
  "detail": "Job not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "error_type": "ValueError"
}
```

---

## Polling Pattern

For long-running jobs, use this polling pattern:

```python
import requests
import time

# Upload document
response = requests.post(
    'http://localhost:8000/api/v1/documents/upload',
    files={'file': open('document.pdf', 'rb')},
    data={'recipient_email': 'test@example.com', 'user_id': 1}
)
job_id = response.json()['job_id']

# Poll for completion
max_attempts = 60  # 5 minutes with 5-second intervals
for attempt in range(max_attempts):
    status_response = requests.get(
        f'http://localhost:8000/api/v1/jobs/{job_id}/status'
    )
    status_data = status_response.json()
    
    if status_data['status'] in ['COMPLETED', 'FAILED']:
        print(f"Job {status_data['status']}")
        if status_data['status'] == 'COMPLETED':
            # Get detailed results
            details = requests.get(
                f'http://localhost:8000/api/v1/jobs/{job_id}'
            )
            print(details.json())
        break
    
    print(f"Status: {status_data['status']}, Progress: {status_data['progress']}%")
    time.sleep(5)
```

---

## Rate Limits

Currently no rate limits are enforced in development mode. In production:
- API requests: 100 requests/minute per IP
- Document uploads: 10 uploads/minute per user
- Job creation: 20 jobs/minute per user

---

## Best Practices

1. **Always check job status before requesting detailed results**
2. **Use polling with increasing intervals** (exponential backoff)
3. **Handle all error responses appropriately**
4. **Store job_id for tracking and debugging**
5. **Validate file types and sizes before uploading**
6. **Use the quick status endpoint for frequent polling**
7. **Retrieve detailed results only when needed**

---

## Support

For API questions or issues:
- Check interactive docs: http://localhost:8000/docs
- Review logs using the execution_logs in job details
- Contact: himanshu.dixit@trinetralabs.ai
