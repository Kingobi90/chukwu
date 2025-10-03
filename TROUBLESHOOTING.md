# Troubleshooting Login Errors

## Error 422: Unprocessable Entity

This usually means the request format is incorrect. Here's what to check:

### ✅ Correct Request Format

The backend expects:
```json
{
  "moodle_token": "your_token_here"
}
```

### Common Issues:

1. **Empty Token**
   - Make sure you actually entered a token
   - The input field should not be empty

2. **Wrong Field Name**
   - Must be `moodle_token` (with underscore)
   - NOT `moodleToken` or `token`

3. **Token Format**
   - Should be a long string of letters and numbers
   - Example: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

---

## Error 401: Unauthorized

This means the token was sent correctly but Moodle rejected it.

### Solutions:

1. **Get a Fresh Token**
   - Go to https://moodle.concordia.ca/user/security.php
   - Delete old tokens
   - Create a new one

2. **Check Token Permissions**
   - Service must be: **"Moodle mobile web service"**
   - Make sure it's enabled

3. **Copy Token Correctly**
   - No extra spaces
   - No line breaks
   - Copy the entire string

---

## Error 404: Not Found

The Moodle server endpoint might be wrong.

### Check:
- Moodle URL in `.env`: `https://moodle.concordia.ca`
- The webservice must be enabled on Moodle

---

## Network Error

### Possible Causes:

1. **Backend Not Running**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/health
   ```

2. **Wrong Port**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000

3. **CORS Issue**
   - Backend `.env` should have:
   ```
   CORS_ORIGINS=["http://localhost:5173"]
   ```

---

## How to Test Manually

### Test Backend Directly:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"moodle_token":"YOUR_REAL_TOKEN"}'
```

### Expected Responses:

**Success (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

**Invalid Token (401):**
```json
{
  "detail": "Invalid Moodle token or connection error: ..."
}
```

**Wrong Format (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "moodle_token"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Quick Fixes

### 1. Restart Backend
```bash
pkill -f uvicorn
cd backend && ./venv/bin/uvicorn app.main:app --reload --port 8000
```

### 2. Clear Browser Cache
- Hard refresh: Cmd + Shift + R (Mac)
- Or open in Incognito mode

### 3. Check Services
```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:5173
```

---

## Still Not Working?

### Check Browser Console
1. Open DevTools (F12)
2. Go to Console tab
3. Look for the actual error message
4. Check Network tab for the request details

### Verify Token Format
Your token should look like:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

NOT like:
- `test123` ❌
- `my_token` ❌
- Empty string ❌

---

**Remember: You need a REAL Moodle API token from https://moodle.concordia.ca/user/security.php**
