"""
Claude API Service
Handles interactions with Anthropic's Claude API for conversational AI
"""

import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from anthropic import AsyncAnthropic
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ClaudeService:
    """Claude API service for conversational AI"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for EVA-Dev"""
        return """You are EVA-Dev, a specialized AI assistant for EV (Electric Vehicle) charging support. You are an expert in electric vehicle charging technology and infrastructure.

## Your Core Expertise:

### Charging Infrastructure:
- Public charging networks (ChargePoint, EVgo, Electrify America, Tesla Supercharger, etc.)
- Home charging solutions (Level 1, Level 2, smart chargers)
- Workplace and destination charging
- Fast charging (DC Fast Charging, Ultra-fast charging)

### Connector Types & Standards:
- Type 1 (J1772) - North American AC standard
- Type 2 (Mennekes) - European AC standard
- CCS (Combined Charging System) - CCS1 & CCS2
- CHAdeMO - Japanese DC fast charging standard
- Tesla connectors (NACS/Tesla proprietary)
- Adapter compatibility and usage

### Technical Troubleshooting:
- Charging session failures and error codes
- Connector fit and compatibility issues
- Payment and authentication problems
- Charging speed optimization
- Power delivery issues
- Network connectivity problems

### Cost & Efficiency:
- Time-of-use electricity rates
- Charging network pricing strategies
- Home vs. public charging economics
- Route planning with charging stops
- Battery health and charging habits

## Communication Style:
- Be conversational, helpful, and technically accurate
- Provide step-by-step troubleshooting when needed
- Ask clarifying questions to better understand the situation
- Always prioritize safety in your recommendations
- If uncertain, recommend consulting a professional or manufacturer
- Use clear, jargon-free explanations while maintaining technical accuracy
- Offer practical, actionable solutions

## Safety First:
- Never recommend unsafe electrical work
- Always suggest professional installation for home charging equipment
- Emphasize proper connector handling and inspection
- Warn about weather-related charging precautions

Remember: You're here to make EV charging easier and more reliable for everyone. Focus on practical solutions and clear guidance."""
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> Optional[str]:
        """
        Get a chat completion from Claude
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            stream: Whether to stream the response
            
        Returns:
            Response text or None if failed
        """
        try:
            # Prepare messages for Claude API
            claude_messages = []
            for msg in messages:
                if msg["role"] in ["user", "assistant"]:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            if not claude_messages:
                logger.warning("No valid messages provided to Claude")
                return None
            
            # Make API call
            response = await self.client.messages.create(
                model=settings.claude_model,
                max_tokens=settings.claude_max_tokens,
                system=self.system_prompt,
                messages=claude_messages
            )
            
            if response.content and len(response.content) > 0:
                # Extract text from response
                content = response.content[0]
                if hasattr(content, 'text'):
                    logger.info(f"Claude response generated: {len(content.text)} characters")
                    return content.text
            
            logger.warning("No content in Claude response")
            return None
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return None
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        include_context: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat completion from Claude with enhanced error handling

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            include_context: Whether to include conversation context

        Yields:
            Response text chunks
        """
        try:
            # Prepare messages for Claude API
            claude_messages = []
            for msg in messages:
                if msg["role"] in ["user", "assistant"]:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

            if not claude_messages:
                logger.warning("No valid messages provided to Claude for streaming")
                yield "I didn't receive your message clearly. Could you please try again?"
                return

            # Add context if conversation is long and context is enabled
            system_prompt = self.system_prompt
            if include_context and len(claude_messages) > 10:
                # Create a mock conversation list for context (in real implementation, this would come from the caller)
                context = self.get_conversation_context([
                    {"role": msg["role"], "content": msg["content"]} for msg in claude_messages
                ])
                if context:
                    system_prompt += f"\n\n{context}"

            # Make streaming API call with retry logic
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    async with self.client.messages.stream(
                        model=settings.claude_model,
                        max_tokens=settings.claude_max_tokens,
                        system=system_prompt,
                        messages=claude_messages,
                        temperature=0.7  # Slightly creative but focused
                    ) as stream:
                        chunk_count = 0
                        async for text in stream.text_stream:
                            chunk_count += 1
                            yield text

                    logger.info(f"Claude streaming completed successfully with {chunk_count} chunks")
                    return

                except Exception as stream_error:
                    if attempt < max_retries:
                        logger.warning(f"Streaming attempt {attempt + 1} failed, retrying: {stream_error}")
                        await asyncio.sleep(1)  # Brief delay before retry
                        continue
                    else:
                        raise stream_error

        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"Claude streaming API error: {e}")

            # Provide specific error messages based on error type
            if "rate limit" in error_msg or "quota" in error_msg:
                yield "I'm currently experiencing high demand. Please wait a moment and try again."
            elif "timeout" in error_msg or "connection" in error_msg:
                yield "I'm having trouble connecting right now. Please check your connection and try again."
            elif "authentication" in error_msg or "api key" in error_msg:
                yield "I'm experiencing authentication issues. Please contact support if this persists."
            else:
                yield "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
    
    async def test_connection(self) -> bool:
        """Test Claude API connection"""
        try:
            test_messages = [
                {"role": "user", "content": "Hello, can you confirm you're working?"}
            ]
            
            response = await self.chat_completion(test_messages)
            
            if response:
                logger.info("Claude API connection test successful")
                return True
            else:
                logger.error("Claude API connection test failed - no response")
                return False
                
        except Exception as e:
            logger.error(f"Claude API connection test error: {e}")
            return False
    
    def format_conversation_history(
        self,
        conversation: List[Dict[str, Any]],
        max_messages: int = 20,
        max_tokens_per_message: int = 1000
    ) -> List[Dict[str, str]]:
        """
        Format conversation history for Claude API with context management

        Args:
            conversation: List of conversation messages
            max_messages: Maximum number of messages to include
            max_tokens_per_message: Maximum tokens per message (approximate)

        Returns:
            Formatted messages for Claude API
        """
        formatted_messages = []

        # Take the most recent messages
        recent_conversation = conversation[-max_messages:] if len(conversation) > max_messages else conversation

        for msg in recent_conversation:
            role = msg.get("role", "")
            content = msg.get("content", "")

            # Skip empty messages
            if not content.strip():
                continue

            # Truncate very long messages (rough token estimation: 1 token ≈ 4 characters)
            if len(content) > max_tokens_per_message * 4:
                content = content[:max_tokens_per_message * 4] + "... [message truncated]"

            if role in ["user", "assistant"]:
                formatted_messages.append({
                    "role": role,
                    "content": content
                })

        # Ensure we don't have consecutive messages from the same role
        cleaned_messages = []
        last_role = None

        for msg in formatted_messages:
            if msg["role"] != last_role:
                cleaned_messages.append(msg)
                last_role = msg["role"]
            else:
                # Merge consecutive messages from the same role
                if cleaned_messages:
                    cleaned_messages[-1]["content"] += "\n\n" + msg["content"]

        return cleaned_messages

    def get_conversation_context(self, conversation: List[Dict[str, Any]]) -> str:
        """
        Generate a context summary for long conversations

        Args:
            conversation: Full conversation history

        Returns:
            Context summary string
        """
        if len(conversation) <= 10:
            return ""

        # Extract key topics and issues mentioned
        user_messages = [msg.get("content", "") for msg in conversation if msg.get("role") == "user"]

        # Simple keyword extraction for EV charging topics
        keywords = []
        ev_terms = [
            "charging", "charger", "connector", "CCS", "CHAdeMO", "Tesla", "Type 1", "Type 2",
            "Level 1", "Level 2", "DC fast", "supercharger", "error", "problem", "issue",
            "home charging", "public charging", "network", "payment", "authentication",
            "speed", "slow", "fast", "battery", "range", "cost", "price"
        ]

        for message in user_messages:
            message_lower = message.lower()
            for term in ev_terms:
                if term.lower() in message_lower and term not in keywords:
                    keywords.append(term)

        if keywords:
            return f"Previous conversation context: User has discussed {', '.join(keywords[:5])}."

        return "Previous conversation: User has been asking about EV charging topics."


# Global Claude service instance
claude_service = ClaudeService()
