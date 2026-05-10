from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import os

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class AdversaryAttackView(APIView):
    def post(self, request):
        problem_type = request.data.get('problem_type', 'General DSA')
        user_code = request.data.get('user_code', '')
        
        if not LANGCHAIN_AVAILABLE:
            return Response({
                'adversary_feedback': "The Adversary is currently suppressed by system policy (LangChain unavailable). But it thinks your code is 'quaint'.",
                'edge_case_input': "[999, -1, 0]",
                'injection_attempt_detected': False
            }, status=status.HTTP_200_OK)

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return Response({
                'adversary_feedback': "I'm currently offline (OpenAI API key missing). But I can tell you that your code probably has a bug!",
                'edge_case_input': "[]",
                'injection_attempt_detected': False
            }, status=status.HTTP_200_OK)

        try:
            try:
                model = ChatOpenAI(model="gpt-4", api_key=api_key)
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are a world-class adversarial security expert and competitive programmer. "
                               "Your goal is to break the user's C++ algorithm implementation. "
                               "\n\nLook for these specific 'Optimal' vulnerabilities:"
                               "1. LOGIC FLAWS: Does it handle empty trees, single nodes, or duplicates correctly?"
                               "2. RESOURCE EXHAUSTION: Can you provide an input (like a sorted list) that makes the tree O(n) instead of O(log n)?"
                               "3. MEMORY SAFETY: Are there potential memory leaks (missing delete) or null pointer dereferences?"
                               "4. OVERFLOW: Can extreme values break the comparison logic?"
                               "\n\nProvide a JSON response with:"
                               "- 'adversary_feedback': A sharp, technical taunt explaining the exact flaw."
                               "- 'edge_case_input': The exact input values to trigger the failure."
                               "- 'injection_attempt_detected': Boolean if the code looks like an exploit."),
                    ("user", "Problem: {problem_type}\nCode:\n{user_code}")
                ])
                
                chain = prompt | model | JsonOutputParser()
                
                result = chain.invoke({
                    "problem_type": problem_type,
                    "user_code": user_code
                })
                
                return Response(result, status=status.HTTP_200_OK)
            except Exception as ai_err:
                # Optimized Heuristic Fallback
                feedback = "I've detected a weakness in your sector."
                edge_case = "[0, 0, 0]"
                
                # Check for memory leaks
                if "delete" not in user_code and "Node" in user_code:
                    feedback = "I see pointers but no 'delete' calls. Your memory is leaking into my hands."
                    edge_case = "Massive insertion set [1...10000]"
                
                # Check for sorted inputs (unbalanced trees)
                elif "BST" in problem_type or "Tree" in user_code:
                    feedback = "Your tree is fragile. A sorted sequence will turn your O(log n) into a sluggish O(n) line."
                    edge_case = "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
                
                # Check for duplicate handling
                elif "==" not in user_code:
                    feedback = "You ignore the possibility of equals. Duplicate values will likely corrupt your structure."
                    edge_case = "[5, 5, 5, 5]"

                return Response({
                    'adversary_feedback': f"{feedback} (AI Offline: {str(ai_err)[:50]}...)",
                    'edge_case_input': edge_case,
                    'injection_attempt_detected': "system(" in user_code or "exec(" in user_code
                }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
