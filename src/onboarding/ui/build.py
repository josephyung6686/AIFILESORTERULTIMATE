from pathlib import Path

project = Path(__file__).resolve().parent
source = project / 'source'
tokens = (project / 'tokens.css').read_text()
components = (project / 'components.css').read_text()
if components.startswith('@import'):
    components = components.split('\n', 1)[1]
css = tokens + '\n' + components + '\n' + (source / 'styles.css').read_text() + '\n' + (source / 'folder-surfaces.css').read_text()
ui = (source / 'ui.html').read_text()
js = (source / 'model.js').read_text() + '\n' + (source / 'controller.js').read_text()
fragment = '<style>\n' + css + '\n</style>\n' + ui + '<script>\n(()=>{\n' + js + '\n})();\n</script>\n'
head = '''<!doctype html>
<html lang="en">
<head>
 <meta charset="utf-8">
 <meta name="viewport" content="width=device-width,initial-scale=1">
 <title>File Companion</title>
 <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=JetBrains+Mono:wght@500&display=swap">
 <style>body{margin:0;padding:32px;background:var(--surface-0,#F5F7FB);color:var(--ink,#18233A);font-family:Manrope,"SF Pro Text",system-ui,sans-serif}@media(max-width:600px){body{padding:10px}}</style>
</head>
<body>
'''
(project / 'index.html').write_text(head + fragment + '</body>\n</html>\n')
review = '''<div class="review-toolbar">
 <label for="review-state">Review a screen</label>
 <select id="review-state">
  <option value="0:first-run">Folder access · first run</option>
  <option value="1:first-run">Profile · nothing selected</option>
  <option value="2:first-run">Work areas · Student</option>
  <option value="3:first-run">Categories · awaiting approval</option>
  <option value="4:first-run">Local scan · paused</option>
  <option value="5:first-run">Archive briefing</option>
  <option value="0:access-denied">Folder access · denied</option>
  <option value="2:blank">Work areas · Start blank</option>
  <option value="3:blank">Categories · none proposed</option>
  <option value="3:all-refused">Categories · all refused</option>
  <option value="5:all-refused">Briefing · all refused</option>
  <option value="5:no-folders">Briefing · no folders chosen</option>
 </select>
 <span>Review controls are outside the product.</span>
</div>
<style>.review-toolbar{display:flex;align-items:center;gap:var(--space-3,12px);flex-wrap:wrap;max-width:1180px;margin:0 auto var(--space-4,16px);color:var(--ink-muted,#566176);font:600 13px/18px Manrope,"SF Pro Text",system-ui,sans-serif}.review-toolbar select{font:inherit;border:1px solid var(--line,#E1E6EE);border-radius:var(--radius-sm,8px);padding:9px;background:var(--surface-1,#FFFFFF);color:var(--ink,#18233A)}.review-toolbar span{font-weight:500;font-size:12px}</style>
'''
review_js = '''<script>
document.getElementById('review-state').addEventListener('change',event=>{
 const [screen,scenario]=event.target.value.split(':');
 document.getElementById('file-companion-onboarding').previewScreen(Number(screen),scenario);
});
</script>
'''
(project / 'Review.html').write_text(head + review + fragment + review_js + '</body>\n</html>\n')
print('Built index.html and Review.html.')
