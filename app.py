"""
AI-Powered Email Responder - Streamlit Web App
Uses Gemini 2.0 to generate response drafts for incoming emails
"""

import streamlit as st
import imaplib
import email
import ssl
from datetime import datetime, timedelta
import google.generativeai as genai
import pandas as pd


class EmailResponder:
    def __init__(self, config):
        """Initialize the email responder with configuration"""
        self.email_address = config['email_address']
        self.email_password = config['email_password']
        self.imap_server = config.get('imap_server', 'imap.gmail.com')
        self.imap_port = config.get('imap_port', 993)
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        
        # AI configuration
        self.gemini_api_key = config['gemini_api_key']
        self.max_emails = config.get('max_emails', 5)
        self.response_tone = config.get('response_tone', 'professional')
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def connect_to_email(self):
        """Establish connection to email server"""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to IMAP server
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port, ssl_context=context)
            self.mail.login(self.email_address, self.email_password)
            
            return True, "Successfully connected to email server"
            
        except Exception as e:
            return False, f"Failed to connect to email: {str(e)}"

    def fetch_recent_emails(self, days_back=1):
        """Fetch recent emails from inbox"""
        try:
            # Select inbox
            self.mail.select('inbox')
            
            # Calculate date for search
            since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            
            # Search for recent emails
            status, messages = self.mail.search(None, f'(SINCE "{since_date}" UNSEEN)')
            
            if status != 'OK':
                return [], "Failed to search for emails"
            
            email_ids = messages[0].split()
            
            # Limit number of emails to process
            email_ids = email_ids[-self.max_emails:] if len(email_ids) > self.max_emails else email_ids
            
            emails = []
            
            for email_id in email_ids:
                try:
                    # Fetch email
                    status, msg_data = self.mail.fetch(email_id, '(RFC822)')
                    
                    if status == 'OK':
                        # Parse email
                        email_message = email.message_from_bytes(msg_data[0][1])
                        
                        # Extract email details
                        email_info = self._extract_email_info(email_message)
                        email_info['id'] = email_id.decode()
                        
                        emails.append(email_info)
                        
                except Exception as e:
                    st.warning(f"Error processing email {email_id}: {str(e)}")
                    continue
            
            return emails, f"Fetched {len(emails)} recent emails"
            
        except Exception as e:
            return [], f"Error fetching emails: {str(e)}"

    def _extract_email_info(self, email_message):
        """Extract relevant information from email message"""
        # Get basic info
        subject = email_message.get('Subject', 'No Subject')
        sender = email_message.get('From', 'Unknown Sender')
        date = email_message.get('Date', 'Unknown Date')
        
        # Get email body
        body = self._get_email_body(email_message)
        
        return {
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body
        }

    def _get_email_body(self, email_message):
        """Extract email body from message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(email_message.get_payload())
        
        return body.strip()

    def generate_response(self, email_info):
        """Generate AI response using Gemini 2.0"""
        try:
            # Create prompt for AI
            prompt = f"""
You are a professional customer service representative. Generate a helpful and {self.response_tone} email response based on the following incoming email:

Subject: {email_info['subject']}
From: {email_info['sender']}
Body: {email_info['body']}

Generate a response that:
1. Acknowledges the sender's inquiry professionally
2. Addresses their main concern or question
3. Provides helpful information or next steps
4. Maintains a {self.response_tone} tone
5. Includes appropriate closing remarks

Only provide the email response content, without subject line or formatting markers.
"""

            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text.strip(), None
            else:
                return "Thank you for your email. We have received your inquiry and will respond shortly.", None
                
        except Exception as e:
            return "Thank you for your email. We have received your inquiry and will respond shortly.", str(e)

    def close_connection(self):
        """Close email connection"""
        try:
            self.mail.close()
            self.mail.logout()
        except:
            pass


def main():
    st.set_page_config(
        page_title="AI Email Responder",
        page_icon="✉️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("AI-Powered Email Responder")
    st.markdown("Generate professional email responses using Gemini 2.0")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Email Settings
        st.subheader("Email Settings")
        email_address = st.text_input("Email Address", placeholder="your-email@gmail.com")
        
        # App Password Instructions
        with st.expander("How to get Gmail App Password"):
            st.markdown("""
            **For Gmail users, you MUST use an App Password (not your regular password):**
            
            1. **Enable 2-Factor Authentication** on your Google account first
            2. Go to [Google Account Settings](https://myaccount.google.com/)
            3. Click **Security** in the left sidebar
            4. Under "How you sign in to Google", click **App passwords**
            5. Select **Mail** and **Other (custom name)**
            6. Enter "Email Responder" as the app name
            7. Google will generate a 16-character password
            8. Copy and paste that password into the field below
            
            **Alternative method:**
            - Go directly to [App Passwords](https://myaccount.google.com/apppasswords)
            - Follow steps 5-8 above
            
            **Important**: Use the generated 16-character password, not your Gmail password.
            """)
        
        email_password = st.text_input("Email Password / App Password", type="password", 
                                     help="For Gmail: Use App Password (16 characters). For other providers: Use your email password.")
        
        with st.expander("Advanced Email Settings"):
            imap_server = st.text_input("IMAP Server", value="imap.gmail.com")
            imap_port = st.number_input("IMAP Port", value=993, min_value=1, max_value=65535)
            smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", value=587, min_value=1, max_value=65535)
        
        # AI Settings
        st.subheader("AI Settings")
        st.info("**API Key**: Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)")
        gemini_api_key = st.text_input("Gemini API Key", type="password",
                                     help="Never commit API keys to version control")
        
        response_tone = st.selectbox("Response Tone", 
                                   ["professional", "friendly", "formal", "casual"])
        
        max_emails = st.slider("Max Emails to Process", min_value=1, max_value=20, value=5)
        days_back = st.slider("Days Back to Search", min_value=1, max_value=7, value=1)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Email Processing")
        
        # Validate configuration
        config_valid = all([email_address, email_password, gemini_api_key])
        
        if not config_valid:
            st.warning("Please fill in all required configuration fields in the sidebar.")
        
        if st.button("Fetch and Process Emails", disabled=not config_valid):
            config = {
                'email_address': email_address,
                'email_password': email_password,
                'imap_server': imap_server,
                'imap_port': imap_port,
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'gemini_api_key': gemini_api_key,
                'response_tone': response_tone,
                'max_emails': max_emails
            }
            
            responder = EmailResponder(config)
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Connect to email
                status_text.text("Connecting to email server...")
                success, message = responder.connect_to_email()
                
                if not success:
                    st.error(f"Connection failed: {message}")
                    st.stop()
                
                st.success(f"Connected successfully: {message}")
                progress_bar.progress(25)
                
                # Fetch emails
                status_text.text("Fetching recent emails...")
                emails, fetch_message = responder.fetch_recent_emails(days_back)
                
                if not emails:
                    st.info(f"No emails found: {fetch_message}")
                    responder.close_connection()
                    st.stop()
                
                st.success(f"Emails fetched: {fetch_message}")
                progress_bar.progress(50)
                
                # Store emails in session state
                st.session_state.emails = emails
                st.session_state.responses = []
                
                # Process emails
                status_text.text("Generating AI responses...")
                
                for i, email_info in enumerate(emails):
                    # Generate response
                    response, error = responder.generate_response(email_info)
                    
                    response_data = {
                        'email': email_info,
                        'response': response,
                        'error': error,
                        'timestamp': datetime.now()
                    }
                    
                    st.session_state.responses.append(response_data)
                    
                    # Update progress
                    progress = 50 + (50 * (i + 1) / len(emails))
                    progress_bar.progress(int(progress))
                
                status_text.text("Processing complete!")
                progress_bar.progress(100)
                
                # Close connection
                responder.close_connection()
                
                st.success(f"Successfully processed {len(emails)} emails!")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                try:
                    responder.close_connection()
                except:
                    pass
    
    with col2:
        st.header("Results")
        
        if 'responses' in st.session_state and st.session_state.responses:
            st.subheader(f"Generated {len(st.session_state.responses)} responses")
            
            # Create summary table
            summary_data = []
            for i, resp in enumerate(st.session_state.responses):
                summary_data.append({
                    'Index': i + 1,
                    'From': resp['email']['sender'][:30] + '...' if len(resp['email']['sender']) > 30 else resp['email']['sender'],
                    'Subject': resp['email']['subject'][:40] + '...' if len(resp['email']['subject']) > 40 else resp['email']['subject'],
                    'Status': 'Success' if not resp['error'] else 'Error'
                })
            
            df = pd.DataFrame(summary_data)
            st.dataframe(df, use_container_width=True)
            
            # Download all responses
            if st.button("Download All Responses"):
                # Create a text file with all responses
                all_responses = ""
                for i, resp in enumerate(st.session_state.responses):
                    all_responses += f"""
EMAIL RESPONSE DRAFT #{i+1}
{'=' * 50}

Original Email:
Subject: {resp['email']['subject']}
From: {resp['email']['sender']}
Date: {resp['email']['date']}

Original Message:
{resp['email']['body']}

Generated Response:
{resp['response']}

Generated on: {resp['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 50}

"""
                
                st.download_button(
                    label="Download Responses as Text",
                    data=all_responses,
                    file_name=f"email_responses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        else:
            st.info("Process emails to see results here")
    
    # Display individual responses
    if 'responses' in st.session_state and st.session_state.responses:
        st.header("Individual Responses")
        
        for i, resp in enumerate(st.session_state.responses):
            with st.expander(f"Response #{i+1}: {resp['email']['subject']}", expanded=False):
                col_left, col_right = st.columns([1, 1])
                
                with col_left:
                    st.subheader("Original Email")
                    st.write(f"**From:** {resp['email']['sender']}")
                    st.write(f"**Subject:** {resp['email']['subject']}")
                    st.write(f"**Date:** {resp['email']['date']}")
                    st.write("**Body:**")
                    st.text_area("", resp['email']['body'], height=200, key=f"orig_{i}", disabled=True)
                
                with col_right:
                    st.subheader("Generated Response")
                    if resp['error']:
                        st.error(f"Error: {resp['error']}")
                    
                    response_text = st.text_area("", resp['response'], height=200, key=f"resp_{i}")
                    
                    # Individual download button
                    response_content = f"""
EMAIL RESPONSE DRAFT
===================

Original Email:
Subject: {resp['email']['subject']}
From: {resp['email']['sender']}
Date: {resp['email']['date']}

Original Message:
{resp['email']['body']}

Generated Response:
{response_text}

Generated on: {resp['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
"""
                    
                    st.download_button(
                        label="Download This Response",
                        data=response_content,
                        file_name=f"response_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        key=f"download_{i}"
                    )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>AI Email Responder powered by Gemini 2.0 | Built with Streamlit</p>
        <p><small>Always review AI-generated responses before sending</small></p>
        <p><small>This app does not store any credentials or personal data</small></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()