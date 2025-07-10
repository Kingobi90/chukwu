# Obtaining Your Moodle API Token from Concordia University

To use the Moodle API client, you'll need to obtain an API token from your Concordia University Moodle account. This guide will walk you through the process.

## Standard Method

1. **Log in to your Concordia Moodle account**
   - Go to https://moodle.concordia.ca
   - Log in with your Concordia credentials

2. **Access your profile settings**
   - Click on your profile picture in the top-right corner
   - Select "Preferences" from the dropdown menu

3. **Find the API tokens section**
   - Look for "Security keys" or "API tokens" in the preferences menu
   - If you don't see this option, try navigating to:
     `https://moodle.concordia.ca/moodle/user/managetoken.php`

4. **Create a new token**
   - Click on "Create token" or "Create new token"
   - Give it a descriptive name like "API Client"
   - Select the services you need access to (if prompted)
   - Click "Create"

5. **Save your token**
   - Copy the generated token string
   - Paste it into your `config.py` file in the `API_TOKEN` field

## Alternative Method (if the standard method doesn't work)

If you don't see the option to create tokens in your profile, Concordia might have restricted this functionality. In this case:

1. **Contact Concordia IT Services**
   - Email the IT Service Desk at help@concordia.ca
   - Explain that you need a Moodle Web Services API token for academic purposes
   - Specify which services you need access to (e.g., course content, assignments, etc.)

2. **Use the Mobile App method**
   - Concordia's Moodle might support the mobile app authentication flow
   - Navigate to: `https://moodle.concordia.ca/moodle/admin/tool/mobile/launch.php`
   - Follow the instructions to authenticate
   - The URL you're redirected to will contain your token in the format:
     `moodlemobile://token=YOUR_TOKEN_HERE`

## Important Notes

1. **Keep your token secure**
   - Your token provides access to your Moodle account
   - Never share it or commit it to public repositories

2. **API Limitations**
   - Concordia may limit which API functions are available
   - Some functions in this client might not work if they're not enabled on the server

3. **Token Expiration**
   - Tokens may expire after a certain period
   - If your client stops working, you might need to generate a new token

4. **Respect Usage Policies**
   - Use the API responsibly and in accordance with Concordia's acceptable use policies
   - Excessive requests might be rate-limited or blocked

## Troubleshooting

If you're having trouble obtaining a token:

1. Check if Concordia has a specific page about Web Services or API access
2. Look for documentation in the Moodle help section
3. Contact your instructor or the IT department for assistance

Once you have your token, add it to the `config.py` file to start using the Moodle API client.
