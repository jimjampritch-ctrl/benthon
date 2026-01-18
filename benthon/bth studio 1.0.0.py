import tkinter as tk
from tkinter import filedialog, simpledialog
import time

# =========================
# GLOBAL VARIABLES
# =========================

variables = {}
functions = {}

# =========================
# OUTPUT FUNCTION
# =========================

def safe_print(text):
    console.insert(tk.END, str(text) + "\n")
    console.see(tk.END)
    console.update_idletasks()  # force GUI to render

# =========================
# EVALUATE FUNCTION
# =========================

def evaluate(expr):
    expr = expr.strip()
    
    if expr == "input":
        # Show previous prints first
        console.update_idletasks()
        time.sleep(0.5)  # short delay so player sees text
        
        value = simpledialog.askstring("Benthon Input", "Enter a value:")
        if value is None:
            return ""
        # Convert to number if possible
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except:
            return value

    if expr in variables:
        return variables[expr]

    try:
        return eval(expr, {}, variables)
    except:
        return expr

# =========================
# INTERPRETER
# =========================

def run_lines(lines):
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        parts = line.split()

        # LET
        if parts[0] == "let":
            variables[parts[1]] = evaluate(" ".join(parts[3:]))

        # PRINT
        elif parts[0] == "print":
            safe_print(evaluate(" ".join(parts[1:])))

        # WAIT
        elif parts[0] == "wait":
            try:
                seconds = float(evaluate(" ".join(parts[1:])))
                time.sleep(seconds)
            except:
                pass

        # IF / ELSE
        elif parts[0] == "if":
            condition = evaluate(" ".join(parts[1:]))
            block, else_block = [], []
            i += 1
            while lines[i].strip() not in ("else", "end"):
                block.append(lines[i])
                i += 1
            if lines[i].strip() == "else":
                i += 1
                while lines[i].strip() != "end":
                    else_block.append(lines[i])
                    i += 1
            run_lines(block if condition else else_block)

        # WHILE
        elif parts[0] == "while":
            condition = " ".join(parts[1:])
            block = []
            i += 1
            while lines[i].strip() != "end":
                block.append(lines[i])
                i += 1
            while evaluate(condition):
                run_lines(block)

        # FUNCTION
        elif parts[0] == "function":
            name = parts[1]
            block = []
            i += 1
            while lines[i].strip() != "end":
                block.append(lines[i])
                i += 1
            functions[name] = block

        # CALL FUNCTION
        elif parts[0] == "call":
            run_lines(functions[parts[1]])

        i += 1

def run_benthon(code):
    variables.clear()
    functions.clear()
    run_lines(code.split("\n"))

# =========================
# GUI FUNCTIONS
# =========================

current_file = None

def run_code():
    console.delete("1.0", tk.END)
    code = editor.get("1.0", tk.END)
    try:
        run_benthon(code)
    except Exception as e:
        safe_print(f"Error: {e}")

def save_file():
    global current_file
    if not current_file:
        current_file = filedialog.asksaveasfilename(
            defaultextension=".bth",
            filetypes=[("Benthon Files", "*.bth")]
        )
    if current_file:
        with open(current_file, "w") as f:
            f.write(editor.get("1.0", tk.END))

def open_file():
    global current_file
    current_file = filedialog.askopenfilename(
        filetypes=[("Benthon Files", "*.bth")]
    )
    if current_file:
        with open(current_file, "r") as f:
            editor.delete("1.0", tk.END)
            editor.insert(tk.END, f.read())

# =========================
# GUI SETUP
# =========================

root = tk.Tk()
root.title("Benthon Studio")

# Menu
menu = tk.Menu(root)
file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As", command=lambda: setattr(globals(), 'current_file', None) or save_file())
menu.add_cascade(label="File", menu=file_menu)
root.config(menu=menu)

# Editor
editor = tk.Text(root, height=20, width=80)
editor.pack()

# Run Button
run_button = tk.Button(root, text="▶ Run Benthon", command=run_code)
run_button.pack(pady=5)

# Console
console = tk.Text(root, height=10, width=80, bg="black", fg="lime")
console.pack(padx=5, pady=5)

root.mainloop()