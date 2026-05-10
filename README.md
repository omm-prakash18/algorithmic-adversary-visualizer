# Algorithmic Adversary & Visualizer

A professional, high-fidelity platform for interactive algorithm learning and security red-teaming. This project combines a secure C++ execution environment, an AI-driven RAG (Retrieval-Augmented Generation) visualization engine, and an adversarial LLM tutor.

## 🚀 Key Features

- **Interactive 3D Visualizer**: A React Flow-powered sandbox with a cinematic 3D background (Three.js) that animates DSA concepts (BST, Linked Lists, Stacks, Queues) in real-time.
- **AI-Driven Logic Tracing**: Uses a professional RAG pipeline (LangChain + GPT-4o) to analyze your *specific* C++ code logic and generate corresponding visualization steps.
- **The "Adversary" AI**: A red-teaming agent that scans your code for vulnerabilities like memory leaks, logic flaws, and resource exhaustion.
- **Secure Code Sandbox**: A isolated execution environment for C++ with strict time and memory limits.
- **Power-User UI**: A fully resizable, persistent dashboard with a professional "Brutalist-Industrial" aesthetic and glassmorphism effects.

## 🛠️ Tech Stack

- **Frontend**: React (Vite), TypeScript, TailwindCSS, React Flow, Three.js, Framer Motion.
- **Backend**: Django REST Framework, LangChain, OpenAI.
- **Intelligence**: RAG Pipeline with ChromaDB/In-Memory Vector Store.
- **Communication**: REST API with real-time system diagnostic feedback.

## 📥 Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API Key

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
```
Create a `.env` file in the `backend/` directory:
```env
OPENAI_API_KEY=your_key_here
SECRET_KEY=your_secret_key
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🖥️ Usage
1.  Open the Dashboard.
2.  Implement your algorithm in the **Source Logic** editor.
3.  Click **Synchronize** to compile, run, and visualize your specific code trace.
4.  Click **Scan** to let the Adversarial Tutor find edge cases in your implementation.

## 🛡️ Security
This project uses isolated subprocess execution with timeouts to prevent server hangs. In production, Dockerized sandboxing is recommended for the code execution layer.

---
*Built for the next generation of competitive programmers and security engineers.*
