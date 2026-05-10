from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .knowledge_base import VISUALIZATION_KNOWLEDGE
import os
import logging

logger = logging.getLogger(__name__)

try:
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Global Vector Store to prevent re-embedding on every request
_vectorstore = None

def get_vectorstore(api_key):
    global _vectorstore
    if _vectorstore is None:
        embeddings = OpenAIEmbeddings(api_key=api_key)
        _vectorstore = InMemoryVectorStore.from_documents(
            documents=VISUALIZATION_KNOWLEDGE, 
            embedding=embeddings
        )
    return _vectorstore

class CodeToStepsView(APIView):
    def post(self, request):
        user_code = request.data.get('user_code', '')
        
        if not LANGCHAIN_AVAILABLE:
            return Response({'error': 'AI parsing unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return Response({'error': 'OpenAI API key missing'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # 1. Setup High-Performance RAG components (Lazy-loaded In-Memory)
            try:
                vectorstore = get_vectorstore(api_key)
                retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

                # 2. Retrieve relevant context
                relevant_docs = retriever.invoke(user_code)
                context = "\n\n".join([doc.page_content for doc in relevant_docs])

                # 3. Generate steps using LLM + RAG context
                model = ChatOpenAI(model="gpt-4o", api_key=api_key)
                
                system_prompt = (
                    "You are a Senior Algorithm Engineer and Educational Visualizer. "
                    "Task: Transform the user's C++ code into a high-fidelity visualization sequence. "
                    "\n\nTECHNICAL PROTOCOL:"
                    "1. PARSE ENTRY: Identify the start state and input data from 'main()'. "
                    "2. EXECUTION TRACE: Map each logic branch (if/else, while, recursion) to visual steps. "
                    "3. ROLE-BASED TAGGING: Every node interaction must have a 'role' (e.g., 'Root', 'Pivot', 'Explorer', 'Leaf'). "
                    "4. PEDAGOGICAL DESCRIPTION: explain the algorithmic reasoning behind every movement. "
                    "\n\nJSON SCHEMA: "
                    "{{ 'steps': [{{ 'step': int, 'action': string, 'node': {{ 'id': int, 'value': int, 'role': string }}, 'node_id': int, 'parent_id': int, 'source_id': int, 'target_id': int, 'description': string, 'role': string }}] }} "
                    "\n\nRELEVANT PATTERNS:\n{context}\n\n"
                    "Return valid JSON only."
                )
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("user", "User C++ Implementation:\n{code}")
                ])
                
                chain = prompt | model | JsonOutputParser()
                
                result = chain.invoke({
                    "context": context,
                    "code": user_code
                })
                
                steps = result.get('steps', result)
                return Response({'steps': steps, 'source': 'rag_professional'}, status=status.HTTP_200_OK)
                
            except Exception as ai_err:
                logger.error(f"RAG Pipeline Error: {str(ai_err)}")
                # Fallback to local simulation (rest of logic remains same)
                # Optimized Mock Fallback (Try to find ANY numbers in the code first)
                import re
                nums = [int(n) for n in re.findall(r'\d+', user_code)]
                test_data = nums[:10] if nums else [10, 5, 15, 3, 7]
                
                steps = []
                # ... (rest of simple BST fallback logic)
                # Mock Fallback Logic for BST
                steps = []
                node_counter = 0
                
                class SimpleBSTNode:
                    def __init__(self, val, id):
                        self.val, self.id = val, id
                        self.left = self.right = None

                root = None
                for val in test_data:
                    if root is None:
                        root = SimpleBSTNode(val, node_counter)
                        steps.append({'step': len(steps)+1, 'action': 'create_root', 'node': {'id': node_counter, 'value': val, 'role': 'Root Node'}, 'description': f'AI offline: Tree is empty. Creating the root node with value {val}.'})
                        node_counter += 1
                    else:
                        curr = root
                        while True:
                            steps.append({'step': len(steps)+1, 'action': 'compare', 'node_id': curr.id, 'role': 'Current Node', 'description': f'AI offline: Comparing our new value ({val}) against the current node ({curr.val}).'})
                            if val < curr.val:
                                if curr.left is None:
                                    curr.left = SimpleBSTNode(val, node_counter)
                                    steps.append({'step': len(steps)+1, 'action': 'insert_left', 'parent_id': curr.id, 'node': {'id': node_counter, 'value': val, 'role': 'New Left Child'}, 'description': f'AI offline: {val} is less than {curr.val}, and the left child is empty. Inserting {val} as the left child.'})
                                    node_counter += 1
                                    break
                                curr = curr.left
                                steps.append({'step': len(steps)+1, 'action': 'compare', 'node_id': curr.id, 'role': 'Traversing Left', 'description': f'AI offline: {val} is less than the previous node. Traversing down the left branch to node {curr.val}.'})
                            else:
                                if curr.right is None:
                                    curr.right = SimpleBSTNode(val, node_counter)
                                    steps.append({'step': len(steps)+1, 'action': 'insert_right', 'parent_id': curr.id, 'node': {'id': node_counter, 'value': val, 'role': 'New Right Child'}, 'description': f'AI offline: {val} is greater than or equal to {curr.val}, and the right child is empty. Inserting {val} as the right child.'})
                                    node_counter += 1
                                    break
                                curr = curr.right
                                steps.append({'step': len(steps)+1, 'action': 'compare', 'node_id': curr.id, 'role': 'Traversing Right', 'description': f'AI offline: {val} is greater than the previous node. Traversing down the right branch to node {curr.val}.'})
                return Response({'steps': steps, 'warning': f'AI currently unavailable ({str(ai_err)}). Using local simulation.'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
