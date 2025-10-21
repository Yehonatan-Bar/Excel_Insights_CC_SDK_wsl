"""
Agent Monitor - Detailed Tracking of Claude Agent SDK Events

This module provides comprehensive monitoring of:
- System prompts and user prompts
- All SDK events (thinking, text, tool use, tool results)
- API call tracking
- Timeline visualization
- Event categorization and filtering
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class AgentMonitor:
    """Monitor and track all Claude Agent SDK activity for debugging."""

    def __init__(self, run_id: str, output_dir: str = "outputs"):
        """
        Initialize agent monitor.

        Args:
            run_id: Unique identifier for this analysis run
            output_dir: Directory to store monitoring data
        """
        self.run_id = run_id
        self.output_dir = Path(output_dir) / run_id
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.monitoring_data = {
            'run_id': run_id,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'status': 'initializing',
            'configuration': {},
            'prompts': {},
            'events': [],
            'thinking_blocks': [],
            'tool_calls': [],
            'api_calls': [],
            'responses': [],
            'errors': [],
            'statistics': {
                'total_events': 0,
                'thinking_count': 0,
                'tool_call_count': 0,
                'api_call_count': 0,
                'error_count': 0,
                'total_tokens': 0
            }
        }

    def set_configuration(self, config: Dict[str, Any]):
        """Store agent configuration (model, options, etc.)."""
        self.monitoring_data['configuration'] = config
        self._save_snapshot()

    def set_prompts(self, system_prompt: str, user_prompt: str):
        """Store the prompts sent to the agent."""
        self.monitoring_data['prompts'] = {
            'system_prompt': system_prompt,
            'user_prompt': user_prompt,
            'timestamp': datetime.now().isoformat()
        }
        self._save_snapshot()

    def record_event(self, event: Any, event_type: str = None):
        """
        Record a raw SDK event with detailed parsing.

        Args:
            event: Raw event from Claude SDK
            event_type: Override event type (optional)
        """
        print(f"[MONITOR-DEBUG] ========== record_event() CALLED ==========")
        print(f"[MONITOR-DEBUG] Event type: {event_type or type(event).__name__}")
        print(f"[MONITOR-DEBUG] Event object type: {type(event)}")
        print(f"[MONITOR-DEBUG] Event has 'content' attr: {hasattr(event, 'content')}")
        print(f"[MONITOR-DEBUG] Current total events before: {self.monitoring_data['statistics']['total_events']}")

        timestamp = datetime.now().isoformat()

        # Build detailed event record
        event_record = {
            'timestamp': timestamp,
            'event_number': self.monitoring_data['statistics']['total_events'] + 1,
            'event_type': event_type or type(event).__name__,
            'raw_data': self._serialize_event(event)
        }

        # Parse content blocks if present
        if hasattr(event, 'content'):
            event_record['has_content'] = True
            event_record['content_blocks'] = self._parse_content_blocks(event.content)
        else:
            event_record['has_content'] = False

        # Check for errors
        if hasattr(event, 'error'):
            event_record['error'] = str(event.error)
            self.monitoring_data['errors'].append({
                'timestamp': timestamp,
                'error': str(event.error),
                'event_number': event_record['event_number']
            })
            self.monitoring_data['statistics']['error_count'] += 1

        # Store the event
        self.monitoring_data['events'].append(event_record)
        self.monitoring_data['statistics']['total_events'] += 1

        print(f"[MONITOR-DEBUG] Event stored! Total events now: {self.monitoring_data['statistics']['total_events']}")
        print(f"[MONITOR-DEBUG] Event record: {event_record}")

        # Categorize and extract specific event types
        self._categorize_event(event_record)

        # Save snapshot after EVERY event during debugging (changed from every 10)
        print(f"[MONITOR-DEBUG] Calling _save_snapshot()...")
        self._save_snapshot()
        print(f"[MONITOR-DEBUG] Snapshot saved!")

    def _parse_content_blocks(self, content) -> List[Dict[str, Any]]:
        """Parse content blocks from event."""
        content_items = content if isinstance(content, list) else [content]
        parsed_blocks = []

        for item in content_items:
            block = {
                'block_type': type(item).__name__,
                'data': {}
            }

            # Thinking block
            if hasattr(item, 'thinking'):
                block['category'] = 'thinking'
                block['data']['thinking_text'] = item.thinking
                block['data']['length'] = len(item.thinking)

            # Text block (agent response)
            elif hasattr(item, 'text'):
                block['category'] = 'text'
                block['data']['text_content'] = item.text
                block['data']['length'] = len(item.text)

            # Tool use block
            elif hasattr(item, 'name') and hasattr(item, 'input'):
                block['category'] = 'tool_use'
                block['data']['tool_name'] = item.name
                block['data']['tool_input'] = getattr(item, 'input', {})
                block['data']['tool_use_id'] = getattr(item, 'id', 'unknown')

            # Tool result block
            elif hasattr(item, 'content') and hasattr(item, 'tool_use_id'):
                block['category'] = 'tool_result'
                block['data']['tool_use_id'] = item.tool_use_id
                block['data']['is_error'] = getattr(item, 'is_error', False)

                # Extract result content
                result_content = item.content
                if isinstance(result_content, str):
                    block['data']['result_text'] = result_content
                    block['data']['result_length'] = len(result_content)
                elif isinstance(result_content, list) and len(result_content) > 0:
                    first_item = result_content[0]
                    if hasattr(first_item, 'text'):
                        block['data']['result_text'] = first_item.text
                        block['data']['result_length'] = len(first_item.text)
                    else:
                        block['data']['result_text'] = str(result_content)
                        block['data']['result_length'] = len(str(result_content))
                else:
                    block['data']['result_text'] = str(result_content)
                    block['data']['result_length'] = len(str(result_content))

            # Unknown block type
            else:
                block['category'] = 'unknown'
                block['data']['raw'] = self._serialize_event(item)

            parsed_blocks.append(block)

        return parsed_blocks

    def _categorize_event(self, event_record: Dict[str, Any]):
        """Categorize event and add to specific collections."""
        if not event_record.get('has_content'):
            return

        for block in event_record.get('content_blocks', []):
            category = block.get('category')

            if category == 'thinking':
                self.monitoring_data['thinking_blocks'].append({
                    'event_number': event_record['event_number'],
                    'timestamp': event_record['timestamp'],
                    'thinking_text': block['data']['thinking_text'],
                    'length': block['data']['length']
                })
                self.monitoring_data['statistics']['thinking_count'] += 1

            elif category == 'tool_use':
                self.monitoring_data['tool_calls'].append({
                    'event_number': event_record['event_number'],
                    'timestamp': event_record['timestamp'],
                    'tool_name': block['data']['tool_name'],
                    'tool_input': block['data']['tool_input'],
                    'tool_use_id': block['data']['tool_use_id']
                })
                self.monitoring_data['statistics']['tool_call_count'] += 1

            elif category == 'text':
                self.monitoring_data['responses'].append({
                    'event_number': event_record['event_number'],
                    'timestamp': event_record['timestamp'],
                    'text_content': block['data']['text_content'],
                    'length': block['data']['length']
                })

    def _serialize_event(self, event: Any) -> Any:
        """Convert event to JSON-serializable format."""
        if hasattr(event, "__dict__"):
            return {k: self._serialize_event(v) for k, v in event.__dict__.items() if not k.startswith("_")}
        elif isinstance(event, dict):
            return {k: self._serialize_event(v) for k, v in event.items()}
        elif isinstance(event, (list, tuple)):
            return [self._serialize_event(item) for item in event]
        else:
            return str(event) if not isinstance(event, (str, int, float, bool, type(None))) else event

    def record_api_call(self, method: str, endpoint: str, payload: Optional[Dict] = None, response: Optional[Dict] = None):
        """Record an API call made by the SDK."""
        self.monitoring_data['api_calls'].append({
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'endpoint': endpoint,
            'payload': payload,
            'response': response
        })
        self.monitoring_data['statistics']['api_call_count'] += 1
        self._save_snapshot()

    def finalize(self, status: str = 'completed'):
        """Finalize monitoring and save final snapshot."""
        self.monitoring_data['end_time'] = datetime.now().isoformat()
        self.monitoring_data['status'] = status

        # Calculate duration
        start = datetime.fromisoformat(self.monitoring_data['start_time'])
        end = datetime.fromisoformat(self.monitoring_data['end_time'])
        self.monitoring_data['duration_seconds'] = (end - start).total_seconds()

        self._save_snapshot()

    def _save_snapshot(self):
        """Save current monitoring data to file."""
        snapshot_path = self.output_dir / "agent_monitor.json"
        print(f"[MONITOR-SAVE] Saving snapshot to: {snapshot_path}")
        print(f"[MONITOR-SAVE] Total events to save: {self.monitoring_data['statistics']['total_events']}")
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(self.monitoring_data, f, indent=2, ensure_ascii=False)
        print(f"[MONITOR-SAVE] Snapshot saved successfully!")

    def get_monitoring_data(self) -> Dict[str, Any]:
        """Get current monitoring data."""
        return self.monitoring_data

    def get_timeline(self) -> List[Dict[str, Any]]:
        """Get chronological timeline of all events."""
        timeline = []

        for event in self.monitoring_data['events']:
            timeline.append({
                'timestamp': event['timestamp'],
                'event_number': event['event_number'],
                'event_type': event['event_type'],
                'has_content': event['has_content'],
                'content_summary': self._summarize_content(event)
            })

        return sorted(timeline, key=lambda x: x['timestamp'])

    def _summarize_content(self, event: Dict[str, Any]) -> str:
        """Create a brief summary of event content."""
        if not event.get('has_content'):
            return "No content"

        summaries = []
        for block in event.get('content_blocks', []):
            category = block.get('category', 'unknown')

            if category == 'thinking':
                text = block['data']['thinking_text'][:100]
                summaries.append(f"Thinking: {text}...")
            elif category == 'text':
                text = block['data']['text_content'][:100]
                summaries.append(f"Response: {text}...")
            elif category == 'tool_use':
                tool = block['data']['tool_name']
                summaries.append(f"Tool: {tool}")
            elif category == 'tool_result':
                result = str(block['data'].get('result_text', ''))[:100]
                summaries.append(f"Result: {result}...")

        return " | ".join(summaries) if summaries else "Empty content"
