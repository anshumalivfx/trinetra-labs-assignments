# Quick Start Guide - Web Interface

## 🚀 Getting Started in 5 Minutes

This guide will help you get started with the AI Document Processing System's web interface.

## Prerequisites

Ensure the backend services are running. If not, start them:

```bash
# Option 1: Using Docker (Recommended)
docker-compose up --build

# Option 2: Local Development
python -m app.main
```

## Step 1: Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8000/
```

You should see a beautiful, modern interface with a gradient purple background.

## Step 2: Upload Your First Document

1. **Click on "Select PDF File"** or drag and drop a PDF into the file input area
2. **Enter Recipient Email**: Type the email address where you want to send the generated email
3. **User ID**: Leave as default (1) or enter your user ID
4. **Click "Upload & Process"**

## Step 3: Track Your Job

After uploading, you'll see:
- ✅ A success message with your Job ID
- 📊 Automatic job details display
- 🔄 Real-time status updates (polls every 2 seconds)

### Job Status Indicators

- 🟡 **PENDING**: Job is queued
- 🔵 **PROCESSING**: AI agents are working
- 🟢 **COMPLETED**: Success! Email sent
- 🔴 **FAILED**: Something went wrong

## Step 4: View Job Details

The job details panel shows:
- **Execution Time**: How long the job took
- **Agent Outputs**: What each AI agent discovered
  - PDF Analyzer: Document insights
  - Email Composer: Generated email content
  - Email Delivery: Send status
- **Email Records**: Details about sent emails
- **Execution Logs**: Step-by-step processing history

## Step 5: Check Recent Jobs

Scroll down to the "Recent Jobs" section to:
- See your last 10 jobs
- Click any job to view its details
- Track multiple documents at once

## Pro Tips

### 💡 Keyboard Shortcuts

- **Ctrl/Cmd + Enter** while in Job ID input: Check job status

### 🎯 Best Practices

1. **Use Valid Emails**: Ensure recipient email is correct
2. **PDF Quality**: Use clear, text-based PDFs for best results
3. **Monitor Console**: Open browser DevTools (F12) to see API calls
4. **Bookmark Job IDs**: Save important job IDs for later reference

### 🔍 Manual Job Lookup

If you have a Job ID from an API call:
1. Paste it into the "Job Status" input field
2. Click "Check Status"
3. View complete job details

## Testing the System

### Test with Sample Data

Create a simple test PDF:
```bash
# On macOS/Linux, create a sample PDF
echo "This is a test document for AI processing." | ps2pdf - test.pdf
```

Then upload this through the web interface.

### Verify System Health

Click the "Check System Health" button to verify:
- ✅ API is running
- ✅ Database is connected
- ✅ Redis is operational

## Common Scenarios

### Scenario 1: Process Multiple Documents

1. Upload first document
2. Note the Job ID
3. Upload another document immediately
4. Both will process concurrently
5. Check both in "Recent Jobs"

### Scenario 2: Monitor Long-Running Jobs

1. Upload a large PDF
2. Watch the status change:
   - PENDING → PROCESSING → COMPLETED
3. View execution logs to see progress

### Scenario 3: Handle Errors

If a job fails:
1. Check the error message in job details
2. Verify your backend logs
3. Common issues:
   - Invalid PDF format
   - Email provider not configured
   - AI API rate limits

## API vs Web Interface

| Feature | Web Interface | API (curl/code) |
|---------|--------------|-----------------|
| Ease of Use | ⭐⭐⭐⭐⭐ Very Easy | ⭐⭐⭐ Moderate |
| Automation | ❌ Manual only | ✅ Full automation |
| Visual Feedback | ✅ Real-time UI | ❌ Text only |
| Job Tracking | ✅ Automatic | ⚠️ Manual polling |
| Best For | Testing, demos | Production, bulk |

## Troubleshooting

### Problem: Page Doesn't Load

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it
docker-compose up
```

### Problem: Upload Button Stuck

**Possible causes**:
1. Backend not responding
2. File too large
3. Network issue

**Solution**:
1. Refresh the page
2. Try a smaller file
3. Check browser console (F12)

### Problem: Job Status Not Updating

**Solution**:
1. Click "Check Status" manually
2. Refresh the page
3. Check browser console for errors

### Problem: No Recent Jobs

**Solution**:
1. Upload a document first
2. Check localStorage isn't cleared
3. Try different browser

## Next Steps

Now that you're familiar with the web interface:

1. **Read API Documentation**: http://localhost:8000/docs
2. **Review Examples**: See [API_EXAMPLES.md](../API_EXAMPLES.md)
3. **Integrate via API**: Use the API for production workflows
4. **Customize Frontend**: Edit files in `frontend/` directory

## Support

- **Frontend Issues**: See [frontend/README.md](README.md)
- **API Issues**: Check main [README.md](../README.md)
- **Backend Logs**: Run `docker-compose logs -f`

## Demo Workflow

Try this complete workflow:

```
1. Open http://localhost:8000/
2. Click "Check System Health" → Should show all green
3. Upload a PDF (e.g., a resume or article)
4. Enter your email as recipient
5. Click "Upload & Process"
6. Watch it process in real-time
7. Check "Recent Jobs" to see it listed
8. Review agent outputs to see AI analysis
9. Check your email for the generated message
10. Upload another document to test concurrency
```

## Screenshots Guide

### Main Interface
- Header with gradient background
- Upload section with file input
- Job status tracker
- Recent jobs list
- System health monitor

### Job Details View
- Status badge (color-coded)
- Execution metrics
- Agent outputs (JSON display)
- Email records
- Execution logs timeline

### Success State
- Green success message
- Job ID displayed
- Real-time status updates
- Toast notification

### Error State
- Red error message
- Detailed error information
- Retry option available

---

**Need Help?** Check the [main README](../README.md) or [API documentation](../API_EXAMPLES.md)
