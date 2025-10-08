"""
Chat Service for Excel File Conversations with Claude
Uses the Anthropic Python SDK for direct Messages API calls
Converts Excel to CSV text format for Claude to understand
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
from anthropic import Anthropic
import pandas as pd
import io
import re
from bs4 import BeautifulSoup

# Maximum number of user messages allowed per chat session
MAX_USER_MESSAGES = 15

# In-memory storage for chat sessions
# Structure: {run_id: {'messages': [...], 'user_message_count': int, 'file_path': str, 'file_text': str}}
chat_sessions: Dict[str, dict] = {}


class ChatService:
    """Service for managing chat conversations about Excel files."""

    def __init__(self, api_key: str):
        """Initialize the chat service with Anthropic API key."""
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5

    def _extract_dashboard_insights(self, dashboard_path: str) -> str:
        """
        Extract text insights from the dashboard HTML.

        Args:
            dashboard_path: Path to dashboard.html file

        Returns:
            Text summary of the analysis/insights
        """
        try:
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style tags
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # Limit size
            if len(text) > 10000:
                text = text[:10000] + "\n\n[... Analysis truncated ...]"

            return text

        except Exception as e:
            return f"(Could not extract dashboard insights: {str(e)})"

    def _excel_to_text(self, file_path: str, max_rows_per_sheet: int = 50) -> str:
        """
        Convert Excel file to readable text format (CSV-like).

        Args:
            file_path: Path to Excel file
            max_rows_per_sheet: Maximum number of rows to include per sheet

        Returns:
            Text representation of the Excel data
        """
        try:
            # Read Excel file
            excel_file = pd.ExcelFile(file_path)
            file_name = Path(file_path).name

            text_parts = []
            text_parts.append(f"📊 EXCEL FILE: {file_name}")
            text_parts.append(f"Total sheets: {len(excel_file.sheet_names)}")
            text_parts.append("=" * 80)
            text_parts.append("")

            # Process each sheet
            for sheet_idx, sheet_name in enumerate(excel_file.sheet_names, 1):
                df = pd.read_excel(excel_file, sheet_name=sheet_name)

                text_parts.append(f"SHEET {sheet_idx}: {sheet_name}")
                text_parts.append(f"Dimensions: {len(df)} rows × {len(df.columns)} columns")
                text_parts.append("")

                # Column information
                text_parts.append("COLUMNS:")
                for col in df.columns:
                    dtype = df[col].dtype
                    non_null = df[col].count()
                    text_parts.append(f"  • {col} ({dtype}) - {non_null}/{len(df)} non-null values")
                text_parts.append("")

                # Statistics for numeric columns
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                if numeric_cols:
                    text_parts.append("NUMERIC STATISTICS:")
                    for col in numeric_cols:
                        stats = df[col].describe()
                        text_parts.append(f"  • {col}:")
                        text_parts.append(f"    - Mean: {stats['mean']:.2f}")
                        text_parts.append(f"    - Median: {stats['50%']:.2f}")
                        text_parts.append(f"    - Min: {stats['min']:.2f}, Max: {stats['max']:.2f}")
                    text_parts.append("")

                # Sample data in CSV format
                sample_size = min(max_rows_per_sheet, len(df))
                text_parts.append(f"DATA (showing first {sample_size} rows in CSV format):")
                text_parts.append("")

                # Convert to CSV string
                csv_buffer = io.StringIO()
                df.head(sample_size).to_csv(csv_buffer, index=True, index_label='Row')
                csv_text = csv_buffer.getvalue()
                text_parts.append(csv_text)

                text_parts.append("=" * 80)
                text_parts.append("")

            result = "\n".join(text_parts)

            # Limit total size to avoid token limits (approximately 100k characters)
            if len(result) > 100000:
                result = result[:100000] + "\n\n[... Data truncated due to size ...]"

            return result

        except Exception as e:
            return f"❌ Error reading Excel file: {str(e)}"

    def initialize_session(self, run_id: str, file_path: str, dashboard_path: Optional[str] = None) -> dict:
        """
        Initialize a new chat session for a run_id.

        Args:
            run_id: Unique identifier for the analysis session
            file_path: Path to the Excel file
            dashboard_path: Optional path to dashboard.html (for including analysis context)

        Returns:
            Session info dict
        """
        if run_id not in chat_sessions:
            # Convert Excel to text once during initialization
            file_text = self._excel_to_text(file_path)

            # Extract dashboard insights if available
            dashboard_insights = None
            if dashboard_path and os.path.exists(dashboard_path):
                dashboard_insights = self._extract_dashboard_insights(dashboard_path)

            chat_sessions[run_id] = {
                'messages': [],
                'user_message_count': 0,
                'file_path': file_path,
                'file_text': file_text,  # Store text representation
                'dashboard_insights': dashboard_insights  # Store analysis context
            }

        return {
            'run_id': run_id,
            'user_message_count': chat_sessions[run_id]['user_message_count'],
            'max_messages': MAX_USER_MESSAGES,
            'remaining_messages': MAX_USER_MESSAGES - chat_sessions[run_id]['user_message_count']
        }

    def get_session_info(self, run_id: str) -> Optional[dict]:
        """Get information about a chat session."""
        if run_id not in chat_sessions:
            return None

        session = chat_sessions[run_id]
        return {
            'run_id': run_id,
            'user_message_count': session['user_message_count'],
            'max_messages': MAX_USER_MESSAGES,
            'remaining_messages': MAX_USER_MESSAGES - session['user_message_count'],
            'messages': session['messages']
        }

    def send_message(self, run_id: str, user_message: str) -> dict:
        """
        Send a message to Claude about the Excel file.

        Args:
            run_id: Unique identifier for the analysis session
            user_message: User's message/question

        Returns:
            dict with response and session info
        """
        # Check if session exists
        if run_id not in chat_sessions:
            return {
                'error': 'Chat session not found. Please initialize first.',
                'success': False
            }

        session = chat_sessions[run_id]

        # Check message limit
        if session['user_message_count'] >= MAX_USER_MESSAGES:
            return {
                'error': f'Message limit reached. Maximum {MAX_USER_MESSAGES} messages allowed per session.',
                'success': False,
                'limit_reached': True
            }

        # Get file text and dashboard insights (already extracted during initialization)
        file_text = session.get('file_text', '')
        dashboard_insights = session.get('dashboard_insights')

        # Build conversation history for API call
        api_messages = []

        # CRITICAL: Always include file context, even when loading from history
        # This ensures Claude has access to data even after page refresh

        if session['messages']:
            # We have conversation history - reconstruct with context
            # Build the full context (file + optional analysis)
            context_parts = [f"""Here is the Excel file data in CSV format:

{file_text}"""]

            if dashboard_insights:
                context_parts.append(f"""

Additionally, here is a summary of the analysis that was already performed on this data:

=== PREVIOUS ANALYSIS ===
{dashboard_insights}
=========================""")

            # Get the first user message from history
            first_user_message = session['messages'][0]['content']
            context_parts.append(f"""

Now, please answer this question: {first_user_message}""")

            # Add reconstructed first message with full context
            api_messages.append({
                "role": "user",
                "content": "\n".join(context_parts)
            })

            # Add the rest of the conversation history (skip first message, we already added it)
            for i, msg in enumerate(session['messages']):
                if i == 0:
                    continue  # Skip first user message (already added with context)

                api_messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })

            # Add current message
            api_messages.append({
                "role": "user",
                "content": user_message
            })

        else:
            # First message ever - include full context
            context_parts = [f"""Here is the Excel file data in CSV format:

{file_text}"""]

            if dashboard_insights:
                context_parts.append(f"""

Additionally, here is a summary of the analysis that was already performed on this data:

=== PREVIOUS ANALYSIS ===
{dashboard_insights}
=========================""")

            context_parts.append(f"""

Now, please answer this question: {user_message}""")

            api_messages.append({
                "role": "user",
                "content": "\n".join(context_parts)
            })

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system="""You are a helpful data analyst assistant. The user has provided an Excel file (converted to CSV format) and wants to chat with you about it.

The Excel data was shared in the first message. If a previous analysis was already performed on this data, that analysis summary is also included in the first message.

When answering:
- Be concise and clear
- Reference specific data points from the Excel data when relevant
- If a previous analysis is mentioned, acknowledge it and build upon those insights
- Use the same language as the user's question (Hebrew/English)
- If asked for calculations, show your work
- Provide actionable insights when appropriate

IMPORTANT: Always respond in the same language as the user's question. If they write in Hebrew (עברית), respond in Hebrew. If they write in English, respond in English.""",
                messages=api_messages
            )

            # Extract assistant's response
            assistant_message = response.content[0].text

            # Update session with new messages
            # Store only the user's question (not the file data) to save memory
            session['messages'].append({
                'role': 'user',
                'content': user_message
            })
            session['messages'].append({
                'role': 'assistant',
                'content': assistant_message
            })
            session['user_message_count'] += 1

            return {
                'success': True,
                'response': assistant_message,
                'user_message_count': session['user_message_count'],
                'remaining_messages': MAX_USER_MESSAGES - session['user_message_count'],
                'max_messages': MAX_USER_MESSAGES
            }

        except Exception as e:
            return {
                'error': f'Error communicating with Claude: {str(e)}',
                'success': False
            }

    def clear_session(self, run_id: str) -> bool:
        """Clear a chat session."""
        if run_id in chat_sessions:
            del chat_sessions[run_id]
            return True
        return False

    def get_conversation_history(self, run_id: str) -> Optional[List[dict]]:
        """Get the full conversation history for a session."""
        if run_id not in chat_sessions:
            return None
        return chat_sessions[run_id]['messages']


# Global chat service instance
chat_service = None

def get_chat_service() -> ChatService:
    """Get or create the global chat service instance."""
    global chat_service
    if chat_service is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not found in environment")
        chat_service = ChatService(api_key)
    return chat_service
