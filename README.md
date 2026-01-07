# 🎧 TempVoice Bot

TempVoice is a Discord bot that automatically creates temporary private voice channels and gives users full control over their own channels using an interactive button-based control panel.

No complicated commands.  
No manual moderation.  
Just join → get a channel → control it.

---

## ✨ Features

- 🔊 Join to Create voice channels
- 👑 Channel ownership system
- 🧹 Automatic cleanup when channels are empty
- 🎛️ Button-based control panel
- 🔒 Lock / 🔓 Unlock voice channels
- 👻 Hide / 👁 Reveal channels
- 🔢 Set user limits
- ✏️ Rename channels
- 🚫 Block users from joining
- 🔌 Disconnect users
- ➡️ Drag users into your channel
- ♻️ Persistent buttons (work after bot restart)

---

## 🧠 How It Works

1. A user joins the **Join to Create** voice channel  
2. The bot automatically creates a private voice channel  
3. The user is moved into their channel and becomes the owner  
4. The owner can manage the channel using buttons in **#voice-control**  
5. When the channel is empty, it is deleted automatically  

---

## 📁 Project Structure

```
tempvoice/
│ bot.py
│ README.md
│ LICENSE
│
└─ cogs/
  ├─ init.py
  ├─ tempvoice_EN.py # English version of the TempVoice cog
  └─ tempvoice_DE.py # German version of the TempVoice cog
```


The bot only loads **one cog**.  
Choose the version that matches your server language.

---

## 🌍 Language Selection

This project provides **two language versions**:

- 🇬🇧 `tempvoice_EN.py` — English
- 🇩🇪 `tempvoice_DE.py` — German

### How to choose the language

1. Open `bot.py`
2. Find this part:
   ```py
   EXTENSIONS = [
       "cogs.tempvoice_EN"
   ]

