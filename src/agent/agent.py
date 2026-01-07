import json
from typing import List, Dict, Any
from openai import AsyncOpenAI
from src.agent.tools import search_tool, lookup_clause_tool, SearchArgs, ClauseLookupArgs
import os
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "lookup_clause",
            "description": "Look up a specific contractual clause by its number.",
            "parameters": ClauseLookupArgs.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_tender",
            "description": "Search the tender documents for technical specifications, requirements, or general information.",
            "parameters": SearchArgs.model_json_schema()
        }
    }
]

class TenderAgent:
    def __init__(self):
        self.model = "gpt-4o" # or gpt-4-turbo

    async def ask_with_strategy(self, query: str, tender_id: str, strategy: str) -> str:
        messages = [
            {"role": "system", "content": f"You are an expert AEC engineering assistant. You answer questions about tender documents based strictly on the retrieved context. Strategy: {strategy}. Tender ID: {tender_id}. You MUST use tools to retrieve information. Do not answer from your own knowledge. If you cannot find the answer in the retrieved documents, state that you don't know."},
            {"role": "user", "content": query}
        ]

        # Force tool choice based on strategy
        tool_choice = "auto"
        if strategy == "BM25": # EXACT -> Force clause lookup
             tool_choice = {"type": "function", "function": {"name": "lookup_clause"}}
        
        # Note: We should pass tender_id to tools covertly or explicitly. 
        # For now, we rely on the tool args model (which we might need to update to accept tender_id).
        # But 'lookup_clause' as defined in tools.py only takes 'clause_number'.
        # We'll assume the simple tool for now.

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice=tool_choice
        )

        response_message = response.choices[0].message
        messages.append(response_message)

        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                tool_output = ""
                if function_name == "lookup_clause":
                    tool_output = await lookup_clause_tool(ClauseLookupArgs(**function_args))
                elif function_name == "search_tender":
                    tool_output = await search_tool(SearchArgs(**function_args))
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_output
                })
            
            # Second call
            final_response = await client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return final_response.choices[0].message.content
        
        # If no tool called (and strict enforcement not violated), return content
        # But for EXACT strategy, valid clause lookup should trigger a tool.
        return response_message.content

    # Deprecated direct simple 'ask' if we want strict control, but keep for simpler tests if needed.
    async def ask(self, query: str) -> str:
        return await self.ask_with_strategy(query, "default_tender", "HYBRID")

agent = TenderAgent()
