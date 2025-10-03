# Test Login - Step by Step

## ✅ Backend is Working

CORS is configured correctly:
```
access-control-allow-origin: http://localhost:5173 ✅
```

Login endpoint returns 200 OK ✅

---

## 🔍 Where is the 403 Coming From?

The 403 error is happening AFTER login, likely when the frontend tries to:
1. Call `/auth/me` to get user info
2. Or navigate to a protected route

---

## 🐛 Debug in Browser

### Step 1: Open Browser DevTools
1. Go to http://localhost:5173
2. Press F12
3. Go to **Network** tab
4. Check "Preserve log"

### Step 2: Try Login
1. Enter token: `a6f3e36db214f134c20acc2d8d6b8af6`
2. Click Login
3. Watch the Network tab

### Step 3: Find the 403 Request
Look for a request with status 403. Click on it and check:

**Request:**
- URL: What endpoint is it calling?
- Headers: Is `Authorization: Bearer <token>` present?
- Origin: Is it `http://localhost:5173`?

**Response:**
- What's the error message?
- Headers: Is `access-control-allow-origin` present?

---

## 🔧 Common Issues

### Issue 1: Token Not Being Sent
**Check:** Request Headers → Authorization header missing

**Fix:** The frontend might not be storing the token correctly

### Issue 2: Wrong Endpoint
**Check:** Request URL is not `http://localhost:8000/api/v1/...`

**Fix:** Frontend .env has wrong VITE_API_URL

### Issue 3: CORS Preflight Failing
**Check:** See an OPTIONS request before the actual request

**Fix:** Backend needs to handle OPTIONS requests

### Issue 4: User Not Active
**Check:** Response says "User account is inactive"

**Fix:** Already fixed - user is active

---

## ✅ Manual Test (This Works!)

```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"moodle_token":"a6f3e36db214f134c20acc2d8d6b8af6"}' \
  -s | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Get user info
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  -s | python3 -m json.tool
```

This returns your user info successfully!

---

## 🎯 Next Steps

1. **Open http://localhost:5173 in browser**
2. **Open DevTools (F12) → Network tab**
3. **Try logging in**
4. **Find the 403 request**
5. **Tell me:**
   - What URL is it calling?
   - What's in the Request Headers?
   - What's the Response body?

This will help me identify exactly where the 403 is coming from.

---

## 📝 Quick Checklist

- [ ] Backend running on port 8000? ✅
- [ ] Frontend running on port 5173? ✅
- [ ] Browser DevTools open? 
- [ ] Network tab visible?
- [ ] Tried logging in?
- [ ] Found the 403 request?

Once you find the 403 request in the Network tab, we can see exactly what's wrong!
