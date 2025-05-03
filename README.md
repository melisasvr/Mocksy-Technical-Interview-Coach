# Mocksy - Technical Interview Coach

**Mocksy** is an AI-powered coach designed to help you prepare for technical interviews with personalized guidance. Whether you're aiming for a role at a top tech company or brushing up on algorithms, Mocksy offers interactive practice and feedback to boost your confidence.

## Features
- 📚 **Practice Core Concepts**: Work on algorithms, data structures, and system design questions.
- 💡 **Company-Specific Tips**: Get tailored advice for interviews at Google, Amazon, Microsoft, Meta, and more.
- 🤖 **AI-Driven Mock Interviews**: Engage in realistic mock interviews with AI feedback.
- 🗂️ **Interactive Chat Interface**: Ask questions and get personalized responses in real time.

## Tech Stack
- **Backend**: FastAPI (Python) for a robust API.
- **AI Logic**: Node.js with Vibing AI SDK for intelligent responses.
- **Frontend**: HTML, CSS, JavaScript for a clean, responsive UI.
- **Dependencies**: Managed via `npm` (Node.js) and `pip` (Python).

## Getting Started
Follow these steps to run **Mocksy** locally:

### Prerequisites
- **Node.js**: Install from [nodejs.org](https://nodejs.org/) (v16 or higher recommended).
- **Python**: Install from [python.org](https://www.python.org/) (v3.8 or higher recommended).
- **Git**: Install from [git-scm.com](https://git-scm.com/) to clone the repo.

### Installation
1. **Clone the Repository**:
   ```
    git clone https://github.com/<your-username>/Mocksy.git
    cd Technical_Interview_Coach_SDK
   ```
2. Install Node.js Dependencies:
- `npm install`
3. Install Python Dependencies
- `cd api`
- `pip install fastapi uvicorn transformers torch pydantic`

## Running the Application
1. Start the Backend (FastAPI)
- `cd api`
- `uvicorn main:app --reload --port 8000`
2. Start the Frontend (Node.js):
- In a new terminal, from the root directory:
- `cd C:\Users\user\Files\Desktop\Technical Interview Coach`
- `npm start`
- This runs src/index.js, handling AI logic and API calls.
-Access Mocksy:
- Open http://localhost:8000 in your browser.
- Try asking questions like "reverse string" or "prepare for Google."

## Project Structure
- `api/`: Contains the FastAPI backend (main.py) and frontend (index.html).
- `src/`: Contains the Node.js AI logic (index.js).
- `package.json`: Node.js dependencies and scripts.
- `.gitignore`: Ignores unnecessary files like node_modules/ and __pycache__/.

## License
- This project is licensed under the MIT License - see the LICENSE file for details.




