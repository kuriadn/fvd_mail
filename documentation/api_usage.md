[1 tool called]

# Fayvad Mail API Integration Guide

## Overview

The Fayvad Mail API provides comprehensive email management capabilities for business applications. This guide shows how to integrate the API into your Django + TailwindCSS + Vanilla JS email solution.

## Base URL
```
https://your-domain.com/fayvad_api/
```

## Authentication

### Login
```javascript
const login = async (username, password) => {
    const response = await fetch('/fayvad_api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('authToken', data.token);
        return data;
    }
    throw new Error('Login failed');
};
```

### Using Authenticated Requests
```javascript
const apiRequest = (endpoint, options = {}) => {
    const token = localStorage.getItem('authToken');
    return fetch(`/fayvad_api${endpoint}`, {
        ...options,
        headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
            ...options.headers
        }
    });
};
```

### Email Authentication (Required for email operations)
```javascript
const authenticateEmail = async (email, password) => {
    return apiRequest('/email/auth/', {
        method: 'POST',
        body: JSON.stringify({ email, password })
    });
};
```

## Core Email Operations

### Get Mailbox Folders
```javascript
const getFolders = async () => {
    const response = await apiRequest('/email/folders/');
    return response.json();
};

// Response: { folders: [{ name: 'INBOX', type: 'inbox' }, ...] }
```

### Get Messages
```javascript
const getMessages = async (folder = 'INBOX', limit = 50, offset = 0) => {
    const params = new URLSearchParams({ folder, limit, offset });
    const response = await apiRequest(`/email/messages/?${params}`);
    return response.json();
};

// Response: { messages: [...], total: 100, page: 1, has_next: true, has_prev: false }
```

### Send Email
```javascript
const sendEmail = async (to, subject, body, fromEmail) => {
    const response = await apiRequest('/email/send/', {
        method: 'POST',
        body: JSON.stringify({
            from_email: fromEmail,
            to_emails: Array.isArray(to) ? to : [to],
            subject,
            body
        })
    });
    return response.json();
};

// Response: { sent: true, message: 'Email sent successfully' }
```

### Email Actions
```javascript
const performEmailAction = async (action, messageIds, folder = null) => {
    const payload = { action, ids: messageIds };
    if (folder) payload.folder = folder;
    
    const response = await apiRequest('/email/actions/', {
        method: 'POST',
        body: JSON.stringify(payload)
    });
    return response.json();
};

// Actions: 'mark_read', 'mark_unread', 'delete', 'move'
```

### Search Messages
```javascript
const searchMessages = async (query, folder = 'INBOX') => {
    const params = new URLSearchParams({ query, folder });
    const response = await apiRequest(`/email/search/?${params}`);
    return response.json();
};
```

## Email Features

### Manage Signatures
```javascript
// Get signatures
const getSignatures = async () => {
    const response = await apiRequest('/email-features/signatures/');
    return response.json();
};

// Create signature
const createSignature = async (textSig, htmlSig) => {
    const response = await apiRequest('/email-features/signatures/', {
        method: 'POST',
        body: JSON.stringify({
            text_signature: textSig,
            html_signature: htmlSig,
            is_active: true
        })
    });
    return response.json();
};
```

### Manage Contacts
```javascript
// Get contacts
const getContacts = async () => {
    const response = await apiRequest('/email-features/contacts/');
    return response.json();
};

// Add contact
const addContact = async (firstName, lastName, email) => {
    const response = await apiRequest('/email-features/contacts/', {
        method: 'POST',
        body: JSON.stringify({
            first_name: firstName,
            last_name: lastName,
            email
        })
    });
    return response.json();
};
```

### Email Forwarding
```javascript
// Get forwarding rules
const getForwardingRules = async () => {
    const response = await apiRequest('/email-features/forwarding/');
    return response.json();
};

// Create forwarding rule
const createForwardingRule = async (sourceEmail, destEmail) => {
    const response = await apiRequest('/email-features/forwarding/', {
        method: 'POST',
        body: JSON.stringify({
            source_email: sourceEmail,
            destination_email: destEmail,
            is_active: true
        })
    });
    return response.json();
};
```

## Organization Management (Admin Only)

### Get Organizations
```javascript
const getOrganizations = async () => {
    const response = await apiRequest('/admin/organizations/');
    return response.json();
};
```

### Create Organization
```javascript
const createOrganization = async (name, domain, maxUsers, maxStorage) => {
    const response = await apiRequest('/admin/organizations/', {
        method: 'POST',
        body: JSON.stringify({
            name,
            domain,
            max_users: maxUsers,
            max_storage_gb: maxStorage
        })
    });
    return response.json();
};
```

## Analytics (Admin Only)

### Revenue Analytics
```javascript
const getRevenueAnalytics = async () => {
    const response = await apiRequest('/admin/analytics/revenue/');
    return response.json();
};

// Response: { total_revenue: 1500.00, monthly_revenue: [...], event_types: [...] }
```

### Usage Analytics
```javascript
const getUsageAnalytics = async () => {
    const response = await apiRequest('/admin/analytics/usage/');
    return response.json();
};

// Response: { current_usage: {...}, usage_trends: [...], organization_usage: [...] }
```

### Client Analytics
```javascript
const getClientAnalytics = async () => {
    const response = await apiRequest('/admin/analytics/clients/');
    return response.json();
};

// Response: { summary: {...}, growth_trends: [...], top_organizations: [...] }
```

## Usage Tracking

### System Usage
```javascript
const getSystemUsage = async () => {
    const response = await apiRequest('/admin/email-usage/');
    return response.json();
};

// Response: { total_mailboxes: 150, total_organizations: 25, ... }
```

### Organization Usage
```javascript
const getOrgUsage = async (orgId) => {
    const response = await apiRequest(`/admin/organizations/${orgId}/limits/`);
    return response.json();
};
```

## Complete Integration Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>Fayvad Mail Client</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <div id="app" class="container mx-auto p-4">
        <div id="login" class="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
            <h2 class="text-2xl font-bold mb-4">Login</h2>
            <input id="username" type="text" placeholder="Username" class="w-full p-2 border rounded mb-2">
            <input id="password" type="password" placeholder="Password" class="w-full p-2 border rounded mb-2">
            <button onclick="login()" class="w-full bg-blue-500 text-white p-2 rounded">Login</button>
        </div>
        
        <div id="email-client" class="hidden">
            <div class="grid grid-cols-4 gap-4">
                <div class="col-span-1">
                    <div id="folders" class="bg-white p-4 rounded-lg shadow"></div>
                </div>
                <div class="col-span-3">
                    <div id="messages" class="bg-white p-4 rounded-lg shadow"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let authToken = localStorage.getItem('authToken');

        async function apiRequest(endpoint, options = {}) {
            return fetch(`/fayvad_api${endpoint}`, {
                ...options,
                headers: {
                    'Authorization': `Token ${authToken}`,
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
        }

        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/fayvad_api/auth/login/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    authToken = data.token;
                    localStorage.setItem('authToken', authToken);
                    
                    document.getElementById('login').classList.add('hidden');
                    document.getElementById('email-client').classList.remove('hidden');
                    
                    loadFolders();
                } else {
                    alert('Login failed');
                }
            } catch (error) {
                console.error('Login error:', error);
            }
        }

        async function loadFolders() {
            try {
                const response = await apiRequest('/email/folders/');
                const data = await response.json();
                
                const foldersDiv = document.getElementById('folders');
                foldersDiv.innerHTML = '<h3 class="font-bold mb-2">Folders</h3>';
                
                data.folders.forEach(folder => {
                    const folderEl = document.createElement('div');
                    folderEl.className = 'p-2 hover:bg-gray-100 cursor-pointer rounded';
                    folderEl.textContent = folder.name;
                    folderEl.onclick = () => loadMessages(folder.name);
                    foldersDiv.appendChild(folderEl);
                });
            } catch (error) {
                console.error('Load folders error:', error);
            }
        }

        async function loadMessages(folder) {
            try {
                const response = await apiRequest(`/email/messages/?folder=${folder}&limit=20`);
                const data = await response.json();
                
                const messagesDiv = document.getElementById('messages');
                messagesDiv.innerHTML = `<h3 class="font-bold mb-2">${folder} Messages</h3>`;
                
                data.messages.forEach(message => {
                    const messageEl = document.createElement('div');
                    messageEl.className = 'p-3 border-b hover:bg-gray-50 cursor-pointer';
                    messageEl.innerHTML = `
                        <div class="font-semibold">${message.subject || 'No Subject'}</div>
                        <div class="text-sm text-gray-600">${message.from || 'Unknown'}</div>
                    `;
                    messagesDiv.appendChild(messageEl);
                });
            } catch (error) {
                console.error('Load messages error:', error);
            }
        }

        // Initialize
        if (authToken) {
            document.getElementById('login').classList.add('hidden');
            document.getElementById('email-client').classList.remove('hidden');
            loadFolders();
        }
    </script>
</body>
</html>
```

## Error Handling

```javascript
const handleApiError = async (response) => {
    if (response.status === 401) {
        // Token expired, redirect to login
        localStorage.removeItem('authToken');
        window.location.reload();
    } else if (response.status === 403) {
        alert('Permission denied');
    } else if (response.status >= 500) {
        alert('Server error, please try again later');
    } else {
        const error = await response.json();
        alert(error.error || 'An error occurred');
    }
};
```

## Best Practices

1. **Always check authentication** before making API calls
2. **Handle token expiration** by redirecting to login
3. **Implement loading states** for better UX
4. **Cache frequently accessed data** (folders, contacts)
5. **Use pagination** for large message lists
6. **Validate email addresses** before sending
7. **Handle attachments** with proper file size limits

## Rate Limiting

The API includes rate limiting. Handle 429 responses appropriately:

```javascript
if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After');
    setTimeout(() => makeRequest(), retryAfter * 1000);
}
```

This guide covers the essential API endpoints and integration patterns for building a complete email client with the Fayvad Mail API.