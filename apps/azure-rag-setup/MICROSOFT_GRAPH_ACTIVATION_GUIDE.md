# 🚀 MICROSOFT GRAPH API ACTIVATION GUIDE

**Date:** January 17, 2025
**Status:** Ready to activate Microsoft Graph API
**Cost:** $0 (FREE within Microsoft 365 license)

---

## 💰 COST BREAKDOWN

### **Microsoft Graph API Costs: $0**

| Service                 | Cost         | Notes                    |
| ----------------------- | ------------ | ------------------------ |
| **Microsoft Graph API** | **$0/month** | FREE within M365 license |
| **SharePoint Access**   | **$0/month** | Included in M365         |
| **OneDrive Access**     | **$0/month** | Included in M365         |
| **Exchange Access**     | **$0/month** | Included in M365         |
| **Teams Access**        | **$0/month** | Included in M365         |
| **Calendar/Contacts**   | **$0/month** | Included in M365         |

### **Why Microsoft Graph is FREE:**

1. **Included in Microsoft 365 License**

   - SharePoint, OneDrive, Exchange access
   - Teams, Calendar, Contacts access
   - No additional charges for tenant users

2. **Generous Rate Limits**

   - 10,000 requests per day (free)
   - 1,000 requests per 10 minutes (free)
   - No monetary charges for overages

3. **Enterprise Features**
   - Advanced security features
   - Compliance features
   - All included in M365 E3/E5 licenses

---

## 🛠️ ACTIVATION STEPS

### **Step 1: Set Up Environment Variables**

Create a `.env` file with your Microsoft 365 credentials:

```bash
# Microsoft 365 Configuration
M365_CLIENT_ID=your-app-registration-id
M365_TENANT_ID=your-tenant-id
M365_USE_DELEGATED_AUTH=true

# Optional: For application permissions
# M365_CLIENT_SECRET=your-client-secret
```

### **Step 2: Get Microsoft 365 Credentials**

#### **Option A: Use Existing App Registration**

If you already have an Azure AD app registration:

1. Go to Azure Portal → Azure Active Directory → App registrations
2. Find your existing app
3. Copy the Application (client) ID
4. Copy the Directory (tenant) ID

#### **Option B: Create New App Registration**

1. Go to Azure Portal → Azure Active Directory → App registrations
2. Click "New registration"
3. Name: "M365 RAG Indexer"
4. Supported account types: "Accounts in this organizational directory only"
5. Click "Register"
6. Copy the Application (client) ID and Directory (tenant) ID

### **Step 3: Configure API Permissions**

1. Go to your app registration → API permissions
2. Click "Add a permission"
3. Select "Microsoft Graph"
4. Select "Delegated permissions"
5. Add these permissions:
   - `Sites.Read.All` - Read SharePoint sites
   - `Files.Read.All` - Read files in OneDrive and SharePoint
   - `Mail.Read` - Read emails
   - `User.Read.All` - Read user information
   - `Calendars.Read` - Read calendars
   - `Contacts.Read` - Read contacts
6. Click "Grant admin consent" (requires Global Admin)

### **Step 4: Test the Connection**

```bash
# Test Microsoft Graph API connection
python3 -c "
from m365_auth import M365Auth
auth = M365Auth()
if auth.test_connection():
    print('✅ Microsoft Graph API connected successfully!')
else:
    print('❌ Connection failed - check credentials')
"
```

---

## 🎯 WHAT YOU GET WITH MICROSOFT GRAPH

### **1. SharePoint Integration**

- Access to all SharePoint sites
- Document libraries and files
- Metadata and permissions
- **Cost:** $0 (FREE)

### **2. OneDrive Integration**

- Personal OneDrive files
- Shared files and folders
- File metadata and versions
- **Cost:** $0 (FREE)

### **3. Exchange Integration**

- User emails and attachments
- Calendar events
- Contact information
- **Cost:** $0 (FREE)

### **4. Teams Integration**

- Teams chat messages
- Teams files and channels
- Meeting recordings
- **Cost:** $0 (FREE)

### **5. Advanced Features**

- User enumeration
- Permission management
- Content search
- **Cost:** $0 (FREE)

---

## 📊 RATE LIMITS (NOT COST LIMITS)

### **Microsoft Graph API Limits:**

- **10,000 requests per day** (free)
- **1,000 requests per 10 minutes** (free)
- **No monetary charges** for overages
- **Only throttling** (not billing)

### **Typical Usage:**

- **Small Organization:** 1,000-5,000 requests/day
- **Medium Organization:** 5,000-10,000 requests/day
- **Large Organization:** May need to optimize queries

---

## 🔧 IMPLEMENTATION OPTIONS

### **Option 1: Full M365 Integration**

```bash
# Enable all M365 services
python3 m365_sharepoint_indexer.py
python3 m365_onedrive_indexer.py
python3 m365_exchange_indexer.py
python3 m365_teams_indexer.py
python3 m365_calendar_indexer.py
python3 m365_contacts_indexer.py
```

### **Option 2: Selective Integration**

```bash
# Enable only specific services
python3 m365_sharepoint_indexer.py  # SharePoint only
python3 m365_onedrive_indexer.py   # OneDrive only
```

### **Option 3: Scheduled Integration**

```bash
# Set up cron job for regular syncing
crontab -e
# Add: 0 2 * * * /path/to/m365_sync.sh
```

---

## 🎉 BENEFITS OF ACTIVATING MICROSOFT GRAPH

### **Immediate Benefits:**

- ✅ Access to all M365 data
- ✅ Real-time document indexing
- ✅ User and permission management
- ✅ Advanced search capabilities
- ✅ **Cost: $0 (FREE)**

### **Long-term Benefits:**

- ✅ Comprehensive knowledge base
- ✅ Advanced AI capabilities
- ✅ Enterprise-grade security
- ✅ Scalable architecture
- ✅ **Cost: $0 (FREE)**

---

## 🚀 QUICK START

### **1. Create Environment File**

```bash
cat > .env << EOF
M365_CLIENT_ID=your-app-id
M365_TENANT_ID=your-tenant-id
M365_USE_DELEGATED_AUTH=true
EOF
```

### **2. Test Connection**

```bash
python3 m365_auth.py
```

### **3. Start Indexing**

```bash
python3 m365_sharepoint_indexer.py
```

### **4. Monitor Progress**

```bash
tail -f m365_sync.log
```

---

## 📞 NEXT STEPS

**To activate Microsoft Graph API:**

1. **Get credentials** from Azure AD app registration
2. **Create `.env` file** with credentials
3. **Test connection** with `python3 m365_auth.py`
4. **Start indexing** with your preferred services
5. **Monitor usage** to stay within rate limits

**Total Cost:** $0 (FREE within Microsoft 365 license)
**Rate Limits:** 10,000 requests/day (free)
**No overage charges:** Only throttling, not billing

Would you like me to help you set up the Microsoft Graph API integration?
