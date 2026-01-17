# 🚀 Quick Start Guide - TranslateBridge

## Step-by-Step Tutorial for Two Friends

### Setup (One-time)

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add Your Groq API Key**
   - Open `.env` file
   - Replace `your_groq_api_key_here` with your actual key
   - Get free key at: https://console.groq.com

3. **Test Everything Works**
   ```bash
   python test_backend.py
   ```
   You should see ✅ for all tests.

---

## Running the App

### Start Both Servers

**Terminal 1 - Backend:**
```bash
python app.py
```
Wait for: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 - Frontend:**
```bash
python serve_frontend.py
```
Wait for: `Frontend server running at http://localhost:3000`

---

## Using the App (Two Friends Example)

### Friend 1: Alice (English Speaker)

1. **Open Browser**
   - Go to: `http://localhost:3000`

2. **Fill Setup Form**
   - Your Name: `Alice`
   - Your Language: `🇬🇧 English`
   - Room Code: Click **"Generate"** button
   - Copy the generated code (e.g., `ABC123`)

3. **Share Room Code**
   - Send `ABC123` to your friend via WhatsApp/SMS

4. **Join Room**
   - Click **"Join Room"**
   - When prompted for friend's language, enter: `hi` (for Hindi)

5. **Start Chatting!**
   - Type: "Hello! How are you today?"
   - Press Enter or click Send
   - Your friend will see it in Hindi!

---

### Friend 2: Raj (Hindi Speaker)

1. **Open Browser**
   - Go to: `http://localhost:3000`
   - (Use a different browser window/tab or device)

2. **Fill Setup Form**
   - Your Name: `Raj` (or `राज`)
   - Your Language: `🇮🇳 Hindi (हिंदी)`
   - Room Code: Paste the code from Alice: `ABC123`

3. **Join Room**
   - Click **"Join Room"**
   - When prompted for friend's language, enter: `en` (for English)

4. **Start Chatting!**
   - Type: "नमस्ते! मैं ठीक हूं।"
   - Press Enter or click Send
   - Alice will see it in English!

---

## What You'll See

### Alice's Screen:
```
┌─────────────────────────────────────┐
│ You: Hello! How are you today?      │
│ (Translation: नमस्ते! आज आप कैसे हैं?) │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Raj: I'm fine, thank you!           │
│ (Original: मैं ठीक हूं, धन्यवाद!)      │
└─────────────────────────────────────┘
```

### Raj's Screen:
```
┌─────────────────────────────────────┐
│ Alice: नमस्ते! आज आप कैसे हैं?        │
│ (Original: Hello! How are you today?)│
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ You: मैं ठीक हूं, धन्यवाद!            │
│ (Translation: I'm fine, thank you!)  │
└─────────────────────────────────────┘
```

---

## Testing on Same Computer

### Option 1: Two Browser Windows
1. Open Chrome window → Join as Alice (English)
2. Open Firefox window → Join as Raj (Hindi)
3. Use same room code in both

### Option 2: Incognito Mode
1. Regular Chrome → Join as Alice
2. Incognito Chrome → Join as Raj
3. Use same room code in both

### Option 3: Two Tabs (Same Browser)
1. Tab 1 → Join as Alice
2. Tab 2 → Join as Raj
3. Use same room code in both

---

## Tips for Best Experience

✅ **DO:**
- Use the same room code for both users
- Select different languages to see translation
- Keep both browser windows visible side-by-side
- Type naturally in your language

❌ **DON'T:**
- Don't refresh the page during chat (you'll lose messages)
- Don't use the same name for both users
- Don't close the terminal windows (servers will stop)

---

## Common Issues & Solutions

### "Connection failed"
**Solution:** Make sure backend server is running
```bash
python app.py
```

### "Translation not working"
**Solution:** Check your Groq API key in `.env` file

### "Page not loading"
**Solution:** Make sure frontend server is running
```bash
python serve_frontend.py
```

### "Friend can't see my messages"
**Solution:** Both users must use the EXACT same room code

---

## Language Codes Reference

When prompted for friend's language, use these codes:

| Language | Code |
|----------|------|
| English | en |
| Hindi | hi |
| Spanish | es |
| French | fr |
| German | de |
| Chinese | zh |
| Japanese | ja |
| Arabic | ar |
| Tamil | ta |
| Telugu | te |

---

## Next Steps

🎉 **Congratulations!** You've successfully set up real-time translation!

**Try these:**
- Test with different language pairs
- Invite more friends (same room code)
- Experiment with longer messages
- Try emojis and special characters

**Need help?** Check the main README.md for detailed documentation.

---

**Happy Translating! 🌍💬**
