#!/bin/bash
# Quick test script to verify the API is working

echo "🧪 Testing AI Agent Orchestration System"
echo "========================================"

# Check if server is running
echo -e "\n1. Checking health endpoint..."
curl -s http://localhost:8000/health | jq .

# Test document upload (requires a sample PDF)
if [ -f "sample.pdf" ]; then
    echo -e "\n2. Testing document upload..."
    RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/documents/upload" \
      -F "file=@sample.pdf" \
      -F "recipient_email=test@example.com" \
      -F "user_id=1")
    
    echo "$RESPONSE" | jq .
    
    # Extract job_id
    JOB_ID=$(echo "$RESPONSE" | jq -r '.job_id')
    
    if [ "$JOB_ID" != "null" ] && [ -n "$JOB_ID" ]; then
        echo -e "\n3. Checking job status..."
        sleep 2
        curl -s "http://localhost:8000/api/v1/jobs/$JOB_ID/status" | jq .
    fi
else
    echo "⚠️  No sample.pdf found. Skipping upload test."
fi

echo -e "\n\n✅ Test completed!"
