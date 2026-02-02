#!/usr/bin/env python3
"""
Code Suggester Agent
Analyzes code context from screenshots and suggests code completions/fixes.
"""

import os
import sys
from openai import OpenAI


class CodeSuggester:
    """Suggests code based on screenshot context."""

    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        self.model = "openai/gpt-4o-mini"  # Fast and good for code

    def run(self, context: str) -> str:
        """
        Generate code suggestions based on context.

        Args:
            context: Code context from screenshot (snippets, errors, intent)

        Returns:
            Formatted code suggestion
        """
        print(f"Processing context: {context[:100]}...")

        suggestion = self._generate_suggestion(context)
        return suggestion

    def _generate_suggestion(self, context: str) -> str:
        """Generate code suggestion using LLM."""

        system_prompt = """You are an expert code assistant. Based on the user's current coding context (extracted from their screen), suggest helpful code.

Your suggestions should be:
1. Directly relevant to what they're working on
2. Concise but complete
3. Well-formatted with proper syntax highlighting markers
4. Include a brief explanation of what the code does

Format your response as:
## Suggestion
[Brief description of what this code does]

```[language]
[code here]
```

## Why this helps
[1-2 sentence explanation]
"""

        user_prompt = f"""Based on this coding context from the user's screen, suggest helpful code:

{context}

Provide a relevant, helpful code suggestion."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=500,  # Keep responses concise for speed
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating suggestion: {e}"


def main():
    """CLI entrypoint."""
    if len(sys.argv) < 2:
        print("Usage: python agent.py '<code context>'")
        print("Example: python agent.py 'Working on React component, have useState hook, need to add useEffect'")
        sys.exit(1)

    context = sys.argv[1]

    try:
        agent = CodeSuggester()
        suggestion = agent.run(context)
        print("\n" + "=" * 60)
        print("CODE SUGGESTION")
        print("=" * 60 + "\n")
        print(suggestion)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
