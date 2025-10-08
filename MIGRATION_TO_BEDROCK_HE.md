# מדריך העברה ל-AWS Bedrock - אפליקציית Excel Insights
## מדריך עבור DevOps

---

## 📋 רקע - מה האפליקציה עושה?

**Excel Insights** היא אפליקציית Flask שמנתחת קבצי Excel באמצעות Claude Agent SDK.
האפליקציה כוללת:
- ניתוח אוטומטי של קבצי Excel עם יצירת דשבורדים אינטראקטיביים
- מערכת אימות משתמשים (users.xml)
- מעקב היסטורי במסד נתונים PostgreSQL
- התראות דוא"ל דרך SendGrid
- מצב אורח (Guest Mode)

**נכון להיום:** האפליקציה משתמשת ב-Claude API הישיר דרך `ANTHROPIC_API_KEY`

**אחרי המעבר:** האפליקציה תשתמש ב-Claude דרך AWS Bedrock (ללא שינויי קוד!)

---

## ✅ דרישות מוקדמות

1. **חשבון AWS** עם הרשאות Bedrock
2. **אזור AWS** שתומך ב-Claude Sonnet 4.5 (מומלץ: `us-east-1` או `us-west-2`)
3. **גישה למודל:** יש לבקש גישה למודלים של Claude בקונסולת Bedrock
4. **IAM Role/User** עם הרשאות מתאימות (ראה למטה)

---

## 🔧 שלבי ההעברה

### שלב 1: אישור גישה למודלים ב-Bedrock

1. היכנסו ל-[AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
2. נווטו ל-**Model Access** בתפריט הצד
3. בקשו גישה למודל: **Claude Sonnet 4.5** (`anthropic.claude-sonnet-4-5-20250929-v1:0`)
4. המתינו לאישור (בדרך כלל מיידי)

**אפשרות נוספת:** בדקו גישה באמצעות CLI:
```bash
aws bedrock list-foundation-models --region us-east-1 | grep claude
```

---

### שלב 2: הגדרת IAM Policy

יש להוסיף Policy זו ל-IAM Role/User שמריץ את האפליקציה:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListInferenceProfiles"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:inference-profile/*",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-sonnet-4-5-*"
      ]
    }
  ]
}
```

**שימו לב:** אם אתם רוצים להגביל לאזור ספציפי, החליפו את ה-`*` ב-Resource לאזור המתאים (לדוגמה: `us-east-1`).

---

### שלב 3: הגדרת Credentials ל-AWS

בחרו אחת מהשיטות הבאות:

#### אפשרות A: AWS CLI Profile (מומלץ בפיתוח)
```bash
aws configure
# AWS Access Key ID: <YOUR_KEY>
# AWS Secret Access Key: <YOUR_SECRET>
# Default region: us-east-1
```

#### אפשרות B: Environment Variables (מומלץ בייצור)
```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_SESSION_TOKEN="YOUR_TOKEN"  # אופציונלי - לזמני בלבד
```

#### אפשרות C: IAM Role (מומלץ ב-EC2/ECS/Lambda)
אין צורך בהגדרה - האפליקציה תיקח את ה-credentials אוטומטית מה-Instance Metadata.

#### אפשרות D: Bedrock API Key (חדש!)
```bash
export AWS_BEARER_TOKEN_BEDROCK="YOUR_BEDROCK_API_KEY"
```

---

### שלב 4: עריכת קובץ `.env` (שינויים נדרשים!)

פתחו את הקובץ `/home/adminuser/projects/Excel_Insights_CC_SDK_wsl/.env` וערכו:

#### **לפני (מצב נוכחי):**
```bash
# Claude Agent SDK Environment Configuration
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# SendGrid Configuration (for email notifications)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=excel_insights
DB_USER=excel_user
DB_PASSWORD=test_password_qwer

# Flask Configuration
SECRET_KEY=744c22cf7b8eb41c979a621d7fc82a7b7c5c91b054c9a80f65a929d52207ce72
```

#### **אחרי (מצב Bedrock):**
```bash
# =============================================================================
# AWS Bedrock Configuration - ENABLED
# =============================================================================

# ✅ Enable Bedrock (REQUIRED!)
CLAUDE_CODE_USE_BEDROCK=1

# ✅ AWS Region (REQUIRED!)
AWS_REGION=us-east-1

# ✅ Model ID - Global Cross-Region Inference Profile (RECOMMENDED)
ANTHROPIC_MODEL=global.anthropic.claude-sonnet-4-5-20250929-v1:0

# ✅ Small/Fast Model for fallback (OPTIONAL)
ANTHROPIC_SMALL_FAST_MODEL=anthropic.claude-3-5-haiku-20241022-v1:0

# ✅ Token Limits for Bedrock (RECOMMENDED)
CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096
MAX_THINKING_TOKENS=1024

# ❌ No longer needed (comment out or delete)
# ANTHROPIC_API_KEY=sk-ant-api03-...

# 🔒 Prompt Caching (enabled by default, disable if needed)
# DISABLE_PROMPT_CACHING=1

# =============================================================================
# AWS Credentials (choose ONE method)
# =============================================================================
# Option A: Environment variables (for EC2/ECS without IAM role)
# AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
# AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
# AWS_SESSION_TOKEN=YOUR_TOKEN  # Optional

# Option B: Use AWS CLI profile (default profile used automatically)
# AWS_PROFILE=default

# Option C: Bedrock API Key (new feature)
# AWS_BEARER_TOKEN_BEDROCK=YOUR_BEDROCK_API_KEY

# =============================================================================
# Other Services (UNCHANGED)
# =============================================================================

# SendGrid Configuration (for email notifications)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=excel_insights
DB_USER=excel_user
DB_PASSWORD=test_password_qwer

# Flask Configuration
SECRET_KEY=744c22cf7b8eb41c979a621d7fc82a7b7c5c91b054c9a80f65a929d52207ce72
```

---

### שלב 5: בדיקת התצורה

לפני הרצת האפליקציה, בדקו שהכל מוגדר נכון:

```bash
# בדיקה 1: בדקו שמשתני הסביבה נטענו
cd /home/adminuser/projects/Excel_Insights_CC_SDK_wsl
source .env  # או: export $(cat .env | grep -v '^#' | xargs)

echo "Bedrock enabled: $CLAUDE_CODE_USE_BEDROCK"
echo "AWS Region: $AWS_REGION"
echo "Model ID: $ANTHROPIC_MODEL"

# בדיקה 2: בדקו גישה ל-Bedrock
aws bedrock list-foundation-models --region $AWS_REGION | grep claude-sonnet-4-5

# בדיקה 3: בדקו Inference Profiles
aws bedrock list-inference-profiles --region $AWS_REGION

# בדיקה 4 (אופציונלי): בדיקת InvokeModel ישירה
aws bedrock invoke-model \
  --region us-east-1 \
  --model-id anthropic.claude-sonnet-4-5-20250929-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}' \
  /tmp/test_output.json

cat /tmp/test_output.json
```

---

### שלב 6: הפעלת האפליקציה

```bash
cd /home/adminuser/projects/Excel_Insights_CC_SDK_wsl

# טענו את משתני הסביבה החדשים
export $(cat .env | grep -v '^#' | xargs)

# הפעילו את האפליקציה
python app.py
```

**פלט צפוי:**
```
✅ API Key loaded: sk-ant-api03-...  ← זה עדיין יכול להופיע (לא משנה)
DEBUG: API Key in environment: ...
DEBUG: Agent configured:
  - Model: sonnet
  - MCP servers: ['excel_tools']
  - Permission mode: bypassPermissions
  - Working directory: ...
  - API key from env: ANTHROPIC_API_...
```

---

### שלב 7: בדיקת פונקציונליות

1. **העלאת קובץ Excel:**
   - פתחו דפדפן: http://localhost:5000
   - התחברו עם: `admin` / `admin` (או `demo` / `demo`)
   - העלו קובץ Excel לדוגמה
   - וודאו שהניתוח מתחיל

2. **בדיקת לוגים:**
   ```bash
   # ראה בלוגים של Flask - אמור להופיע:
   DEBUG: Received event type: ...
   Flask received event: ...
   ```

3. **בדיקת דשבורד:**
   - וודאו שהדשבורד נוצר בהצלחה
   - בדקו שהתרשימים מוצגים
   - בדקו שהטקסט בעברית (default behavior)

4. **בדיקת עלויות ב-AWS:**
   ```bash
   # ראה Usage במסוף AWS:
   # https://console.aws.amazon.com/bedrock → Usage
   ```

---

## 🔍 פתרון בעיות נפוצות (Troubleshooting)

### בעיה 1: `Region not supported`
**פתרון:** בדקו שהאזור תומך ב-Claude Sonnet 4.5:
```bash
aws bedrock list-foundation-models --region us-east-1 | grep claude-sonnet-4-5
```
אזורים נתמכים: `us-east-1`, `us-west-2`, `eu-west-1`, `ap-northeast-1`

---

### בעיה 2: `AccessDeniedException`
**פתרון:** בדקו את ה-IAM Policy:
```bash
aws iam get-user-policy --user-name YOUR_USER --policy-name BedrockAccess
# או
aws iam get-role-policy --role-name YOUR_ROLE --policy-name BedrockAccess
```

וודאו שה-Policy כולל את ה-Actions:
- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`

---

### בעיה 3: `Model not found` או `On-demand throughput not supported`
**פתרון:** השתמשו ב-**Inference Profile** במקום Model ID ישיר:

```bash
# ❌ לא יעבוד (במקרים מסוימים):
ANTHROPIC_MODEL=anthropic.claude-sonnet-4-5-20250929-v1:0

# ✅ יעבוד (מומלץ):
ANTHROPIC_MODEL=global.anthropic.claude-sonnet-4-5-20250929-v1:0
```

---

### בעיה 4: `/login doesn't work`
**זה צפוי!** Bedrock לא תומך במנגנון `/login` של Claude CLI.
אימות נעשה רק דרך AWS credentials.
האפליקציה שלכם משתמשת באימות עצמאי (users.xml) - זה ממשיך לעבוד כרגיל.

---

### בעיה 5: `ANTHROPIC_API_KEY still required`
אם האפליקציה עדיין דורשת API Key למרות `CLAUDE_CODE_USE_BEDROCK=1`:

**פתרון זמני:** השאירו `ANTHROPIC_API_KEY` בקובץ `.env` (גם אם הוא לא בשימוש), או השתמשו בערך dummy:
```bash
ANTHROPIC_API_KEY=sk-dummy-key-for-bedrock
```

Claude Agent SDK **אמור** לדלג על API key כאשר `CLAUDE_CODE_USE_BEDROCK=1`, אבל במקרים מסוימים זה עדיין נבדק.

---

### בעיה 6: Tool-use cutoffs (תגובות חתוכות)
**פתרון:** הגדירו token limits נמוכים יותר (Bedrock דורש זאת):
```bash
CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096
MAX_THINKING_TOKENS=1024
```

---

## 📊 השוואת עלויות

| Model | Anthropic Direct API | AWS Bedrock (us-east-1) |
|-------|---------------------|-------------------------|
| Claude Sonnet 4.5 | $3 / 1M input tokens<br>$15 / 1M output tokens | ~$3 / 1M input tokens<br>~$15 / 1M output tokens |
| Claude Haiku 3.5 | $0.80 / 1M input tokens<br>$4 / 1M output tokens | ~$0.80 / 1M input tokens<br>~$4 / 1M output tokens |

**הערות:**
- מחירי Bedrock דומים ל-API הישיר, אבל ישנן הפתעות במקרים מסוימים
- **Prompt Caching** יכול להוזיל משמעותית (עד 90% הנחה)
- בדקו מחירים עדכניים: [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

---

## 🎯 מה נשאר ללא שינוי?

✅ **אף שורת קוד לא משתנה!**
- `agent_service.py` - ללא שינוי
- `app.py` - ללא שינוי
- `database.py` - ללא שינוי
- `users.xml` - ללא שינוי
- `requirements.txt` - ללא שינוי

✅ **כל הפונקציות קיימות:**
- ניתוח Excel
- יצירת דשבורדים
- משוב (refinement)
- התראות דוא"ל
- היסטוריה
- אימות משתמשים

✅ **רק משתני סביבה משתנים:**
- הוספת `CLAUDE_CODE_USE_BEDROCK=1`
- הוספת `AWS_REGION`
- שינוי `ANTHROPIC_MODEL` ל-inference profile
- הוספת AWS credentials (במידת הצורך)

---

## 📚 קישורים נוספים

- [Claude Code on Amazon Bedrock - מדריך רשמי](https://docs.claude.com/en/docs/claude-code/amazon-bedrock)
- [Claude Agent SDK Overview](https://docs.claude.com/en/api/agent-sdk/overview)
- [AWS Bedrock - Supported Models](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)
- [AWS Bedrock - Inference Profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-how.html)
- [Global Cross-Region Inference](https://aws.amazon.com/blogs/machine-learning/unlock-global-ai-inference-scalability-using-new-global-cross-region-inference-on-amazon-bedrock-with-anthropics-claude-sonnet-4-5/)

---

## 🚀 סיכום מהיר (TL;DR)

```bash
# 1. בקשו גישה למודל ב-AWS Bedrock Console
# 2. הגדירו IAM Policy עם bedrock:InvokeModel
# 3. הגדירו AWS credentials (CLI/env vars/IAM role)
# 4. ערכו .env:

echo "CLAUDE_CODE_USE_BEDROCK=1" >> .env
echo "AWS_REGION=us-east-1" >> .env
sed -i 's|ANTHROPIC_MODEL=.*|ANTHROPIC_MODEL=global.anthropic.claude-sonnet-4-5-20250929-v1:0|' .env
echo "CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096" >> .env
echo "MAX_THINKING_TOKENS=1024" >> .env

# 5. הפעילו מחדש
python app.py

# 6. בדקו שהכל עובד - העלו קובץ Excel
```

**זהו! אין שינויי קוד. רק environment variables.**

---

**מוכן לשאלות? צרו קשר עם צוות הפיתוח.**

**נוצר עבור:** Excel Insights Application
**גרסה:** 1.0
**תאריך:** אוקטובר 2025
**מחבר:** Claude (Sonnet 4.5) 🤖
