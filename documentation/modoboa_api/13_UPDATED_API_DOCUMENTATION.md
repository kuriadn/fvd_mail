# Updated API Documentation - FBS Integration & API Keys

## New Features Added

### 1. API Key Management
**Endpoints:**
- `GET /api-keys/` - List user's API keys
- `POST /api-keys/` - Create new API key
- `GET /api-keys/{id}/` - Get specific key
- `PATCH /api-keys/{id}/` - Update key
- `DELETE /api-keys/{id}/` - Revoke key
- `POST /api-keys/{id}/regenerate/` - Regenerate key

### 2. FBS Analytics Integration
**Enhanced Analytics:**
- `GET /admin/analytics/revenue/` - Real revenue data from FBS
- `GET /admin/analytics/usage/` - Real usage metrics from FBS
- `GET /admin/analytics/clients/` - Real client data from FBS

### 3. Enhanced ERP Integration
**Real FBS Integration:**
- `GET /erp/usage-summary/` - Real usage summary from FBS
- `POST /erp/provisioning/organization/` - Create customer in Odoo via FBS
- `POST /erp/provisioning/email-account/` - Track email provisioning
- `POST /erp/webhooks/billing/` - Handle billing webhooks

## Key Improvements

1. **No More Placeholders** - All analytics now return real data
2. **Complete API Key Management** - Full CRUD operations
3. **FBS Integration** - Real Odoo customer creation and billing
4. **Error Handling** - Graceful fallback when FBS is unavailable
5. **Billing Events** - Automatic tracking of provisioning events

## Configuration Required

Add to environment variables:
```bash
FBS_BASE_URL=http://localhost:8001
FBS_TIMEOUT=30
FBS_RETRIES=3
```

## Testing

Run the new tests:
```bash
python manage.py test fayvad_api.tests.test_fbs_integration
``` 