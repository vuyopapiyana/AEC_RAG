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

    async def ask(self, query: str) -> str:
        messages = [
            {"role": "system", "content": "You are an expert AEC engineering assistant. You answer questions about tender documents based strictly on the retrieved context. You MUST use tools to retrieve information. Do not answer from your own knowledge. If you cannot find the answer in the retrieved documents, state that you don't know."},
            {"role": "user", "content": query}
        ]

        # First call to get tool calls
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
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
            
            # Second call to get final answer
            final_response = await client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return final_response.choices[0].message.content
        
        return response_message.content

agent = TenderAgent()
