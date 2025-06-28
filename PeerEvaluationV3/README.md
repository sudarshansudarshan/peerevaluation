# PeerEvaluation_V3

Peer Evaluation System An open-source web application built using the MERN stack (MongoDB, Express.js, React, Node.js) to streamline and manage peer evaluations in academic courses.  Features include customizable evaluation criteria, secure authentication, real-time scoring, and visual feedback reports.

---

## Prerequisites

- [Node.js](https://nodejs.org/) (v16 or above recommended)
- [npm](https://www.npmjs.com/) (comes with Node.js)
- [MongoDB](https://www.mongodb.com/try/download/community) (local or cloud instance)
- [Git](https://git-scm.com/)

---

## Getting Started

### 1. Clone the Repository -

```bash
git clone <REPO_URL>
cd PES_Project_V3
```

### 2. Setup the Backend -

```bash
cd Backend
npm install
```

* Create a .env file in the Backend directory with the following (edit as needed):
```bash
MONGO_URI=mongodb://localhost:27017/peer_evaluation
JWT_SECRET=your_jwt_secret
PORT=5000
```

* Start the backend server:
```bash
npm start / npm run dev
```
#### The backend will run on http://localhost:5000.

### 3. Setup the Frontend -
```bash
cd ../Frontend
npm install
```

* Start the frontend development server:
```bash
npm run dev
```
The frontend will run on http://localhost:5173 (or as shown in your terminal).

### 4. AI Engine (Optional) -
If you want to use the AI Engine:
```bash
cd ../AI_Engine
# (Optional) Create a virtual environment and activate it
# python -m venv venv
# source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

### 5. Usage -
* Open the frontend URL in your browser.
* Register a new user or login with provided credentials.
* Use the dashboard to manage courses, batches, exams, and peer evaluations.

---
## Project Structure
```bash
PES_Project_V3/
│
├── Backend/      # Express.js API server
├── Frontend/     # React.js client app (Vite)
├── AI_Engine/    # (Optional) Python AI engine
└── README.md
```

---
## Common Commands
* Install dependencies: npm install
* Start backend: npm run dev (from 📁 Backend)
* Start frontend: npm run dev (from 📁 Frontend)
* Start AI Engine: python main.py (from 📁 AI_Engine)

---
## Troubleshooting
* Ensure MongoDB is running locally or update MONGO_URI in .env to your cloud instance.
* If ports are in use, change the PORT in .env or Vite config.
* For CORS issues, ensure backend and frontend URLs are correct.

---
## License
This project is open-source and available under the MIT License.

---
### For inquiries, feedback, or suggestions, feel free to:

* Open an issue on the repository.
* Reach out to the maintainers at:
    - rohit.24csz0014@iitrpr.ac.in