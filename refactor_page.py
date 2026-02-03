
import re
import os

PAGE_FILE = r'c:\Users\sec\Desktop\Naspick\page.html'
NEW_JS_FILE = r'c:\Users\sec\Desktop\Naspick\new_render_page.js'

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

    # Find the start of function renderPage(data)
    match = re.search(r'function\s+renderPage\s*\(\s*data\s*\)\s*\{', content)
    if not match:
        print("Error: Could not find 'function renderPage(data) {' in page.html")
        return

    start_index = match.start()
    open_brace_index = match.end() - 1 # The '{' character
    
    # Brace counting to find the matching closing brace
    brace_count = 0
    end_index = -1
    
    for i in range(open_brace_index, len(content)):
        char = content[i]
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_index = i + 1 # Include the closing brace
                break
    
    if end_index == -1:
        print("Error: Could not find matching closing brace for renderPage function")
        # Fallback: try to find the line number I saw earlier (around 1357)
        return

    print(f"Found renderPage block: {start_index} to {end_index}")
    
    # Construct new content
    new_content = content[:start_index] + new_js + content[end_index:]
    
    with open(PAGE_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Successfully updated {PAGE_FILE}")

if __name__ == "__main__":
    main()
