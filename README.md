# 🤖 Nexa AI – Your Smart AI Assistant
![logo](assets/logo.png)

> 💬 A fully customizable conversational AI chatbot built using **Streamlit + LangChain + DeepSeek/Groq + OpenAI**  
> 🧠 Supports multiple model providers with built-in memory, chat history, and desi-style humor packs!  
> 🌐 Built for developers, learners, and businesses — open source and ready to deploy.

---

# 🎯 Preview of Nexa AI
| Chat Bot UI | Saved Chat | Login Page | Output of AI |
|--------|------------|----------------|--------------|
| ![Main UI](preview/main.png) | ![Saved Chat](preview/saved_chat.png) | ![Login](preview/login.png) | ![Coding](preview/coding.png) |

---

# 📺 Demo Video

<a href="https://youtu.be/your-demo-link" target="_blank" style="padding:10px 16px;background:#4CAF50;color:white;border-radius:4px;text-decoration:none;font-weight:bold;">
▶️ Watch Demo
</a>

---

# ⚙ Tech Stack

<p>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="40" alt="Python" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/streamlit/streamlit-original.svg" height="40" alt="Streamlit" />
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/ec/DeepSeek_logo.svg" height="40" alt="OpenAI" />
</p>

- **Python** – Core logic
- **Streamlit** – UI framework
- **LangChain** – Prompting and memory
- **DeepSeek** – LLM APIs
- **Dotenv** – Secure API key management

---

# ✨ Features

✅ Smart chat with history & saved conversations  
✅ Supports Groq, DeepSeek, and OpenAI models  
✅ Custom modes: Gujarati Jokes, Shayari, Motivational Quotes, Chanakya Quotes  
✅ Clean, animated sidebar with actions  
✅ Built-in emoji & desi flavor  
✅ Custom prompt handling  
✅ Lottie animations for visual appeal  
✅ `.env` based secure API integration  
✅ Light & Fast UI with Streamlit

---

# 📁 Project Structure

```plaintext
nexa-ai/
├ assets/                → Images, logos
├ saved_chats/           → User-saved conversations
├ chat_history/          → Temporary chat memory
├ components/
│   ├ sidebar.py         → Sidebar navigation logic
│   └ auth.py            → Login / session logic
├ custom_responses.py    → Custom reply packs (shayari, jokes, quotes)
├ bot.py                 → Main chatbot app (Streamlit)
├ .env                   → API keys (not committed)
├ .gitignore
├ requirements.txt
└ README.md
```

---

# 🚀 Installation & Setup

## 🔵 Windows
### 1. clone the Github Repo
```
git clone https://github.com/dhruvpatel16120/AI-bot.git
cd AI-bot
```
### 2. Create Virtual Env for Setup
```
python -m venv venv
venv\Scripts\activate
```
### 3. Install the Packages
```
pip install -r requirements.txt
```

## 🟢 Linux / macOS

### 1. clone the Github Repo
```
git clone https://github.com/dhruvpatel16120/nexa-ai.git
cd nexa-ai
```
2. Create Virtual Env for Setup
```
python3 -m venv venv
source venv/bin/activate
```

3. Install the Packages
```
pip install -r requirements.txt
```

# 🔑 Set Up API Key

Get your key from [https://console.groq.com/keys](https://console.groq.com/keys).

```
# PAST YOUR API KEY in .env file content 
API_KEY=your_key_here
```

# ▶️ Run the App

```bash
streamlit run main.py
```

> Make sure `.env` is configured correctly before running.

---

# 🧪 Usage Tips

- Use the sidebar to view history and saved chats  
- Add or delete specific conversations  
- Activate Shayari, Jokes, and Quotes from custom_responses.py  
- Use “Download” button to save your chats  
- Clear all chats or refresh with a click!

---

# 🙌 Contributing

We welcome contributions and ideas!

### How to Contribute

1. Fork the repo 🍴  
2. Create your feature branch (`git checkout -b feature/YourFeature`)  
3. Commit your changes (`git commit -m 'Add awesome feature'`)  
4. Push to the branch (`git push origin feature/YourFeature`)  
5. Create a Pull Request 🚀

---

# 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

# 🏷 Tags / Topics

```
#chatbot #nexa #ai-assistant #langchain #streamlit #groq #openai #deepseek #chat-ui #python #desi-bot #open-source
```

---

> Built with ❤️ by [@dhruvpatel16120](https://github.com/dhruvpatel16120)
