# 📬 Outlook to WhatsApp Notifier

This Python script monitors emails in Microsoft Outlook, checks for messages from a specific sender, and automatically sends a WhatsApp notification using Twilio API.

If the email contains attachments, they are downloaded, uploaded to Google Drive, and the public links are shared in the WhatsApp message. It's ideal for automating internal alerts, receiving reports, or monitoring key email sources in real time.

---

## 🚀 Features

- ✅ Reads emails from a specified Outlook inbox
- 🔁 Skips already processed emails using EntryID tracking
- 📎 Downloads attachments and uploads them to Google Drive
- 📱 Sends WhatsApp messages via Twilio API with:
  - Subject
  - Date
  - Attachments (as clickable links)

---

## 🛠 Requirements

- Python 3.x
- Microsoft Outlook (desktop client)
- Twilio account with WhatsApp sandbox access
- Google API credentials for Drive (OAuth)

---

## ⚙️ Setup Instructions

### 1. Clone this repository

```bash
git clone https://github.com/mixterix99/OutlookToWhatsApp-Notifier.git
cd OutlookToWhatsApp-Notifier
