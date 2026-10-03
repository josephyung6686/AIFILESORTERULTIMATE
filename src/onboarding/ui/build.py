from pathlib import Path
import base64

project = Path(__file__).resolve().parent
source = project / 'source'
tokens = (project / 'tokens.css').read_text().replace(':root {', '#file-companion-onboarding {')
css = tokens + '\n' + (source / 'styles.css').read_text() + '\n' + (source / 'folder-surfaces.css').read_text()
ui = (source / 'ui.html').read_text()
js = (source / 'model.js').read_text() + '\n' + (source / 'controller.js').read_text()
fragment = '<style>\n' + css + '\n</style>\n' + ui + '<script>\n(()=>{\n' + js + '\n})();\n</script>\n'
asset = 'data:image/webp;base64,' + base64.b64encode((project / 'assets/glass-companion.webp').read_bytes()).decode()
fragment = fragment.replace('assets/glass-companion.webp', asset)
head = '''<!doctype html>
<html lang="en">
<head>
 <meta charset="utf-8">
 <meta name="viewport" content="width=device-width,initial-scale=1">
 <title>File companion | Onboarding</title>
 <style>body{margin:0;padding:32px;background:#EEF1F6;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}@media(max-width:600px){body{padding:10px}}</style>
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
<style>.review-toolbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;max-width:1220px;margin:0 auto 18px;color:#364C84;font-size:13px}.review-toolbar select{font:inherit;border:1px solid #DCDDE1;border-radius:8px;padding:9px;background:#FFFFFF;color:#364C84}.review-toolbar span{font-size:12px;color:#657080}@media(max-width:600px){.review-toolbar select{width:100%}}</style>
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
