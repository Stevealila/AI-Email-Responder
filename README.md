# AI Email Responder

A Streamlit web application that uses Google's Gemini 2.0 AI to automatically generate professional email response drafts. Simply connect your Gmail account and let AI handle the heavy lifting of crafting thoughtful replies.

## Features

- **AI-Powered Responses**: Uses Gemini 2.0 to generate contextual, professional email replies
- **Gmail Integration**: Secure IMAP connection to fetch unread emails
- **Web Interface**: Clean, intuitive Streamlit interface
- **Customizable Tone**: Choose from professional, friendly, formal, or casual response styles
- **Bulk Processing**: Handle multiple emails at once with configurable limits
- **Export Options**: Download individual responses or batch export all drafts
- **Security First**: Uses Gmail App Passwords and stores no credentials permanently

## Prerequisites

- Python 3.10+
- UV package manager (recommended) or pip
- Gmail account with 2-Factor Authentication enabled
- Google AI Studio account (free tier available)

## Installation

1. **Clone the repository**:
   
   ```bash
   git clone https://github.com/Stevealila/AI-Email-Responder.git
   cd AI-Email-Responder
   ```
   
2. **Install dependencies**:
   
   ```bash
   # Using UV (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

## Setup

### 1. Gmail App Password Setup

**Important**: You MUST use an App Password, NOT your regular Gmail password.

1. **Enable 2-Factor Authentication**:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification if not already active

2. **Generate App Password**:
   - In Security settings → App passwords
   - Select "Mail" from dropdown
   - Click "Generate"
   - Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)

3. **Enable IMAP**:
   - Gmail Settings → Forwarding and POP/IMAP
   - Enable IMAP access

### 2. Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in and create a new API key
3. Copy and securely store the API key

## Usage

1. **Start the application**:
   
   ```bash
   # Using UV
   uv run streamlit run app.py
   
   # Or with activated environment
   streamlit run app.py
   ```
   
2. **Configure in the sidebar**:
   
   - Email address
   - App Password (16 characters)
   - Gemini API key
   - Response preferences
   
3. **Process emails**:
   
   - Click "Fetch and Process Emails"
   - Review generated responses
   - Download drafts as needed

## Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| Response Tone | AI response style | Professional |
| Max Emails | Number of emails to process | 5 |
| Days Back | How far back to search | 1 day |
| IMAP Server | Gmail IMAP server | imap.gmail.com |
| IMAP Port | IMAP port number | 993 |

## Security & Privacy

- **No Data Storage**: Credentials are only stored in memory during the session
- **App Passwords**: Uses Gmail App Passwords instead of account passwords
- **Local Processing**: All email processing happens locally on your machine
- **No Email Sending**: Application only reads emails and generates drafts
- **Secure Connections**: Uses SSL/TLS for all email connections

## Troubleshooting

### Authentication Errors
- Verify you're using an **App Password**, not your Gmail password
- Ensure 2FA is enabled on your Google account
- Check IMAP is enabled in Gmail settings

### API Errors
- Verify Gemini API key is correct
- Check API quota limits in Google AI Studio
- Ensure you have access to Gemini 2.0

### No Emails Found
- Check for unread emails in your inbox
- Adjust "Days Back" setting
- Verify email filters aren't auto-marking emails as read

## Best Practices

- **Never commit credentials** to version control
- **Regularly rotate** API keys and App Passwords
- **Review AI responses** before sending
- **Use environment variables** for production deployments
- **Revoke unused** App Passwords periodically

## Dependencies

```
streamlit>=1.28.0
google-generativeai>=0.3.0
pandas>=2.0.0
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool generates draft responses using AI. Always review and edit responses before sending. The application authors are not responsible for any issues arising from AI-generated content.

## Links

- [Repository](https://github.com/Stevealila/AI-Email-Responder)
- [Google AI Studio](https://aistudio.google.com/)
- [Gmail App Passwords Help](https://support.google.com/accounts/answer/185833)

---

**Built with ❤️ using Streamlit and Google Gemini 2.0**