
import re
import os

PAGE_FILE = r'c:\Users\sec\Desktop\Naspick\page.html'
NEW_JS_FILE = r'c:\Users\sec\Desktop\Naspick\restored_logic.js'

def main():
    if not os.path.exists(PAGE_FILE):
        print(f"Error: {PAGE_FILE} not found")
        return
    if not os.path.exists(NEW_JS_FILE):
        print(f"Error: {NEW_JS_FILE} not found")
        return

    with open(PAGE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(NEW_JS_FILE, 'r', encoding='utf-8') as f:
        new_js = f.read()

    # Try to find the start marker of the previous injection
    start_marker = "// --- Safe Rendering Helper ---"
    start_pos = content.find(start_marker)
    
    if start_pos != -1:
        print(f"Found previous injection at index {start_pos}")
        # Find the end of renderPage AFTER the start_pos
        match = re.search(r'function\s+renderPage\s*\(\s*data\s*\)\s*\{', content[start_pos:])
        if not match:
             print("Error: Could not find renderPage after start marker")
             return
        
        # Calculate absolute position of renderPage start
        func_start_rel = match.start()
        func_open_brace_rel = match.end() - 1
        
        open_brace_index = start_pos + func_open_brace_rel
        
        # Brace counting from the open brace of renderPage
        brace_count = 0
        end_index = -1
        
        for i in range(open_brace_index, len(content)):
            char = content[i]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_index = i + 1
                    break
        
        if end_index == -1:
            print("Error: Could not find closing brace")
            return
            
        # Replace from start_marker to end_index
        new_content = content[:start_pos] + new_js + content[end_index:]
        
    else:
        # First time run logic (or marker missing)
        print("Start marker not found, falling back to simple renderPage replacement")
        match = re.search(r'function\s+renderPage\s*\(\s*data\s*\)\s*\{', content)
        if not match:
            print("Error: Could not find 'function renderPage(data) {'")
            return

        start_index = match.start()
        open_brace_index = match.end() - 1
        
        brace_count = 0
        end_index = -1
        
        for i in range(open_brace_index, len(content)):
            char = content[i]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_index = i + 1
                    break
        
        if end_index == -1:
             print("Error: Could not find matching closing brace")
             return

        new_content = content[:start_index] + new_js + content[end_index:]

    
    with open(PAGE_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Successfully updated {PAGE_FILE}")

if __name__ == "__main__":
    main()
