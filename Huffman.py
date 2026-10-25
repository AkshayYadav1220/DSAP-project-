import tkinter as tk
from tkinter import messagebox, ttk
from collections import deque

# ==========================================
# 1. ALGORITHM LOGIC (Separated from GUI) finalized code 
# ==========================================

class Node:
    """Class representing a node in the Huffman Tree."""
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

def merge_sort(arr):
    """
    Custom Merge Sort algorithm to sort leaf nodes by frequency.
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left_half = merge_sort(arr[:mid])
    right_half = merge_sort(arr[mid:])
    
    return merge(left_half, right_half)

def merge(left, right):
    """Helper function to merge two sorted arrays of Nodes."""
    sorted_arr = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i].freq <= right[j].freq:
            sorted_arr.append(left[i])
            i += 1
        else:
            sorted_arr.append(right[j])
            j += 1
            
    # Append any remaining elements
    sorted_arr.extend(left[i:])
    sorted_arr.extend(right[j:])
    return sorted_arr

def get_min_node(q1, q2):
    """
    Helper for the two-queue Huffman algorithm.
    Extracts and returns the node with the smallest frequency from the fronts of q1 and q2.
    """
    if not q1:
        return q2.popleft()
    if not q2:
        return q1.popleft()
    
    if q1[0].freq <= q2[0].freq:
        return q1.popleft()
    else:
        return q2.popleft()

def build_huffman_tree(sorted_nodes):
    """
    Builds the Huffman tree using the Two-Queue method.
    Time Complexity: O(n) given that the input list is already sorted.

    Returns:
        root      - root node of the finished tree
        steps     - list of text descriptions of each merge
        snapshots - list of dicts, one per stage, used for the step-by-step
                    visualization. Each dict has:
                      "forest": list of root nodes of all current sub-trees
                      "new":    the node created in this step (None at start)
                      "msg":    text description of this stage
    """
    # Queue 1 holds the sorted leaf nodes
    q1 = deque(sorted_nodes)
    # Queue 2 holds the newly created merged internal nodes
    q2 = deque()
    
    steps = [] # Log of merge operations
    snapshots = [{
        "forest": list(q1),
        "new": None,
        "msg": "Start: every character is its own tree (sorted by frequency)."
    }]
    
    # Loop until there is only 1 node remaining (the root)
    while len(q1) + len(q2) > 1:
        # Take the two smallest nodes
        left = get_min_node(q1, q2)
        right = get_min_node(q1, q2)
        
        merged_freq = left.freq + right.freq
        
        # Format names for logging
        left_name = left.char if left.char else "MergedNode"
        right_name = right.char if right.char else "MergedNode"
        steps.append(f"Merged {left_name}({left.freq}) + {right_name}({right.freq}) = {merged_freq}")
        
        # Create parent node and enqueue to q2
        merged_node = Node(char=None, freq=merged_freq, left=left, right=right)
        q2.append(merged_node)
        
        # Save the state of the forest after this merge (sorted for display)
        snapshots.append({
            "forest": merge_sort(list(q1) + list(q2)),
            "new": merged_node,
            "msg": steps[-1]
        })
        
    root = get_min_node(q1, q2)
    return root, steps, snapshots

def generate_codes(node, current_code, codes_dict):
    """
    Recursively traverses the tree to assign 0 to left edges and 1 to right edges.
    Time Complexity: O(n) where n is the number of nodes in the tree.
    """
    if node is None:
        return
    
    # If it's a leaf node, assign the accumulated code
    if node.char is not None:
        codes_dict[node.char] = current_code
        return
    
    generate_codes(node.left, current_code + "0", codes_dict)
    generate_codes(node.right, current_code + "1", codes_dict)


# ==========================================
# 2. GUI APPLICATION (tkinter)
# ==========================================

class HuffmanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Huffman Tree Builder with Merge Sort")
        self.root.geometry("1400x800")
        
        self.inputs = [] # List of tuples (char, freq)
        self.huffman_codes = {}
        self.reverse_codes = {}
        self.tree_root = None
        
        # --- State for step-by-step mode ---
        self.sorted_nodes = []
        self.steps = []
        self.snapshots = []
        self.step_index = 0
        self.auto_job = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- LEFT PANEL: Input and Tables ---
        left_frame = tk.Frame(self.root, width=350, bd=2, relief=tk.SUNKEN, padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(left_frame, text="Input Characters", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Input fields
        input_form = tk.Frame(left_frame)
        input_form.pack(pady=5)
        tk.Label(input_form, text="Char:").grid(row=0, column=0)
        self.char_entry = tk.Entry(input_form, width=8)
        self.char_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(input_form, text="Freq:").grid(row=0, column=2)
        self.freq_entry = tk.Entry(input_form, width=8)
        self.freq_entry.grid(row=0, column=3, padx=5)
        
        tk.Button(left_frame, text="Add Pair", command=self.add_pair, bg="lightblue").pack(fill=tk.X, pady=5)
        
        # Control Buttons
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="Load Example", command=self.load_example).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(btn_frame, text="Reset", command=self.reset).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=2)
        
        tk.Button(left_frame, text="Build Huffman Tree", command=self.build_tree, bg="lightgreen", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=(10, 5))
        
        # --- NEW: Step-by-step controls ---
        tk.Button(left_frame, text="Build Step-by-Step", command=self.start_step_mode,
                  bg="orange", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=(5, 3))
        
        step_btn_frame = tk.Frame(left_frame)
        step_btn_frame.pack(fill=tk.X)
        tk.Button(step_btn_frame, text="< Prev", command=self.prev_step).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(step_btn_frame, text="Next >", command=self.next_step).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.auto_btn = tk.Button(step_btn_frame, text="Auto Play", command=self.toggle_auto_play)
        self.auto_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        self.step_label = tk.Label(left_frame, text="Step mode not started", fg="darkblue",
                                   wraplength=300, justify=tk.LEFT)
        self.step_label.pack(pady=5)
        
        # Unsorted Table
        tk.Label(left_frame, text="1. Unsorted Input").pack()
        self.unsorted_tree = ttk.Treeview(left_frame, columns=("Char", "Freq"), show="headings", height=5)
        self.unsorted_tree.heading("Char", text="Character")
        self.unsorted_tree.heading("Freq", text="Frequency")
        self.unsorted_tree.column("Char", width=100, anchor=tk.CENTER)
        self.unsorted_tree.column("Freq", width=100, anchor=tk.CENTER)
        self.unsorted_tree.pack(fill=tk.X, pady=5)
        
        # Sorted Table
        tk.Label(left_frame, text="2. After Merge Sort").pack()
        self.sorted_tree = ttk.Treeview(left_frame, columns=("Char", "Freq"), show="headings", height=5)
        self.sorted_tree.heading("Char", text="Character")
        self.sorted_tree.heading("Freq", text="Frequency")
        self.sorted_tree.column("Char", width=100, anchor=tk.CENTER)
        self.sorted_tree.column("Freq", width=100, anchor=tk.CENTER)
        self.sorted_tree.pack(fill=tk.X, pady=5)
        
        # --- MIDDLE PANEL: Tree Canvas ---
        mid_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        mid_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        tk.Label(mid_frame, text="3. Huffman Tree Visualization", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Scrollbars so large forests/trees never get cut off
        x_scroll = tk.Scrollbar(mid_frame, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        y_scroll = tk.Scrollbar(mid_frame, orient=tk.VERTICAL)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(mid_frame, bg="white",
                                xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        x_scroll.config(command=self.canvas.xview)
        y_scroll.config(command=self.canvas.yview)
        
        # --- RIGHT PANEL: Logs and Output ---
        right_frame = tk.Frame(self.root, width=350, bd=2, relief=tk.SUNKEN, padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Code Table
        tk.Label(right_frame, text="4. Huffman Codes Table", font=("Arial", 12, "bold")).pack()
        self.code_tree = ttk.Treeview(right_frame, columns=("Char", "Freq", "Code", "Len"), show="headings", height=8)
        for col, text, w in [("Char", "Char", 50), ("Freq", "Freq", 50), ("Code", "Code", 100), ("Len", "Length", 50)]:
            self.code_tree.heading(col, text=text)
            self.code_tree.column(col, width=w, anchor=tk.CENTER)
        self.code_tree.pack(fill=tk.X, pady=5)
        
        # Merge Steps
        tk.Label(right_frame, text="Merge Steps (Two-Queue Method)").pack()
        self.steps_text = tk.Text(right_frame, height=8, width=40, state=tk.DISABLED)
        self.steps_text.pack(pady=5)
        
        # Encoder / Decoder
        tk.Label(right_frame, text="5. Encoder / Decoder", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(right_frame, text="Type text to encode OR binary to decode:").pack()
        self.lookup_entry = tk.Entry(right_frame, width=35)
        self.lookup_entry.pack(pady=5)
        
        tk.Button(right_frame, text="Process Lookup", command=self.process_lookup).pack()
        
        self.lookup_result = tk.Text(right_frame, height=5, width=40, state=tk.DISABLED)
        self.lookup_result.pack(pady=5)

    # --- ACTION METHODS ---
    
    def add_pair(self):
        char = self.char_entry.get().strip()
        freq_str = self.freq_entry.get().strip()
        
        # Validation
        if len(char) != 1:
            messagebox.showerror("Error", "Please enter exactly one character.")
            return
        if any(c == char for c, f in self.inputs):
            messagebox.showerror("Error", "Character already exists. No duplicates allowed.")
            return
        if not freq_str.isdigit() or int(freq_str) <= 0:
            messagebox.showerror("Error", "Frequency must be a positive number.")
            return
            
        freq = int(freq_str)
        self.inputs.append((char, freq))
        self.unsorted_tree.insert("", tk.END, values=(char, freq))
        
        self.char_entry.delete(0, tk.END)
        self.freq_entry.delete(0, tk.END)
        self.char_entry.focus()

    def load_example(self):
        self.reset()
        example_data = [('A', 5), ('B', 9), ('C', 12), ('D', 13), ('E', 16), ('F', 45)]
        for char, freq in example_data:
            self.inputs.append((char, freq))
            self.unsorted_tree.insert("", tk.END, values=(char, freq))

    def reset(self):
        self.stop_auto_play()
        self.inputs.clear()
        self.huffman_codes.clear()
        self.reverse_codes.clear()
        self.tree_root = None
        self.sorted_nodes = []
        self.steps = []
        self.snapshots = []
        self.step_index = 0
        self.step_label.config(text="Step mode not started")
        
        for tree in [self.unsorted_tree, self.sorted_tree, self.code_tree]:
            for row in tree.get_children():
                tree.delete(row)
                
        self.update_text_widget(self.steps_text, "")
        self.update_text_widget(self.lookup_result, "")
        self.canvas.delete("all")
        self.canvas.configure(scrollregion=(0, 0, 0, 0))

    # --- SHARED HELPERS (used by both normal build and step-by-step build) ---

    def compute_tree(self):
        """Runs merge sort + two-queue Huffman and fills the sorted table."""
        nodes = [Node(char, freq) for char, freq in self.inputs]
        self.sorted_nodes = merge_sort(nodes)
        
        for row in self.sorted_tree.get_children():
            self.sorted_tree.delete(row)
        for node in self.sorted_nodes:
            self.sorted_tree.insert("", tk.END, values=(node.char, node.freq))
            
        self.tree_root, self.steps, self.snapshots = build_huffman_tree(self.sorted_nodes)

    def finalize_codes(self):
        """Generates the codes from the finished tree and fills the code table."""
        self.huffman_codes = {}
        generate_codes(self.tree_root, "", self.huffman_codes)
        self.reverse_codes = {v: k for k, v in self.huffman_codes.items()}
        
        for row in self.code_tree.get_children():
            self.code_tree.delete(row)
        for node in self.sorted_nodes:
            code = self.huffman_codes[node.char]
            self.code_tree.insert("", tk.END, values=(node.char, node.freq, code, len(code)))

    def clear_codes(self):
        """Removes codes (used while the tree is still under construction)."""
        self.huffman_codes = {}
        self.reverse_codes = {}
        for row in self.code_tree.get_children():
            self.code_tree.delete(row)

    # --- NORMAL (INSTANT) BUILD ---

    def build_tree(self):
        if len(self.inputs) < 2:
            messagebox.showerror("Error", "At least 2 characters are required to build a Huffman Tree.")
            return
        
        self.stop_auto_play()
        self.compute_tree()
        self.update_text_widget(self.steps_text, "\n".join(self.steps))
        self.finalize_codes()
        
        # Jump straight to the final stage in the snapshot list
        self.step_index = len(self.snapshots) - 1
        self.step_label.config(text="Full tree built. Click 'Build Step-by-Step' to watch it form.")
        self.draw_forest([self.tree_root])

    # --- NEW: STEP-BY-STEP BUILD ---

    def start_step_mode(self):
        """Starts (or restarts) the step-by-step visualization from the first stage."""
        if len(self.inputs) < 2:
            messagebox.showerror("Error", "At least 2 characters are required to build a Huffman Tree.")
            return
        
        self.stop_auto_play()
        self.compute_tree()
        self.clear_codes()
        self.update_text_widget(self.lookup_result, "")
        self.step_index = 0
        self.show_step()

    def show_step(self):
        """Draws the forest for the current step and updates logs/labels."""
        snap = self.snapshots[self.step_index]
        last = len(self.snapshots) - 1
        
        self.draw_forest(snap["forest"], highlight=snap["new"])
        
        # Show only the merges done so far
        self.update_text_widget(self.steps_text, "\n".join(self.steps[:self.step_index]))
        
        msg = f"Step {self.step_index} of {last}:  {snap['msg']}"
        if self.step_index == last:
            msg += "\nTree complete! Codes generated."
            self.finalize_codes()
        else:
            self.clear_codes()
        self.step_label.config(text=msg)

    def next_step(self):
        if not self.snapshots:
            messagebox.showinfo("Info", "Click 'Build Step-by-Step' first.")
            return
        if self.step_index < len(self.snapshots) - 1:
            self.step_index += 1
            self.show_step()
        else:
            self.stop_auto_play()

    def prev_step(self):
        if not self.snapshots:
            messagebox.showinfo("Info", "Click 'Build Step-by-Step' first.")
            return
        self.stop_auto_play()
        if self.step_index > 0:
            self.step_index -= 1
            self.show_step()

    def toggle_auto_play(self):
        if self.auto_job is not None:
            self.stop_auto_play()
            return
        
        if not self.snapshots or self.step_index >= len(self.snapshots) - 1:
            self.start_step_mode()
            if not self.snapshots:  # start_step_mode failed validation
                return
        
        self.auto_btn.config(text="Pause")
        self.auto_job = self.root.after(1200, self.auto_tick)

    def auto_tick(self):
        if self.step_index < len(self.snapshots) - 1:
            self.step_index += 1
            self.show_step()
            self.auto_job = self.root.after(1200, self.auto_tick)
        else:
            self.stop_auto_play()

    def stop_auto_play(self):
        if self.auto_job is not None:
            self.root.after_cancel(self.auto_job)
            self.auto_job = None
        self.auto_btn.config(text="Auto Play")

    # --- DRAWING ---

    def draw_forest(self, forest, highlight=None):
        """
        Draws one or more trees side by side on the canvas.
        Leaves are spaced evenly and each parent is centred over its children,
        so nodes never overlap. 'highlight' is the newly merged node (orange).
        """
        self.canvas.delete("all")
        
        x_unit, y_gap, margin, tree_gap, r = 55, 75, 40, 40, 18
        positions = {}
        cursor = [margin]
        
        def layout(node, depth):
            if node.left is None and node.right is None:
                x = cursor[0]
                cursor[0] += x_unit
            else:
                xl = layout(node.left, depth + 1)
                xr = layout(node.right, depth + 1)
                x = (xl + xr) / 2
            positions[node] = (x, 40 + depth * y_gap)
            return x
        
        for tree in forest:
            layout(tree, 0)
            cursor[0] += tree_gap
        
        # Draw edges first so circles sit on top of the lines
        for node, (x, y) in positions.items():
            for child, label in ((node.left, "0"), (node.right, "1")):
                if child is not None:
                    cx, cy = positions[child]
                    self.canvas.create_line(x, y, cx, cy, fill="black", width=2)
                    offset = -10 if label == "0" else 10
                    self.canvas.create_text((x + cx) / 2 + offset, (y + cy) / 2 - 6,
                                            text=label, fill="red", font=("Arial", 12, "bold"))
        
        # Draw nodes
        for node, (x, y) in positions.items():
            if node is highlight:
                color = "orange"
            elif node.char is not None:
                color = "lightgreen"
            else:
                color = "lightblue"
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="black")
            label = f"{node.char}\n{node.freq}" if node.char is not None else str(node.freq)
            self.canvas.create_text(x, y, text=label, font=("Arial", 9, "bold"))
        
        # Let the scrollbars cover everything that was drawn
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=(0, 0, bbox[2] + margin, bbox[3] + margin))
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        
    def process_lookup(self):
        if not self.huffman_codes:
            messagebox.showerror("Error", "Build the tree first!")
            return
            
        text = self.lookup_entry.get().strip()
        if not text:
            return
            
        # Check if input is meant to be decoded (only 1s and 0s)
        if all(c in '01' for c in text):
            # Decode logic
            decoded_str = ""
            temp_code = ""
            for bit in text:
                temp_code += bit
                if temp_code in self.reverse_codes:
                    decoded_str += self.reverse_codes[temp_code]
                    temp_code = ""
            if temp_code != "": # Unfinished bits means invalid code sequence
                output = f"Invalid sequence remainder: {temp_code}"
            else:
                output = f"Decoded String:\n{decoded_str}"
        else:
            # Encode logic
            try:
                encoded_str = " ".join(self.huffman_codes[char] for char in text)
                output = f"Encoded Sequence:\n{encoded_str}"
            except KeyError as e:
                output = f"Error: Character {e} not in tree!"
                
        self.update_text_widget(self.lookup_result, output)

    def update_text_widget(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = HuffmanApp(root)
    root.mainloop()