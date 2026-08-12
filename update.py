import io

HTML_FILE = 'frontend/index.html'

with io.open(HTML_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

CSS_OLD = '''        /* Live feed indicator */
        .live-feed {
            display: flex;'''

CSS_NEW = '''        /* Live feed indicator */
        .live-feed-container { margin-top: 16px; border-radius: 12px; overflow: hidden; border: 1px solid var(--border); background: #000; position: relative; }
        .live-feed-video { width: 100%; display: block; filter: brightness(0.9); }
        .live-feed-overlay { position: absolute; top: 12px; left: 12px; display: flex; align-items: center; gap: 8px; background: rgba(0,0,0,0.6); padding: 4px 10px; border-radius: 100px; backdrop-filter: blur(4px); }
        .live-feed-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent-red); animation: pulse 1.5s infinite; }
        .live-feed-text { font-size: 10px; color: #fff; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }'''

UI_OLD = '''                    <div className="live-feed">
                        <div className="live-feed-dot"></div>
                        <span className="live-feed-text">Live Recognition Feed</span>
                    </div>'''

UI_NEW = '''                    <div className="live-feed-container">
                        <img src="/api/video_feed" alt="Live Camera Stream" className="live-feed-video" onError={(e) => { e.target.style.display = 'none'; }} />
                        <div className="live-feed-overlay">
                            <div className="live-feed-dot"></div>
                            <span className="live-feed-text">Live Camera Feed</span>
                        </div>
                    </div>'''

# This will just replace the exact lines that I know exist
if 'className="live-feed"' in content:
    content = content.replace(UI_OLD, UI_NEW)
    print("UI replaced.")

if '.live-feed {' in content:
    # Need to replace the css block
    lines = content.split('\n')
    new_lines = []
    skip = False
    for line in lines:
        if '/* Live feed indicator */' in line:
            skip = True
            new_lines.append(CSS_NEW)
        elif skip and '/* Main content */' in line:
            skip = False
            new_lines.append(line)
        elif not skip:
            new_lines.append(line)
            
    content = '\n'.join(new_lines)
    print("CSS replaced.")

with io.open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(content)
