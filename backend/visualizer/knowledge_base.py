from langchain_core.documents import Document

# A specialized knowledge base for algorithm visualization patterns
# This helps the AI understand how to map specific C++ code patterns to JSON visualization steps.

VISUALIZATION_KNOWLEDGE = [
    Document(
        page_content="Binary Search Tree (BST) Insertion: Standard recursive implementation. "
                     "If root is null, create root. If value < root->val, go left. If value > root->val, go right. "
                     "Visualization Schema: steps should start with 'create_root' (if empty), then 'compare' steps "
                     "for each node traversed, followed by 'insert_left' or 'insert_right'.",
        metadata={"algorithm": "BST", "pattern": "recursive_insertion"}
    ),
    Document(
        page_content="BST Duplicate Handling: If code uses 'if (val == root->val) return root;', "
                     "the visualization should show a 'compare' step followed by 'no_action' or a description saying 'Duplicate ignored'.",
        metadata={"algorithm": "BST", "pattern": "duplicate_handling"}
    ),
    Document(
        page_content="BST Unbalanced (Skewed) Tree: When inputs are sorted (e.g., [1, 2, 3, 4]), "
                     "the code will create a degenerate linked-list-like structure. "
                     "The visualizer should reflect this by only calling 'insert_right' repeatedly.",
        metadata={"algorithm": "BST", "pattern": "skewed_tree"}
    ),
    Document(
        page_content="Linked List Visualization: Nodes are arranged linearly. "
                     "Actions: 'create_node' (id, value), 'link' (source_id, target_id), 'traverse' (node_id). "
                     "Visualization Schema: Start with 'create_node' for the head, then 'link' to subsequent nodes as they are added.",
        metadata={"algorithm": "LinkedList", "pattern": "linear_structure"}
    ),
    Document(
        page_content="Stack/Queue Visualization: Vertical or horizontal stack of nodes. "
                     "Actions: 'push' (value), 'pop' (), 'enqueue' (value), 'dequeue' (). "
                     "Visualization Schema: Use 'push'/'enqueue' to add to the structure and 'pop'/'dequeue' to remove. "
                     "The UI should animate the entry and exit of nodes.",
        metadata={"algorithm": "StackQueue", "pattern": "sequential_access"}
    ),
    Document(
        page_content="Generic Action Rules: "
                     "- 'create_node': { 'step': N, 'action': 'create_node', 'node': { 'id': ID, 'value': X }, 'description': '...' } "
                     "- 'link': { 'step': N, 'action': 'link', 'source_id': SID, 'target_id': TID, 'description': '...' } "
                     "- 'traverse': { 'step': N, 'action': 'traverse', 'node_id': ID, 'description': '...' }",
        metadata={"category": "formatting"}
    )
]
