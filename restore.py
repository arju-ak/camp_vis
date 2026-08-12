import os
import re

log_path = r"C:\Users\arjun\.gemini\antigravity\brain\e910a090-27a6-469c-b3ad-9df8ab0d47a4\.system_generated\logs\implementing_frontend_dashboard.txt"
with open(log_path, 'r', encoding='utf-8') as f:
    text = f.read()

# We need to find the contents of the latest write_to_file call or replace_file_content 
# that contains the full index.html.
# Actually, the quickest way is to just find the entire `<!DOCTYPE html>` to `</html>` block.
parts = text.split("<!DOCTYPE html>")
if len(parts) > 1:
    # Get the last chunk that contains it
    last_doc = parts[-1]
    # Find </html>
    end_idx = last_doc.find("</html>")
    if end_idx != -1:
        html = "<!DOCTYPE html>" + last_doc[:end_idx + 7]
        with open(r"frontend/index.html", 'w', encoding='utf-8') as f:
            f.write(html)
        print("Restored successfully. Length:", len(html))
    else:
        print("Couldn't find </html>")
else:
    print("Couldn't find <!DOCTYPE html>")
