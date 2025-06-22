Nexibit Backend
===============

This is the backend service for **Nexibit**, an AI-powered application that generates layout results using a trained AI model. The backend is written in **Python** and uses **Gunicorn** for local hosting and **ngrok** to expose it to the internet.

Features
--------

-   Uses an AI model to generate intelligent layout results

-   Written in Python with a clean backend structure

-   Runs using Gunicorn on localhost

-   Exposed to the internet using ngrok tunnel

-   Includes utility functions for layout placement logic

Tech Stack
----------

-   **Python 3.10+**

-   **PyTorch** -- for AI model execution

-   **Gunicorn** -- WSGI server for running the app

-   **Ngrok** -- to expose local server to the internet

-   **Flask** or **FastAPI** -- for handling HTTP requests

Project Structure
-----------------

```
nexibit_backend/
├── app.py               # Main Flask server file
├── model/               # AI model and weights
│   └── layout_model.pth
├── utils/               # Utility functions
│   └── utils.py
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation

```

How to Run
----------

### 1\. Clone the Repository

```
git clone https://github.com/coode-sensei/nexibit_backend.git
cd nexibit_backend

```

### 2\. Create a Virtual Environment

```
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

```

### 3\. Install Dependencies

```
pip install -r requirements.txt

```

### 4\. Run the Server with Gunicorn

```
gunicorn -w 1 app:app --bind 0.0.0.0:5000

```

### 5\. Expose Localhost with Ngrok

```
ngrok http 5000

```

> Copy the generated URL (e.g., [https://xxxx.ngrok.io](https://xxxx.ngrok.io/)) to access your backend from anywhere.

# NOTE

Each time new url create (e.g., [https://xxxx.ngrok.io](https://xxxx.ngrok.io/)) needs to be put in the frontend of the porject so it may send requests to correct url.

Sample API Usage
----------------

### Endpoint

```
POST /generate-layout
Content-Type: application/json

```

### Request Body

```
{
  "input_parameters": {
    "platinum": {"count": 2, "width": 3, "height": 3},
    "gold": {"count": 3, "width": 2, "height": 2}
  }
}

```

### Response

```
{
  "status": "success",
  "predictions": [...]
}

```

Notes
-----

-   Make sure `layout_model.pth` is available in the `model/` folder.

-   Ensure the `app` object is correctly exposed in `app.py`.

-   For production, consider using a proper server and SSL instead of ngrok.

Author
------

Created by [@coode-sensei](https://github.com/coode-sensei)

License
-------

MIT License
