"""
LLM Factory — Multi-provider LLM support with graceful fallback
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

def get_llm_chain(api_key: str, app_type: str = "visualizer"):
    """
    Returns a LangChain pipeline for either visualizer or adversary.
    Supports OpenAI and Google Gemini providers.
    """
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    
    # 1. Select Model
    model = None
    if api_key.startswith("sk-"):
        from langchain_openai import ChatOpenAI
        model = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key,
            temperature=0.2 if app_type == "visualizer" else 0.3,
            max_tokens=2048,
            request_timeout=20,
            max_retries=0, # Fail fast
        )

    else:
        # Try Google Gemini
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            model = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.2 if app_type == "visualizer" else 0.3,
            )
        except ImportError:
            logger.warning("langchain-google-genai not installed, cannot use Google models")

    if model is None:
        raise ValueError("No valid LLM provider configured or installed")

    # 2. Select Prompt
    if app_type == "visualizer":
        system_prompt = (
            "You are a Senior Algorithm Engineer and Educational Visualizer. "
            "Task: Transform the user's code into a high-fidelity visualization sequence.\n\n"
            "TECHNICAL PROTOCOL:\n"
            "1. PARSE ENTRY: Identify the start state and input data from 'main()' or entry point.\n"
            "2. EXECUTION TRACE: Map each logic branch (if/else, while, recursion) to visual steps.\n"
            "3. ROLE-BASED TAGGING: Every node interaction must have a 'role' (e.g., 'Root', 'Pivot', 'Explorer', 'Leaf').\n"
            "4. PEDAGOGICAL DESCRIPTION: Explain the algorithmic reasoning behind every movement.\n"
            "5. ALGORITHM DETECTION: Identify the data structure and algorithm being implemented.\n\n"
            "RELEVANT KNOWLEDGE BASE PATTERNS:\n{context}\n\n"
            "JSON SCHEMA (return valid JSON only):\n"
            "{{ \"steps\": [{{ \"step\": int, \"action\": string, \"node\": {{ \"id\": int, \"value\": int, \"role\": string }}, "
            "\"node_id\": int, \"parent_id\": int, \"source_id\": int, \"target_id\": int, "
            "\"description\": string, \"role\": string }}] }}"
        )
        user_prompt = "User Code Implementation:\n{code}"
    else:
        system_prompt = (
            "You are a world-class adversarial security expert and competitive programmer. "
            "Your goal is to break the user's algorithm implementation.\n\n"
            "VULNERABILITY ANALYSIS PROTOCOL:\n"
            "1. LOGIC FLAWS: Does it handle empty structures, single elements, or duplicates correctly?\n"
            "2. RESOURCE EXHAUSTION: Can you provide input that degrades time complexity (e.g., sorted input → O(n) BST)?\n"
            "3. MEMORY SAFETY: Are there memory leaks (missing delete), dangling pointers, or null dereferences?\n"
            "4. OVERFLOW: Can extreme values (INT_MAX, INT_MIN, 0) break comparison or arithmetic logic?\n"
            "5. BOUNDARY CONDITIONS: Empty input, single element, maximum size, negative values.\n\n"
            "RELEVANT VULNERABILITY PATTERNS:\n{context}\n\n"
            "Provide a JSON response with:\n"
            "- 'adversary_feedback': A sharp, technical explanation of the exact flaw found.\n"
            "- 'edge_case_input': The exact input values to trigger the failure.\n"
            "- 'injection_attempt_detected': Boolean if the code looks like a system exploit.\n"
            "- 'vulnerability_severity': 'critical' | 'high' | 'medium' | 'low'\n"
            "- 'vulnerability_categories': List of categories (e.g., ['memory_leak', 'logic_flaw'])"
        )
        user_prompt = "Problem: {problem_type}\nCode:\n{user_code}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt),
    ])

    return prompt | model | JsonOutputParser()
