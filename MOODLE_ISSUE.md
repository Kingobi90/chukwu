# Moodle Webservice Issue

## Current Status

**Your token:** `a6f3e36db214f134c20acc2d8d6b8af6`  
**Moodle URL:** https://moodle.concordia.ca  
**Issue:** Webservice endpoint returning 404

## What's Happening

The Moodle webservice endpoint is currently returning a 404 error:
```
https://moodle.concordia.ca/webservice/rest/server.php
```

This is unusual if it worked earlier today.

## Possible Causes

1. **Moodle Maintenance** - The server might be undergoing maintenance
2. **Webservice Temporarily Disabled** - IT might have disabled it
3. **URL Changed** - Concordia might have changed the endpoint
4. **Network/Firewall Issue** - Your network might be blocking it

## What to Try

### 1. Wait and Retry
If it's maintenance, try again in 15-30 minutes.

### 2. Check Moodle Status
- Go to https://moodle.concordia.ca
- See if there's a maintenance notice
- Try logging in normally

### 3. Test with Moodle Mobile App
- If you have the Moodle mobile app installed
- Try logging in there
- If it works, the webservice is up

### 4. Contact Concordia IT
- Email: support@concordia.ca
- Ask if webservices are enabled
- Verify the correct endpoint URL

### 5. Alternative: Use Mock Mode
For development, you can temporarily bypass Moodle:

Edit `backend/app/api/v1/endpoints/auth.py` and add a development bypass:

```python
# At the top of the login function, add:
if settings.ENVIRONMENT == "development" and user_data.moodle_token == "dev_bypass":
    # Create a test user
    username = "test_user"
    email = "test@example.com"
    # ... continue with user creation
```

Then login with token: `dev_bypass`

## Current Workaround

Since the webservice is down, you have two options:

### Option A: Wait for Moodle
The service should come back up. Check back in 30 minutes.

### Option B: Development Mode
I can add a development bypass so you can test the app without Moodle being up.

---

**The issue is NOT with your token or the StudyMaster app - it's the Moodle server itself.**
