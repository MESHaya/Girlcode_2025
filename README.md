
# 🌍 Auraven — Local-Language AI Detection Platform

### Detect • Learn • Empower

---

## 🧠 Overview

**Auraven** is a multilingual **AI detection platform** designed to make digital spaces safer and more inclusive for South Africans.
It detects **AI-generated videos, images, and documents**, and **teaches users how to identify AI content themselves** — all in their **preferred local language**.

Most AI detection tools only work in English and focus on one media type. Auraven bridges that gap by combining **multimedia detection** with **language accessibility** and **digital literacy education**.

---

## 🚩 Problem

AI-generated misinformation is spreading rapidly across platforms like TikTok, WhatsApp, and email — yet most detection tools:

* Only support **English**, leaving millions of local-language speakers behind.
* Focus on **text only**, ignoring videos, images, and documents.
* Don’t explain *why* something is AI-generated, which limits public understanding.

This creates a **digital divide** where communities are more vulnerable to scams, fake news, and manipulation.

---

## 💡 Solution

Auraven is a **web-based tool** that:

1. **Detects** whether videos, images, or documents are AI-generated or manipulated.
2. **Translates** results and explanations into **South African languages** like isiZulu, isiXhosa, and Sesotho.
3. **Educates** users by teaching them how to identify AI-generated content on their own.

It’s more than a detection tool — it’s a step toward **AI literacy for all**.

---

## 🧩 Features

* 🎥 **Video Analysis** — Detects deepfakes or AI-generated footage.
* 🖼️ **Image Analysis** — Identifies AI-generated or manipulated images.
* 📄 **Document Scanning** — Detects AI-written or edited documents (PDF, Word).
* 🌐 **Multilingual Output** — Supports South African local languages.
* 🧠 **Learning Mode** — Provides educational tips on spotting AI content yourself.

---

## 🧰 Tech Stack

| Layer                   | Technologies Used                                               |
| ----------------------- | --------------------------------------------------------------- |
| **Frontend**            | React (Vite) / HTML / TailwindCSS                               |
| **Backend**             | FastAPI (Python)                                                |
| **AI Models / APIs**    | OpenAI / Hugging Face detection models / Deepfake detection API |
| **Storage**             | Local temporary file storage (MVP)                              |
| **Languages Supported** | isiZulu, isiXhosa, Sesotho, English                             |
| **Deployment (future)** | Render / Vercel / AWS                                           |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your-username>/Auraven.git
cd Auraven
```

### 2️⃣ Backend Setup (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 3️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Then open your browser at:
👉 [http://localhost:5173](http://localhost:5173)

Backend runs on:
👉 [http://localhost:8000](http://localhost:8000)

---

## 🚀 How It Works

1. The user uploads a **video, image, or document**.
2. The backend processes it using AI detection APIs.
3. The system outputs a **confidence score** and a **multilingual explanation**.
4. The frontend displays the results and **teaches the user** how to identify similar content manually.

---

## 🎯 Impact

* Reduces misinformation by **detecting AI-generated content**.
* Makes digital safety **accessible to all languages**.
* Builds **digital literacy skills** for South African communities.

---

## 💸 Sustainability & Funding

* **Free core access** for all users.
* **Partnerships** with fact-checking and educational organizations.
* **Freemium model** for enterprise or large-scale integrations.

---

## 🛠️ Future Plans

* Add **more South African languages**.
* Improve **translation accuracy** for long text bodies.
* Enable **real-time media scanning** (browser extension).
* Deploy as a **mobile-friendly PWA**.

---

## 🌟 Inspiration

This project was built during the **GirlCode Hackathon 2025** to bridge South Africa’s **AI accessibility gap** and promote **digital trust** in a multilingual society.

---


