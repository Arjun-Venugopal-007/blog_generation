# 🌟 SOPHIA Blog Generator

> **Discover your Pathway to Prosperity** - An AI-powered blog generation platform that creates professional content with integrated image generation.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Features

- **🤖 AI-Powered Content**: Generate professional blogs using advanced language models
- **🎨 Multiple Styles**: Choose from Professional, Conversational, or Concise writing styles
- **🖼️ Smart Image Generation**: Automatic image creation for blog sections
- **📱 Responsive Design**: Beautiful, mobile-friendly interface
- **⚡ Fast Generation**: Create complete blogs in seconds
- **🔄 Fallback Systems**: Robust error handling with backup options

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **AI APIs**: Groq (Llama3), Unsplash, OpenAI (optional)
- **Templates**: Jinja2
- **Styling**: Custom CSS with modern design principles

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection for API access
- API keys for Groq and Unsplash

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Internship_2025/internshipproject
   ```

2. **Create virtual environment**
   ```bash
   python -m venv myvenv
   # Windows
   myvenv\Scripts\activate
   # macOS/Linux
   source myvenv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   UNSPLASH_ACCESS_KEY=your_unsplash_key_here
   OPENAI_API_KEY=your_openai_key_here  # Optional
   ```

5. **Run the application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application**
   Open your browser and go to: `http://localhost:8000`

## 🎯 Usage

### Quick Generation
1. Select "Quick Generation" method
2. Enter your blog title
3. Optionally enable image generation
4. Click "Generate" and choose your preferred style

### Detailed Generation
1. Select "Detailed Generation" method
2. Provide title and detailed description
3. Configure image settings
4. Generate and select your favorite variation

## 📁 Project Structure

```
internshipproject/
├── main.py                 # FastAPI application
├── config.py              # Configuration settings
├── groq_client.py         # AI content generation
├── generate_image.py      # Image generation logic
├── static/
│   ├── style.css          # Styling
│   ├── script.js          # Frontend logic
│   └── images/            # Generated images
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Homepage
│   ├── blog_selection.html # Style selection
│   └── blog_result.html   # Final output
└── docs/                  # Documentation
```

## 🔄 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Homepage with generation options |
| `/generate` | POST | Generate blog variations |
| `/generate-final` | POST | Create final blog with images |
| `/generate-heading-image` | POST | Generate single image |

## 🎨 Screenshots

### Homepage
![Homepage](docs/screenshots/homepage.png)

### Blog Selection
![Blog Selection](docs/screenshots/selection.png)

### Final Result
![Final Result](docs/screenshots/result.png)

## 🔧 Configuration

### Required API Keys

1. **Groq API**: Get your key from [Groq Console](https://console.groq.com)
2. **Unsplash API**: Register at [Unsplash Developers](https://unsplash.com/developers)
3. **OpenAI API** (Optional): Get from [OpenAI Platform](https://platform.openai.com)

### Environment Variables

```env
# Required
GROQ_API_KEY=your_groq_api_key
UNSPLASH_ACCESS_KEY=your_unsplash_access_key

# Optional
OPENAI_API_KEY=your_openai_api_key
DEBUG=True
MAX_IMAGES=6
```

## 🚨 Troubleshooting

### Common Issues

**API Connection Errors**
- Verify your API keys are correct
- Check internet connectivity
- Ensure API quotas aren't exceeded

**Image Generation Fails**
- Fallback SVG images will be generated automatically
- Check Unsplash API limits
- Verify image storage permissions

**Content Generation Issues**
- Validate input parameters
- Check Groq API status
- Review error logs in console

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq** for providing fast AI inference
- **Unsplash** for high-quality stock images
- **FastAPI** for the excellent web framework
- **OpenAI** for AI capabilities

## 📞 Support

For support, email [your-email@example.com] or create an issue in this repository.

---

**Made with ❤️ by [Your Name]**