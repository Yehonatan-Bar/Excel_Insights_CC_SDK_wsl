"""
Email notification service using SendGrid
Sends completion notifications to users when analysis jobs finish
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import datetime


class EmailService:
    """SendGrid email service for analysis notifications."""

    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = 'Excel-insights@metro-mail.co.il'
        self.enabled = bool(self.api_key)

        if not self.enabled:
            print("⚠️ WARNING: SENDGRID_API_KEY not set. Email notifications disabled.")

    def send_analysis_complete(self, to_email, user_name, filename, dashboard_url, run_id):
        """
        Send analysis completion email to user.

        Args:
            to_email: Recipient email address
            user_name: User's full name
            filename: Original Excel filename
            dashboard_url: URL to view the dashboard
            run_id: Analysis run ID

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            print(f"Email notifications disabled. Would have sent to: {to_email}")
            return False

        if not to_email:
            print("No email address provided for notification")
            return False

        try:
            # Create email content
            subject = f"✅ ניתוח האקסל שלך הושלם - {filename}"

            html_content = f"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, 'Segoe UI', sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 30px;
            line-height: 1.6;
            color: #333;
        }}
        .info-box {{
            background: #f8f9fa;
            border-right: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .info-box strong {{
            color: #667eea;
        }}
        .button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 8px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 הניתוח שלך מוכן!</h1>
        </div>
        <div class="content">
            <p>שלום {user_name},</p>
            <p>הניתוח של קובץ האקסל שלך הושלם בהצלחה!</p>

            <div class="info-box">
                <p><strong>📁 שם הקובץ:</strong> {filename}</p>
                <p><strong>🆔 מזהה ריצה:</strong> {run_id}</p>
                <p><strong>⏰ הושלם ב:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>

            <p>לוח הבקרה האינטראקטיבי שלך כולל:</p>
            <ul>
                <li>📈 תרשימים ויזואליים מתקדמים</li>
                <li>💡 תובנות מונעות בינה מלאכותית</li>
                <li>📊 ניתוח סטטיסטי מעמיק</li>
                <li>🔄 אפשרות לשכלול הניתוח</li>
            </ul>

            <center>
                <a href="{dashboard_url}" class="button">
                    👁️ צפיה בלוח הבקרה
                </a>
            </center>

            <p style="color: #999; font-size: 14px; margin-top: 30px;">
                💡 <strong>טיפ:</strong> אתה יכול לשכלל את הניתוח על ידי לחיצה על "שכלל ניתוח" בלוח הבקרה.
            </p>
        </div>
        <div class="footer">
            <p>מייל זה נשלח מ-Excel Insights Dashboard</p>
            <p>מופעל על ידי Claude AI | Powered by SendGrid</p>
        </div>
    </div>
</body>
</html>
"""

            # Plain text version
            text_content = f"""
שלום {user_name},

הניתוח של קובץ האקסל שלך הושלם בהצלחה!

📁 שם הקובץ: {filename}
🆔 מזהה ריצה: {run_id}
⏰ הושלם ב: {datetime.now().strftime('%d/%m/%Y %H:%M')}

לצפייה בלוח הבקרה: {dashboard_url}

תודה שהשתמשת ב-Excel Insights Dashboard!
"""

            # Create and send email
            message = Mail(
                from_email=Email(self.from_email, 'Excel Insights Dashboard'),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=Content("text/plain", text_content),
                html_content=Content("text/html", html_content)
            )

            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)

            if response.status_code in [200, 201, 202]:
                print(f"✅ Email sent successfully to {to_email}")
                return True
            else:
                print(f"❌ Email send failed with status: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False

    def send_analysis_error(self, to_email, user_name, filename, error_message, run_id):
        """
        Send analysis error notification email.

        Args:
            to_email: Recipient email address
            user_name: User's full name
            filename: Original Excel filename
            error_message: Error description
            run_id: Analysis run ID

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled or not to_email:
            return False

        try:
            subject = f"⚠️ בעיה בניתוח האקסל - {filename}"

            html_content = f"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; }}
        .header {{ background: #f44336; color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; line-height: 1.6; }}
        .error-box {{ background: #ffebee; border-right: 4px solid #f44336; padding: 15px; margin: 20px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ בעיה בניתוח</h1>
        </div>
        <div class="content">
            <p>שלום {user_name},</p>
            <p>לצערנו, נתקלנו בבעיה במהלך ניתוח הקובץ שלך.</p>
            <div class="error-box">
                <p><strong>📁 קובץ:</strong> {filename}</p>
                <p><strong>🆔 מזהה ריצה:</strong> {run_id}</p>
                <p><strong>❌ שגיאה:</strong> {error_message}</p>
            </div>
            <p>אנא נסה שוב או צור קשר עם התמיכה אם הבעיה נמשכת.</p>
        </div>
    </div>
</body>
</html>
"""

            message = Mail(
                from_email=Email(self.from_email, 'Excel Insights Dashboard'),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )

            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)

            return response.status_code in [200, 201, 202]

        except Exception as e:
            print(f"Error sending error notification email: {str(e)}")
            return False


# Global email service instance
email_service = EmailService()
