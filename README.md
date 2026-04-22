# DropShare | Secure, Pro-Level File Sharing

DropShare is a sleek, ephemeral file-sharing platform designed for speed, security, and premium user experience. Whether you're sending large project archives or private documents, DropShare handles it with local network auto-detection and zero-knowledge privacy.

## Key Features

- **Massive Capacity**: Share files up to 500MB with automatic server-side Zipping for multi-file uploads.
- **Secure by Design**: Password protection, one-time download links, and UUID-based secure file naming.
- **Dynamic UI**: Hand-crafted Dark and Light modes with persistent memory.
- **Pro Sharing**: Built-in QR Code generation and direct sharing links for WhatsApp and Email.
- **Local History**: Keep track of your active sharing links with a local dashboard (Privacy-first).
- **Mobile Ready**: Automatic IP detection for seamless sharing between PC and Mobile on the same network.

## Tech Stack

- **Backend**: Python, Flask, SQLAlchemy, SQLite
- **Frontend**: Vanilla JS, Modern CSS (Glassmorphism), FontAwesome, Google Fonts
- **Utilities**: QRious (Local QR Rendering), ZipFile (Bulk Bundling)

## Getting Started

### Prerequisites
- Python 3.8+ 

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/dropshare.git
   cd dropshare
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python -m backend.main
   ```

4. **Open in browser:**
   Go to `http://localhost:8000`

## License
This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## Contributing
Contributions, issues, and feature requests are welcome!

---
*Developed with care to make file sharing simple and secure.*
