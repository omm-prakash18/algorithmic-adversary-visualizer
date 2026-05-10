# 🛡️ Algorithmic Adversary & Visualizer

A professional, high-fidelity platform for interactive algorithm learning and security red-teaming. This project combines a **secure C++ execution environment**, an **AI-driven RAG (Retrieval-Augmented Generation)** visualization engine, and an **Adversarial LLM Tutor**.

---

## 🚀 Key Features

### 1. Interactive 3D & 2D Visualizer
- **Dynamic Logic Tracing**: A React Flow-powered sandbox that animates DSA concepts (BST, Linked Lists, Stacks, Queues) in real-time.
- **Cinematic Experience**: High-fidelity 3D "Cyber-Artifact" built with Three.js and a professional "Brutalist-Industrial" UI with glassmorphism and animated blueprint grids.

### 2. Professional RAG Pipeline
- **Context-Aware Visualization**: Uses **LangChain** and **GPT-4o** to analyze raw C++ code logic. It retrieves expert visualization patterns from a **ChromaDB/In-Memory Vector Store** to ensure the animation perfectly mirrors your implementation.
- **Dynamic Data Extraction**: The AI automatically parses your `main()` function to extract test data, ensuring the visualization matches your specific inputs.

### 3. The "Adversary" AI (Red-Teaming)
- **Vulnerability Scanning**: An automated security agent that scans your code for memory leaks (missing `delete`), logic flaws, resource exhaustion, and duplicate handling issues.
- **Edge-Case Generator**: Provides the exact technical feedback and test inputs required to break your algorithm.

### 4. Power-User Dashboard
- **Resizable Workspace**: Fully customizable and persistent layout using `react-resizable-panels`. Your workspace configuration is saved to Local Storage.
- **Kernel Stream**: Real-time terminal output with professional typography (Fira Code) for a true developer-tool experience.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React (Vite), TypeScript, TailwindCSS, React Flow, Three.js, Framer Motion |
| **Backend** | Django REST Framework, LangChain, OpenAI GPT-4o |
| **Database** | ChromaDB (Vector Store), SQLite |
| **Security** | Isolated Subprocess Sandbox, Heuristic Heuristic Fallback |

---

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
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your-django-secret-key
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:5175
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🖥️ Usage
1.  **Synchronize**: Implement your C++ algorithm and click **Synchronize** to compile and visualize the logic trace.
2.  **Scan**: Click **Scan** to trigger the Adversarial Tutor and identify potential vulnerabilities in your code.
3.  **Customize**: Drag panel borders to create your ideal workspace layout.

## 🛡️ Security
This project uses isolated subprocess execution with a 2-second timeout to prevent server hangs. For production environments, it is recommended to wrap the execution layer in a Docker container.

---
*Built for the next generation of competitive programmers and security engineers.*
