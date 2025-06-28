# Peer Evaluation System (PES)

This repository contains multiple versions of a Peer Evaluation System (PES) designed to facilitate and automate the process of peer assessment in educational and collaborative environments.

## Project Structure

```
Documentation/
│
├── Documentation_Peer_Evaluation_Version_1.pdf
├── Final_Demo_Screen_Recording.mp4
├── Schema of the Version 2.pdf
├── SOP_Peer_Evaluation_V2.pdf
├── SOP_Peer_Evaluation.pdf
└── PES Paper/
    ├── AI-Assisted Peer Review.pdf
    └── ...

PeerEvaluationV1/
│
├── manage.py
├── requirements.txt
├── app/
│   ├── models.py
│   ├── views.py
│   └── ...
└── peereval/
    ├── settings.py
    ├── urls.py
    └── ...

PeerEvaluationV2/
│
├── manage.py
├── requirements.txt
├── app.py
├── apps/
│   ├── authentication/
│   ├── home/
│   └── ...
└── core/
    ├── settings.py
    ├── urls.py
    └── ...

PeerEvaluationV3/
│
├── Backend/      # Express.js API server
│   ├── server.js
│   ├── package.json
│   ├── config/
│   ├── controllers/
│   ├── models/
│   ├── routes/
│   └── ...
├── Frontend/     # React.js client app (Vite)
│   ├── index.html
│   ├── package.json
│   ├── src/
│   ├── public/
│   └── ...
├── AI_Engine/    # (Optional) Python AI engine
│   └── main.py
└── README.md
```

- **Documentation/**: Contains documentation, research papers, and demo materials related to the project.
- **PeerEvaluationV1/**: First version of the Peer Evaluation System (Django-based).
- **PeerEvaluationV2/**: Second version with updated architecture and features.
- **PeerEvaluationV3/**: Latest version with separate AI Engine, Backend (Node.js), and Frontend (Vite/React).

## Version Information
For details about each version, including setup and usage instructions, please refer to the `README.md` file inside the respective version folder:
- [PeerEvaluationV1/README.md](./PeerEvaluationV1/README.md)
- [PeerEvaluationV2/README.md](./PeerEvaluationV2/README.md)
- [PeerEvaluationV3/README.md](./PeerEvaluationV3/README.md)

---

For any additional information, please consult the documentation folder or contact the project maintainers.
