# How to Login to StudyMaster

## ✅ The "Network Error" is Expected

When you enter your Moodle API token and see a **network error**, this is actually the app trying to verify your token with Moodle.

## 🔑 Get Your Real Moodle Token

### Step 1: Login to Moodle
Go to: https://moodle.concordia.ca

### Step 2: Navigate to Security Keys
1. Click your profile picture (top right)
2. Go to **Preferences**
3. Click **Security keys**
4. Or go directly to: https://moodle.concordia.ca/user/security.php

### Step 3: Create a Token
1. Click **"Create token"**
2. Service: Select **"Moodle mobile web service"** or **"Web services"**
3. Click **"Create token"**
4. **Copy the token** (long string of letters and numbers)

### Step 4: Use the Token in StudyMaster
1. Go to http://localhost:5173
2. Paste your token
3. Click Login

---

## 🐛 Why "test123" Doesn't Work

The error you're seeing means:
- ✅ Frontend is working
- ✅ Backend is working
- ✅ They're communicating correctly
- ❌ The token "test123" is not valid (it's just a test string)

You need a **real Moodle API token** from your Moodle account.

---

## 📝 What Happens When You Login

1. StudyMaster sends your token to Moodle
2. Moodle verifies it and returns your user info
3. StudyMaster creates your account
4. You get access to all features

---

## ✨ After Login You Can:

- Sync your Moodle courses
- Create AI-powered flashcards
- Use Focus Mode (Pomodoro timer)
- Track your study progress
- View your points and streak

---

**Get your real token from Moodle and try again!** 🚀
