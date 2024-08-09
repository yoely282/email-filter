import imaplib
import email
from email.header import decode_header
import json

# Increase the maximum line length for imaplib
imaplib._MAXLINE = 10000000  # Set this to a large value to handle big responses

# Email credentials and server details
username = "yoely282@gmail.com"
password = "muvuvysxscgiucia"  # Use your app password if 2-Step Verification is enabled
imap_server = "imap.gmail.com"

# Connect to the email server
def connect_to_email():
    print("Connecting to email server...")
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    mail.select("inbox")
    print("Connected.")
    return mail

# Function to decode MIME words
def decode_mime_words(s):
    def decode_part(part, encoding):
        try:
            return str(part if isinstance(part, str) else part.decode(encoding or 'utf-8'))
        except LookupError:
            return str(part if isinstance(part, str) else part.decode('utf-8', errors='ignore'))
    return ''.join(decode_part(b, encoding) for b, encoding in decode_header(s))

# Fetch and filter emails based on keywords
def fetch_and_filter_emails(mail, keywords, limit=100):
    print("Fetching and filtering emails...")
    status, messages = mail.search(None, 'ALL')
    if status != 'OK':
        print("Failed to search emails.")
        return []
    
    email_ids = messages[0].split()[:limit]
    print(f"Found {len(email_ids)} emails to process.")

    filtered_emails = []

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != 'OK':
            print(f"Failed to fetch email with ID {email_id.decode()}")
            continue
        
        msg = email.message_from_bytes(msg_data[0][1])
        subject = decode_mime_words(msg["Subject"])
        from_ = decode_mime_words(msg.get("From"))
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

        if any(keyword.lower() in subject.lower() for keyword in keywords) or \
           any(keyword.lower() in body.lower() for keyword in keywords):
            print(f"Email matched: {subject} from {from_}")
            filtered_emails.append({
                "id": email_id.decode(),
                "subject": subject,
                "from": from_,
                "body": body
            })

    print(f"Filtered {len(filtered_emails)} emails.")
    return filtered_emails

# Print filtered emails
def print_filtered_emails(filtered_emails):
    print("Printing filtered emails...")
    for email in filtered_emails:
        print(f"Subject: {email['subject']}")
        print(f"From: {email['from']}")
        print(f"Body: {email['body']}\n")
        print("-" * 50)

# Store filtered emails in a JSON file
def store_emails_in_json(filtered_emails, filename='filtered_emails.json'):
    print(f"Storing filtered emails in {filename}...")
    with open(filename, 'w') as file:
        json.dump(filtered_emails, file, indent=4)
    print("Stored filtered emails in JSON file.")

# Main function
def main():
    keywords = ["urgent", "action required", "verify", "account", "password"]
    mail = connect_to_email()
    filtered_emails = fetch_and_filter_emails(mail, keywords, limit=100)
    print_filtered_emails(filtered_emails)
    store_emails_in_json(filtered_emails)

    mail.logout()
    print("Logged out.")

if __name__ == "__main__":
    main()
