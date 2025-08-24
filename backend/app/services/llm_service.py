import os
from typing import Dict, Any
from openai import OpenAI

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    def format_response_for_display(self, content: str) -> Dict[str, Any]:
        """Format AI response content for better frontend display"""
        
        # Split into sections if using structured format
        sections = {}
        current_section = "content"
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers (markdown style)
            if line.startswith('##'):
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.replace('##', '').strip().lower().replace(' ', '_')
                current_content = []
            elif line.startswith('**') and line.endswith('**:'):
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.replace('**', '').replace(':', '').strip().lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # Add the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # If no sections were found, return as single content
        if len(sections) == 1 and "content" in sections:
            return {
                "formatted": True,
                "type": "simple",
                "content": content.strip()
            }
        
        return {
            "formatted": True,
            "type": "structured",
            "sections": sections,
            "raw_content": content.strip()
        }
    
    def clean_text_formatting(self, text: str) -> str:
        """Clean up text formatting for better readability"""
        if not text:
            return ""
        
        # Split into lines and clean
        lines = [line.strip() for line in text.split('\n')]
        
        # Remove empty lines at start and end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        
        # Process lines for better formatting
        formatted_lines = []
        prev_was_header = False
        
        for i, line in enumerate(lines):
            if not line:
                # Only add empty line if previous wasn't already empty
                if formatted_lines and formatted_lines[-1]:
                    formatted_lines.append("")
                continue
            
            # Handle headers (## or **)
            is_header = line.startswith('##') or (line.startswith('**') and line.endswith('**:'))
            
            # Add spacing before headers (except first line)
            if is_header and formatted_lines and formatted_lines[-1]:
                formatted_lines.append("")
            
            formatted_lines.append(line)
            prev_was_header = is_header
        
        return '\n'.join(formatted_lines)
