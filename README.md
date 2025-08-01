
 🛍️ D.Watson Smart Assistant 🤖

An AI-powered smart retail assistant that transforms the traditional shopping experience using multimodal AI, voice interaction, and visual dashboards.

---

 🔥 Features

 🧠 Intelligent Shop Assistant
- 🔍 Search by Text or Voice: Ask about any product and get instant answers.
- 🧾 AI-Generated Product Descriptions: Leveraging Google Gemini to generate smart summaries.
- 🔊 Text-to-Speech (TTS): Reads product details aloud for accessibility.
- 🎙️ Voice Recognition: Search via your voice using real-time speech recognition.
- 📷 Image-Based Product Identification: Upload an image and detect the closest matching product using OpenAI CLIP.

 📊 Inventory & Sales Dashboard
- 🗃️ Real-time product inventory overview.
- 📈 Sales data visualized using:
  - Bar charts
  - Pie charts
  - Line graphs
- ⚠️ Low stock warnings for efficient inventory management.

 💳 Checkout Simulation
- 🛒 Add products to cart and simulate payment (Cash & Online).
- 📩 OTP verification included for online payments.
- 🧾 Auto-generates invoice in PDF format.

---

 🛠️ Tech Stack

| Component        | Technology              |
|------------------|--------------------------|
| Interface        | Streamlit                |
| Voice Input      | SpeechRecognition        |
| Text-to-Speech   | pyttsx3                  |
| AI Descriptions  | Google Gemini API        |
| Vision Model     | OpenAI CLIP              |
| Data Handling    | Pandas                   |
| Visualizations   | Plotly, Matplotlib       |
| File Export      | FPDF (for PDF invoices)  |

---

 🚀 Getting Started

 1. Clone the Repository
```bash
git clone https://github.com/yourusername/dwatson-smart-assistant.git
cd dwatson-smart-assistant
````

 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # on Linux/Mac
venv\Scripts\activate     # on Windows
```

 3. Install Dependencies

```bash
pip install -r requirements.txt
```

 4. Add Your Gemini API Key

In your Python file:

```python
genai.configure(api_key="YOUR_GEMINI_API_KEY")
```

 5. Run the App

```bash
streamlit run app.py
```

---

 📁 Project Structure

```
├── app.py
├── clip_openai/
├── src/
│   ├── database.py
│   ├── order_utils.py
├── order_history.csv
├── invoice.pdf
├── requirements.txt
└── README.md
```

---

 📜 License

This project is licensed under the MIT License.
Feel free to fork, customize, and use it for learning or building more powerful retail AI tools.

---

 👨‍💻 Developed By

Mujahid Kareem
💼 AI Engineer | Python Developer
📧 [mujahidkareem1122@gmail.com]

---

## ⭐ Give it a Star!

If you find this project helpful or inspiring, please ⭐ the repo — it motivates me to keep building!

