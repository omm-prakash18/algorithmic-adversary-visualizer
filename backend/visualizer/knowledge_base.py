"""
Comprehensive Algorithm Visualization Knowledge Base (v2.0)
============================================================
Contains expert-level documentation for 25+ algorithm patterns spanning
Trees, Graphs, Sorting, Dynamic Programming, Heaps, and Hash Tables.

Each Document is tagged with rich metadata for semantic filtering in
the ChromaDB retriever pipeline.
"""

from langchain_core.documents import Document

VISUALIZATION_KNOWLEDGE = [
    # ──────────────────── BINARY SEARCH TREE ────────────────────
    Document(
        page_content=(
            "Binary Search Tree (BST) Insertion — Recursive Implementation:\n"
            "1. If root is NULL, allocate a new node with the given value and return it as root.\n"
            "2. If value < root->val, recurse into the left subtree.\n"
            "3. If value > root->val, recurse into the right subtree.\n"
            "4. Return root after insertion completes.\n\n"
            "Visualization Steps:\n"
            "- 'create_root': First insertion creates the root node. Include id=0, value, role='Root Node'.\n"
            "- 'compare': Each recursive descent logs a comparison. Include node_id, role='Current Node'.\n"
            "- 'insert_left' / 'insert_right': Terminal step with parent_id and new node data.\n"
            "- Each step must include a pedagogical 'description' explaining the algorithmic reasoning."
        ),
        metadata={"algorithm": "BST", "pattern": "recursive_insertion", "difficulty": "beginner", "category": "trees"}
    ),
    Document(
        page_content=(
            "BST Iterative Insertion:\n"
            "Uses a while loop with a trailing parent pointer instead of recursion.\n"
            "Pattern: curr = root; while(curr != NULL) { parent = curr; if(val < curr->val) curr = curr->left; else curr = curr->right; }\n"
            "Then attach new node to parent->left or parent->right.\n\n"
            "Visualization: Same schema as recursive but the step descriptions should say 'Iteratively traversing' instead of 'Recursively descending'."
        ),
        metadata={"algorithm": "BST", "pattern": "iterative_insertion", "difficulty": "beginner", "category": "trees"}
    ),
    Document(
        page_content=(
            "BST Deletion (3 cases):\n"
            "Case 1: Leaf node — simply remove it. Action: 'delete_leaf'.\n"
            "Case 2: One child — replace node with its child. Action: 'replace_with_child'.\n"
            "Case 3: Two children — find inorder successor (smallest in right subtree), copy its value, then delete the successor.\n"
            "Actions: 'find_successor', 'copy_value', 'delete_successor'.\n"
            "Each step should annotate the role: 'Target Node', 'Inorder Successor', 'Replacement'."
        ),
        metadata={"algorithm": "BST", "pattern": "deletion", "difficulty": "intermediate", "category": "trees"}
    ),
    Document(
        page_content=(
            "BST Search / Lookup:\n"
            "Start at root. If target == root->val, found. If target < root->val, go left. Else go right.\n"
            "Visualization: 'search_start' at root, then 'compare' steps with role='Searching', ending with 'found' or 'not_found'.\n"
            "For not_found, include a description: 'Reached NULL — value does not exist in the tree.'"
        ),
        metadata={"algorithm": "BST", "pattern": "search", "difficulty": "beginner", "category": "trees"}
    ),
    Document(
        page_content=(
            "BST Traversals (Inorder, Preorder, Postorder):\n"
            "- Inorder (LNR): Visit left, visit node, visit right — yields sorted order.\n"
            "- Preorder (NLR): Visit node, visit left, visit right — useful for tree copying.\n"
            "- Postorder (LRN): Visit left, visit right, visit node — useful for deletion.\n"
            "Actions: 'visit_node' with traversal_type metadata. Each step should show the current node being visited with role='Visiting'."
        ),
        metadata={"algorithm": "BST", "pattern": "traversals", "difficulty": "beginner", "category": "trees"}
    ),
    Document(
        page_content=(
            "BST Duplicate Handling:\n"
            "If code uses 'if (val == root->val) return root;', the visualization should show a 'compare' step "
            "followed by 'no_action' with description: 'Duplicate value detected — ignoring insertion per BST property.'\n"
            "Some implementations allow duplicates by placing them in the right subtree (val >= root->val)."
        ),
        metadata={"algorithm": "BST", "pattern": "duplicate_handling", "difficulty": "beginner", "category": "trees"}
    ),
    Document(
        page_content=(
            "BST Unbalanced / Skewed Tree:\n"
            "When inputs are sorted (e.g., [1, 2, 3, 4, 5]), the BST degenerates into a linked list.\n"
            "All insertions go to the right child only, creating O(n) height.\n"
            "Visualization: Only 'insert_right' actions with descriptions warning about O(n) degradation.\n"
            "Adversary insight: This is the primary attack vector against naive BST implementations."
        ),
        metadata={"algorithm": "BST", "pattern": "skewed_tree", "difficulty": "intermediate", "category": "trees"}
    ),

    # ──────────────────── AVL TREE ────────────────────
    Document(
        page_content=(
            "AVL Tree Rotations:\n"
            "- Left Rotation (LL): When right subtree is heavy. Pivot right child up, current node becomes left child of pivot.\n"
            "- Right Rotation (RR): When left subtree is heavy. Pivot left child up, current node becomes right child of pivot.\n"
            "- Left-Right (LR): First left-rotate the left child, then right-rotate the root.\n"
            "- Right-Left (RL): First right-rotate the right child, then left-rotate the root.\n\n"
            "Visualization Actions: 'rotate_left', 'rotate_right', 'update_height', 'check_balance'.\n"
            "Each rotation should annotate the balance factor and the type of imbalance detected."
        ),
        metadata={"algorithm": "AVL", "pattern": "rotations", "difficulty": "advanced", "category": "trees"}
    ),

    # ──────────────────── HEAP / PRIORITY QUEUE ────────────────────
    Document(
        page_content=(
            "Binary Heap — Insert (Sift Up / Bubble Up):\n"
            "1. Add new element at the end of the array (last leaf position).\n"
            "2. Compare with parent (index (i-1)/2). If violates heap property, swap.\n"
            "3. Repeat until heap property is restored or root is reached.\n\n"
            "Visualization: 'insert_at_end', then 'compare_parent' + 'swap' steps moving upward.\n"
            "Roles: 'New Element', 'Parent', 'Swapping Up'."
        ),
        metadata={"algorithm": "Heap", "pattern": "insert_sift_up", "difficulty": "intermediate", "category": "trees"}
    ),
    Document(
        page_content=(
            "Binary Heap — Extract Min/Max (Sift Down / Heapify Down):\n"
            "1. Remove root element (min or max).\n"
            "2. Move last element to root position.\n"
            "3. Compare with children. Swap with the smaller (min-heap) or larger (max-heap) child.\n"
            "4. Repeat until heap property is restored.\n\n"
            "Visualization: 'extract_root', 'move_last_to_root', then 'compare_children' + 'swap_down' steps.\n"
            "Roles: 'Root', 'Last Element', 'Left Child', 'Right Child'."
        ),
        metadata={"algorithm": "Heap", "pattern": "extract_sift_down", "difficulty": "intermediate", "category": "trees"}
    ),
    Document(
        page_content=(
            "Heapify — Build Heap from Array:\n"
            "Start from the last non-leaf node (index n/2 - 1) and sift down each node.\n"
            "Time complexity: O(n), not O(n log n) — this is a common misconception.\n\n"
            "Visualization: Show the array as a tree. Highlight each node being heapified from bottom-right to root.\n"
            "Actions: 'heapify_start', 'sift_down' for each non-leaf, 'heap_complete'."
        ),
        metadata={"algorithm": "Heap", "pattern": "build_heap", "difficulty": "intermediate", "category": "trees"}
    ),

    # ──────────────────── LINKED LIST ────────────────────
    Document(
        page_content=(
            "Singly Linked List Operations:\n"
            "- Insert at head: Create node, set next to current head, update head pointer.\n"
            "- Insert at tail: Traverse to last node, set its next to new node.\n"
            "- Delete by value: Find node, update previous node's next pointer.\n"
            "- Reverse: Use three pointers (prev, curr, next) to reverse all links.\n\n"
            "Visualization Schema:\n"
            "- 'create_node': {id, value}, 'link': {source_id, target_id}, 'traverse': {node_id}\n"
            "- 'unlink': {source_id, target_id} for deletion, 'reverse_link' for reversal."
        ),
        metadata={"algorithm": "LinkedList", "pattern": "singly_linked", "difficulty": "beginner", "category": "linear"}
    ),
    Document(
        page_content=(
            "Doubly Linked List:\n"
            "Each node has prev and next pointers. Supports O(1) deletion when node reference is known.\n"
            "Visualization: Nodes arranged linearly with bidirectional arrows.\n"
            "Actions: 'create_node', 'link_forward', 'link_backward', 'delete_node'.\n"
            "Show both prev and next pointer updates during insertion and deletion."
        ),
        metadata={"algorithm": "LinkedList", "pattern": "doubly_linked", "difficulty": "beginner", "category": "linear"}
    ),

    # ──────────────────── STACK / QUEUE ────────────────────
    Document(
        page_content=(
            "Stack (LIFO) Visualization:\n"
            "Operations: push(value), pop(), peek().\n"
            "Visualize as a vertical stack growing upward.\n"
            "Actions: 'push' adds to top with animation, 'pop' removes from top with exit animation.\n"
            "Roles: 'Top of Stack', 'New Element', 'Popped Element'.\n"
            "Include stack size and capacity information in each step description."
        ),
        metadata={"algorithm": "Stack", "pattern": "lifo_operations", "difficulty": "beginner", "category": "linear"}
    ),
    Document(
        page_content=(
            "Queue (FIFO) Visualization:\n"
            "Operations: enqueue(value), dequeue(), front().\n"
            "Visualize as a horizontal queue with elements entering from right and leaving from left.\n"
            "Actions: 'enqueue' adds to rear, 'dequeue' removes from front.\n"
            "Roles: 'Front', 'Rear', 'New Element', 'Dequeued Element'."
        ),
        metadata={"algorithm": "Queue", "pattern": "fifo_operations", "difficulty": "beginner", "category": "linear"}
    ),

    # ──────────────────── GRAPH ALGORITHMS ────────────────────
    Document(
        page_content=(
            "Breadth-First Search (BFS):\n"
            "Uses a queue. Start from source, enqueue it, mark visited.\n"
            "While queue is not empty: dequeue a node, process it, enqueue all unvisited neighbors.\n"
            "Explores level by level — shortest path in unweighted graphs.\n\n"
            "Visualization Actions: 'enqueue', 'dequeue', 'visit_node', 'discover_neighbor', 'mark_visited'.\n"
            "Roles: 'Source', 'Current', 'Neighbor', 'Visited', 'In Queue'.\n"
            "Color coding: unvisited=gray, in-queue=yellow, visited=green."
        ),
        metadata={"algorithm": "Graph", "pattern": "bfs", "difficulty": "intermediate", "category": "graphs"}
    ),
    Document(
        page_content=(
            "Depth-First Search (DFS):\n"
            "Uses a stack (or recursion). Start from source, push it.\n"
            "While stack is not empty: pop a node, if not visited mark it and push all unvisited neighbors.\n"
            "Explores as deep as possible before backtracking.\n\n"
            "Visualization Actions: 'push', 'pop', 'visit_node', 'backtrack', 'discover_neighbor'.\n"
            "Roles: 'Source', 'Current', 'Backtracking', 'Neighbor'.\n"
            "Color coding: unvisited=gray, on-stack=orange, visited=green, backtracked=blue."
        ),
        metadata={"algorithm": "Graph", "pattern": "dfs", "difficulty": "intermediate", "category": "graphs"}
    ),
    Document(
        page_content=(
            "Dijkstra's Shortest Path Algorithm:\n"
            "Uses a priority queue (min-heap). Initialize distances to infinity, source to 0.\n"
            "While PQ is not empty: extract minimum, relax all adjacent edges.\n"
            "Relaxation: if dist[u] + weight(u,v) < dist[v], update dist[v] and add to PQ.\n\n"
            "Visualization: 'init_distances', 'extract_min', 'relax_edge', 'update_distance', 'shortest_path_found'.\n"
            "Show distance labels on each node, highlight the relaxation process."
        ),
        metadata={"algorithm": "Graph", "pattern": "dijkstra", "difficulty": "advanced", "category": "graphs"}
    ),

    # ──────────────────── SORTING ALGORITHMS ────────────────────
    Document(
        page_content=(
            "Bubble Sort Visualization:\n"
            "Nested loops: outer from 0 to n-1, inner from 0 to n-i-1.\n"
            "Compare adjacent elements, swap if out of order. Largest bubbles to the end.\n\n"
            "Visualization: 'compare' (highlight two elements), 'swap' (animate swap), 'mark_sorted' (element reaches final position).\n"
            "Roles: 'Comparing Left', 'Comparing Right', 'Sorted Element'.\n"
            "Show pass number and total comparisons in descriptions."
        ),
        metadata={"algorithm": "Sorting", "pattern": "bubble_sort", "difficulty": "beginner", "category": "sorting"}
    ),
    Document(
        page_content=(
            "Quick Sort Visualization:\n"
            "1. Choose pivot (last element, first element, or median-of-three).\n"
            "2. Partition: rearrange so elements < pivot are left, > pivot are right.\n"
            "3. Recursively sort left and right partitions.\n\n"
            "Visualization Actions: 'choose_pivot', 'partition_start', 'compare_to_pivot', 'swap', 'place_pivot', 'recurse_left', 'recurse_right'.\n"
            "Roles: 'Pivot', 'i-pointer', 'j-pointer', 'Partition Boundary'.\n"
            "Show the partition index and current subarray boundaries."
        ),
        metadata={"algorithm": "Sorting", "pattern": "quick_sort", "difficulty": "intermediate", "category": "sorting"}
    ),
    Document(
        page_content=(
            "Merge Sort Visualization:\n"
            "1. Divide array into two halves until single elements.\n"
            "2. Merge sorted halves by comparing front elements.\n\n"
            "Visualization: 'divide' (split array), 'compare_merge' (compare front elements), 'place_element' (put in merged array), 'merge_complete'.\n"
            "Show the recursion tree alongside the array state.\n"
            "Roles: 'Left Half', 'Right Half', 'Merged', 'Comparing'."
        ),
        metadata={"algorithm": "Sorting", "pattern": "merge_sort", "difficulty": "intermediate", "category": "sorting"}
    ),

    # ──────────────────── DYNAMIC PROGRAMMING ────────────────────
    Document(
        page_content=(
            "Dynamic Programming — Fibonacci / Memoization:\n"
            "Top-down: Recursive with memo array. Check if already computed before recursing.\n"
            "Bottom-up: Iterative, fill dp[0]=0, dp[1]=1, then dp[i] = dp[i-1] + dp[i-2].\n\n"
            "Visualization: Show the DP table being filled cell by cell.\n"
            "Actions: 'check_memo' (cache hit/miss), 'compute', 'store_result', 'return_result'.\n"
            "For top-down, also show the recursion tree with pruned branches (memoized)."
        ),
        metadata={"algorithm": "DP", "pattern": "memoization", "difficulty": "intermediate", "category": "dynamic_programming"}
    ),
    Document(
        page_content=(
            "Dynamic Programming — Knapsack (0/1):\n"
            "dp[i][w] = max value using first i items with weight capacity w.\n"
            "Transition: dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt[i]] + val[i]) if wt[i] <= w.\n\n"
            "Visualization: 2D table with items as rows and capacities as columns.\n"
            "Actions: 'consider_item', 'check_weight', 'include_item', 'exclude_item', 'fill_cell'.\n"
            "Highlight the cell being computed and the cells it depends on."
        ),
        metadata={"algorithm": "DP", "pattern": "knapsack", "difficulty": "advanced", "category": "dynamic_programming"}
    ),

    # ──────────────────── HASH TABLE ────────────────────
    Document(
        page_content=(
            "Hash Table — Chaining Collision Resolution:\n"
            "Each bucket contains a linked list. On collision, append to the list.\n"
            "Insert: hash(key) → bucket index → append to chain.\n"
            "Search: hash(key) → bucket index → traverse chain.\n\n"
            "Visualization: Show array of buckets with chains hanging below.\n"
            "Actions: 'hash_compute', 'insert_at_bucket', 'chain_traverse', 'found' / 'not_found'.\n"
            "Show the hash function computation and load factor."
        ),
        metadata={"algorithm": "HashTable", "pattern": "chaining", "difficulty": "intermediate", "category": "hashing"}
    ),

    # ──────────────────── GENERIC FORMATTING RULES ────────────────────
    Document(
        page_content=(
            "Universal Visualization Step Schema (v2.0):\n"
            "Every step MUST conform to this JSON structure:\n"
            "{\n"
            "  'step': <int>,           // Sequential step number starting from 1\n"
            "  'action': <string>,      // Machine-readable action type\n"
            "  'node': {                // Optional: node being created or modified\n"
            "    'id': <int>,\n"
            "    'value': <any>,\n"
            "    'role': <string>       // Human-readable role description\n"
            "  },\n"
            "  'node_id': <int>,        // Optional: ID of existing node being referenced\n"
            "  'parent_id': <int>,      // Optional: parent node for insertions\n"
            "  'source_id': <int>,      // Optional: source for edge operations\n"
            "  'target_id': <int>,      // Optional: target for edge operations\n"
            "  'description': <string>, // Pedagogical explanation of this step\n"
            "  'role': <string>         // Node's current role in the algorithm\n"
            "}\n\n"
            "Rules:\n"
            "- All IDs must be consistent across steps (same node = same ID).\n"
            "- Descriptions must explain WHY the action is happening, not just WHAT.\n"
            "- Roles should be algorithm-specific (e.g., 'Pivot' for quicksort, 'Root' for BST)."
        ),
        metadata={"category": "formatting", "pattern": "schema_v2"}
    ),
    Document(
        page_content=(
            "Code Pattern Recognition Rules:\n"
            "- If code contains 'left' and 'right' pointers → Tree data structure.\n"
            "- If code contains 'next' pointer only → Linked List.\n"
            "- If code contains 'push' and 'pop' → Stack.\n"
            "- If code contains 'enqueue' and 'dequeue' → Queue.\n"
            "- If code contains 'adj[' or adjacency → Graph.\n"
            "- If code contains 'dp[' or 'memo[' → Dynamic Programming.\n"
            "- If code contains 'swap' in a loop → Sorting algorithm.\n"
            "- If code contains 'hash' or '%' with array → Hash Table.\n"
            "- If code contains 'priority_queue' or 'heap' → Heap.\n\n"
            "Use these patterns to select the most relevant visualization schema."
        ),
        metadata={"category": "formatting", "pattern": "code_detection"}
    ),
]

# Precomputed metadata keys for fast filtering
ALGORITHM_CATEGORIES = {
    "trees": ["BST", "AVL", "Heap"],
    "linear": ["LinkedList", "Stack", "Queue"],
    "graphs": ["Graph"],
    "sorting": ["Sorting"],
    "dynamic_programming": ["DP"],
    "hashing": ["HashTable"],
}
