# Frontend Documentation

## Overview

This is a modern, responsive web interface for the AI Document Processing System. It provides an intuitive way to interact with the backend API for uploading PDFs, tracking jobs, and monitoring system health.

## Features

### 🚀 Key Features

- **Document Upload**: Drag-and-drop PDF upload with real-time validation
- **Job Tracking**: Real-time job status monitoring with automatic updates
- **Recent Jobs**: View and track your recent document processing jobs
- **System Health**: Monitor the health of the backend services
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Toast Notifications**: User-friendly feedback for all operations
- **Local Storage**: Automatically saves your recent job IDs

### 📋 UI Components

#### 1. Upload Section
- Select PDF files for processing
- Enter recipient email address
- Specify user ID
- Real-time upload progress indicator
- Instant feedback with job ID

#### 2. Job Status Section
- Search for jobs by ID
- View detailed job information including:
  - Current status (Pending, Processing, Completed, Failed)
  - Execution time
  - Retry count
  - Agent outputs
  - Email records
  - Execution logs

#### 3. Recent Jobs Section
- Quick access to your 10 most recent jobs
- Click any job to view details
- Status badges for quick visual feedback
- Automatic refresh after operations

#### 4. System Health Section  
- Check backend service status
- Monitor database connectivity
- Verify Redis connection
- View environment information

## Getting Started

### Prerequisites

The backend API must be running on `http://localhost:8000`

### Running the Application

1. **Start the Backend**:
   ```bash
   # From the project root
   docker-compose up
   # Or
   python -m app.main
   ```

2. **Access the Frontend**:
   Open your browser and navigate to:
   ```
   http://localhost:8000/
   ```

3. **Alternative Access**:
   You can also open the HTML file directly:
   ```bash
   # From the frontend directory
   open index.html
   # This will work for static viewing, but you'll need the backend running for API calls
   ```

## Usage Guide

### Uploading a Document

1. Click on **"Select PDF File"** or drag and drop a PDF
2. Enter the recipient email address
3. Optionally adjust the User ID
4. Click **"Upload & Process"**
5. Wait for the upload confirmation with Job ID
6. The job will automatically start polling for status updates

### Tracking a Job

1. **Automatic**: After uploading, the job details will automatically appear
2. **Manual**: Enter a Job ID in the "Job Status" section and click "Check Status"
3. **From Recent Jobs**: Click any job in the "Recent Jobs" list

### Understanding Job Status

- 🟡 **Pending**: Job is queued for processing
- 🔵 **Processing**: Job is currently being executed by agents
- 🟢 **Completed**: Job finished successfully
- 🔴 **Failed**: Job encountered an error

### Keyboard Shortcuts

- `Ctrl/Cmd + Enter` when focused on Job ID input: Check job status

## Technical Details

### API Integration

The frontend communicates with the backend using REST API:

- **Base URL**: `http://localhost:8000`
- **API Version**: `/api/v1`

### Key Endpoints Used

```
POST /api/v1/documents/upload    - Upload PDF documents
GET  /api/v1/jobs/{job_id}       - Get job details
GET  /health                     - Check system health
```

### Data Storage

The application uses `localStorage` to persist:
- Recent job IDs (last 10 jobs)
- User preferences (if any)

### Auto-Polling

When a document is uploaded, the frontend automatically polls the job status every 2 seconds for up to 60 attempts (2 minutes) to provide real-time updates.

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # Complete styling with responsive design
├── app.js          # JavaScript for API interactions and UI logic
└── README.md       # This file
```

## Customization

### Changing API URL

Edit `app.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### Adjusting Polling Interval

Edit `app.js`:
```javascript
setTimeout(poll, 2000); // Change 2000 to desired milliseconds
```

### Styling

All styles are in `styles.css` with CSS custom properties (variables) for easy theming:

```css
:root {
    --primary-color: #4f46e5;
    --success-color: #10b981;
    --error-color: #ef4444;
    /* ... more variables */
}
```

## Browser Compatibility

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Features in Detail

### Responsive Design

The interface adapts to different screen sizes:
- Desktop: Multi-column grid layout
- Tablet: Adjusted layout with touch-friendly controls
- Mobile: Single-column layout, optimized for small screens

### Error Handling

- Network errors are caught and displayed with user-friendly messages
- API errors show detailed information
- File validation prevents uploading non-PDF files
- Toast notifications for quick feedback

### Accessibility

- Semantic HTML structure
- Keyboard navigation support
- ARIA labels where appropriate
- Clear visual feedback for all interactions

## Troubleshooting

### Backend Connection Issues

**Problem**: "Failed to fetch" or "Network error"

**Solution**:
1. Ensure the backend is running on `http://localhost:8000`
2. Check if CORS is properly configured in the backend
3. Verify your firewall/antivirus isn't blocking the connection

### Jobs Not Appearing

**Problem**: Recent jobs list is empty

**Solution**:
1. Try uploading a new document
2. Check browser's localStorage (not cleared)
3. Verify the job IDs are valid

### Upload Fails

**Problem**: Upload button stays in loading state

**Solution**:
1. Check file is a valid PDF
2. Ensure recipient email is valid
3. Check backend logs for errors
4. Try with a smaller PDF file first

### Polling Stops

**Problem**: Job status doesn't update

**Solution**:
1. Manually click "Check Status" to refresh
2. Check if backend is still running
3. Look at browser console for errors

## Development

### Adding New Features

1. **HTML**: Add structure in `index.html`
2. **CSS**: Add styles in `styles.css`
3. **JavaScript**: Add functionality in `app.js`

### Testing

1. Test with various PDF files (small, large, multi-page)
2. Test error scenarios (invalid files, backend down)
3. Test on different browsers and devices
4. Test keyboard navigation

## Future Enhancements

Potential features for future versions:
- 📊 Dashboard with analytics
- 📈 Job history with filtering and search
- 🔔 Real-time WebSocket updates
- 👥 User authentication and profiles
- 📤 Bulk document upload
- 📥 Download processed documents
- 🎨 Theme customization (dark mode)
- 🌐 Internationalization (i18n)

## Support

For issues or questions:
1. Check the main `README.md` in the project root
2. Review the `API_EXAMPLES.md` for API documentation
3. Check backend logs for detailed error information

## License

Same as the main project.
