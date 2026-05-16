"""
Adversarial Vulnerability Knowledge Base (v2.0)
================================================
Contains expert-level security patterns for algorithmic implementations.
Used by the Adversary app to identify logic flaws, resource exhaustion,
and memory safety issues.
"""

from langchain_core.documents import Document

ADVERSARY_KNOWLEDGE = [
    Document(
        page_content=(
            "Unbalanced BST Vulnerability:\n"
            "Naive BST implementations without self-balancing (like AVL or Red-Black) "
            "are vulnerable to sorted input attacks. If elements are inserted in "
            "ascending or descending order, the tree becomes a linked list, "
            "degrading search and insertion from O(log n) to O(n).\n"
            "Detection: Look for 'left' and 'right' pointers without 'rotate' or 'balance' logic.\n"
            "Edge Case: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
        ),
        metadata={"category": "security", "vulnerability": "resource_exhaustion", "target": "trees"}
    ),
    Document(
        page_content=(
            "Integer Overflow in Accumulation:\n"
            "When summing elements or multiplying values in algorithms (like Fibonacci, "
            "factorial, or graph weights), using standard 32-bit integers can lead to "
            "wraparound errors.\n"
            "Detection: Use of 'int' for counters or sums without bounds checking.\n"
            "Edge Case: INT_MAX + 1"
        ),
        metadata={"category": "security", "vulnerability": "integer_overflow", "target": "general"}
    ),
    Document(
        page_content=(
            "Memory Leak (Missing Delete):\n"
            "In C++, allocating nodes with 'new' without corresponding 'delete' in the "
            "destructor or removal functions leads to memory exhaustion over time.\n"
            "Detection: 'new' keyword present, but 'delete' or 'free' is missing in cleanup paths.\n"
            "Edge Case: Continuous insertion and deletion of 100k nodes."
        ),
        metadata={"category": "security", "vulnerability": "memory_leak", "target": "cpp"}
    ),
    Document(
        page_content=(
            "Null Pointer Dereference:\n"
            "Accessing 'node->left' or 'node->right' without checking if 'node' is NULL "
            "will cause the program to crash (Segfault).\n"
            "Detection: Arrow operator '->' used immediately after a potential null return or parameter.\n"
            "Edge Case: Search in an empty tree / Delete from empty tree."
        ),
        metadata={"category": "security", "vulnerability": "null_dereference", "target": "general"}
    ),
    Document(
        page_content=(
            "Recursive Stack Overflow:\n"
            "Deep recursion on large structures (like a skewed tree or a long linked list) "
            "can exhaust the stack memory, leading to a crash.\n"
            "Detection: Recursive calls without depth limits or tail-call optimization.\n"
            "Edge Case: Recursion depth > 10,000."
        ),
        metadata={"category": "security", "vulnerability": "stack_overflow", "target": "general"}
    ),
]
