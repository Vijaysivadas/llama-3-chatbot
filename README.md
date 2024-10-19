# Llama 3 Chatbot Application

This repository contains a fully-fledged chatbot application built using the open-source Llama model, designed to function similarly to ChatGPT. The application leverages the power of Python and Flask to provide an interactive, responsive user experience.

## Features
- **Llama-based model:** Utilizes Meta's open-source Llama language model for natural language understanding and generation.
- **ChatGPT-like interface:** Offers conversational AI interaction similar to ChatGPT.
- **Fully-functional backend:** Built using the Python Flask framework for efficient API handling.
- **Extensible and customizable:** Easily integrate new features or models as per your requirements.
  
## Getting Started

### Prerequisites
Before you begin, ensure you have met the following requirements:
- Python 3.8 or higher
- Flask 2.0 or higher
- Huggingface transformers library
- Llama model weights (Check the [Meta AI repository](https://github.com/meta-llama/llama3) for downloading instructions)
- Currently a GPU (atleast 12 GB VRAM) is required to run the application for loading the model and inferenecing.

### Installation

1. **Clone the repository:**  

   ```bash
   git clone https://github.com/yourusername/llama-chatbot.git
   cd llama-chatbot
   ```
3. **Set up a virtual environment (optional but recommended):**

```bash
  python -m venv venv
  source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3. **Install the required dependencies:**
```bash
pip install -r requirements.txt
```
4. **Download and configure the Llama model weights:**

   Follow the instructions from the [Meta AI Llama repository](https://github.com/meta-llama/llama3) to download the model weights or download the weights directly from [Hugging Face Llama 3 8B page](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct). Place the weights inside the model directory with the name `llama-3-8b-instruct` in the project.

5. **Run the Flask app:**

```bash
python app.py

```
6. **Access the chatbot:**  

   Open your browser and go to http://127.0.0.1:5000/ to start chatting.
## Project Structure
<pre>
📦 llama-chatbot  
 ┣ 📂 models              # Contains model configuration and weights  
 ┣ 📂 static              # Frontend static files (CSS, JS, images)  
 ┣ 📂 templates           # HTML templates for the UI  
 ┣ 📄 app.py              # Main Flask application  
 ┣ 📄 db.py               # Handles Database functions  
 ┣ 📄 model.py            # Handles inferenceing with the AI models  
 ┣ 📃 requirements.txt    # Python dependencies  
 ┗ 📜 README.md           # This file
  </pre>
## Customization
**Model Customization:** You can swap the Llama model with any other supported models. Update the model loading part in app.py to use different model weights or configurations.
**Frontend Customization:** Modify the HTML/CSS in the templates and static folders to change the look and feel of the chatbot UI.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For any questions or feedback, feel free to reach out:

GitHub: [@vijaysivadas](https://github.com/Vijaysivadas)  
Portfolio Website: https://www.vijaysivadas.com/
