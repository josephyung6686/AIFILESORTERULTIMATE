const root=document.getElementById('file-companion-onboarding');
if(root){
 let model=new SetupModel();
 const $=s=>root.querySelector(s),$$=s=>[...root.querySelectorAll(s)];
 const steps=['Folder access','Your profile','Areas of work','Your categories','Local scan','Archive briefing'];
 const sides=[
  ['Your desktop companion','Right where you left them.','The folders you choose stay on your Mac. We only read them.'],
  ['A place to begin','A starting point. Yours to change.','Student suggests a few categories. Start blank leaves it up to you.'],
  ['Keep it personal','Just the work you choose.','Leave out anything you want to keep to yourself.'],
  ['You have the last word','Keep what fits. Leave the rest.','A suggestion becomes a category only when you confirm it.'],
  ['A quiet look around','Nothing gets moved.','Reading your chosen folders with your confirmed categories.'],
  ['One step closer','The same files. A clearer view.','Your workspace keeps the structure. Your originals stay put.'],
  ['Ready when you are','Everything starts with your choices.','Change your categories whenever your work changes.']
 ];
 const examples={Courses:['Homework_2.pdf','Lecture_notes.pdf'],Applications:['Resume.pdf','Cover_letter.docx'],Recruiting:['Interview_notes.md','Company_research.pdf'],Projects:['Research_notes.pdf','Project_brief.md']};
 let page=0,furthest=0,focusedCategory=null,scanTimer=null,modalConfirm=null,modalCancel=null,previousFocus=null,answersNote='',briefing=null,nativeSeq=0,nativeFlight=null;
 const nativePending={};
 function isMacApp(){return !!(window.webkit&&window.webkit.messageHandlers&&window.webkit.messageHandlers.companion);}
 function callNative(method,payload){
  return new Promise(resolve=>{
   const id=String(++nativeSeq);
   nativePending[id]=resolve;
   window.webkit.messageHandlers.companion.postMessage({id,method,payload});
  });
 }
 window.fileCompanionDone=function(id,body){const resolve=nativePending[String(id)];if(resolve){delete nativePending[String(id)];resolve(body||{});}};
 function say(text){$('#fc-announcement').textContent=text;}
 function el(tag,cls,text){const node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node;}
 function actionButton(text,action,id,cls='fc-text'){const b=el('button',cls+' cursor-interaction',text);b.type='button';b.dataset.action=action;if(id)b.dataset.category=id;return b;}
 function stopTimer(){if(scanTimer!==null){clearTimeout(scanTimer);scanTimer=null;}}
 function scheduleScan(){
  if(isMacApp()){
   if(model.scanStatus!=='running'||nativeFlight)return;
   nativeFlight=callNative('scan',root.setupSnapshot()).then(body=>{
    nativeFlight=null;
    if(model.scanStatus==='paused'){model._pausedBody=body;return;}
    finishNativeScan(body);
   });
   return;
  }
  stopTimer();if(model.scanStatus==='running')scanTimer=setTimeout(()=>{scanTimer=null;const done=model.advanceScan();renderScan();if(done){go(5);say('The preview scan is complete. Archive briefing.');}else scheduleScan();},1500);
 }
 function finishNativeScan(body){
  if(body&&body.ok&&body.briefing&&body.briefing.complete){briefing=body.briefing;model.scanStatus='complete';model.scanPhase=3;}
  else{briefing=null;model.scanStatus='stopped';answersNote=(body&&body.error)||'The scan did not finish. Counts stay empty.';}
  const error=$('#fc-scan-error');
  if(error){error.hidden=model.scanStatus!=='stopped';error.textContent=model.scanStatus==='stopped'?answersNote:'';}
  renderScan();
  if(model.scanStatus==='complete')go(5);
  else renderFooter();
 }
 async function loadWorkspace(){
  if(!isMacApp()){renderWorkspace(null);return;}
  const body=await callNative('workspace',root.setupSnapshot());
  renderWorkspace(body);
 }
 function syncFolders(){const values=$$('input[name=folder]:checked').map(x=>x.value);const other=$('#fc-other-check').checked;$('#fc-other-field').hidden=!other;if(other&&$('#fc-other-input').value.trim())values.push($('#fc-other-input').value.trim());model.setFolders(values);$('#fc-access-error').hidden=true;renderFooter();}
 function renderAreas(){
  const student=model.profile==='student';$('#fc-course-card').hidden=!student;
  $$('input[name=area]').forEach(x=>{x.checked=model.areas.includes(x.value);});
  $('[data-context=courses]').hidden=!model.areas.includes('Courses');
  $('[data-context=companies]').hidden=!model.areas.some(x=>['Applications','Recruiting'].includes(x));
  $('[data-context=projects]').hidden=!model.areas.includes('Projects');
  $('#fc-areas-note').hidden=model.areas.length>0;
 }
 function renderProfile(){
  $$('input[name=profile]').forEach(input=>input.checked=input.value===model.profile);
  $('#fc-person-line').hidden=model.profile!=='student';
  $('#fc-person-input').value=model.personName;$('#fc-school-input').value=model.school;
  $('#fc-profile-note').textContent=model.profile==='student'?'You will confirm or refuse the proposed categories next.':model.profile==='blank'?'Your items start unplaced until you confirm a category.':'No profile selected. Continue to start with a blank setup.';
 }
 function renderCategories(){
  const list=$('#fc-category-list');list.replaceChildren();
  if(!model.categories.some(c=>c.id===focusedCategory))focusedCategory=model.categories[0]?.id||null;
  model.categories.forEach(c=>{
   const row=el('article','fc-category-row'+(c.id===focusedCategory?' is-focused':''));row.dataset.category=c.id;
   const head=el('div','fc-category-head');
   const name=actionButton(c.name,'focus-category',c.id,'fc-category-name');name.setAttribute('aria-label','View examples for '+c.name);
   const badge=el('span','fc-status-badge '+c.status,c.status==='pending'?'Suggested':c.status==='confirmed'?'Confirmed':'Refused');
   head.append(name,badge);const controls=el('div','fc-category-actions');
   const confirm=actionButton(c.status==='confirmed'?'Confirmed':'Confirm','confirm',c.id,'fc-secondary');confirm.setAttribute('aria-pressed',String(c.status==='confirmed'));confirm.setAttribute('aria-label','Confirm '+c.name);
   const edit=actionButton('Edit','edit-category',c.id);edit.setAttribute('aria-label','Edit '+c.name);
   const refuse=actionButton('Refuse','refuse',c.id);refuse.setAttribute('aria-pressed',String(c.status==='refused'));refuse.setAttribute('aria-label','Refuse '+c.name);
   controls.append(confirm,edit,refuse);if(c.status==='refused')controls.append(actionButton('Restore','restore',c.id));
   row.append(head,controls);list.append(row);
  });
  $('#fc-category-empty').hidden=model.categories.length>0;
  const accepted=model.confirmed();
  $('#fc-category-note').textContent=accepted.length?'Only the confirmed categories will be used.':model.categories.length&&model.categories.every(c=>c.status==='refused')?'All categories refused. Readable items will start unplaced; sensitive material stays held.':'No categories confirmed. You can continue with items unplaced.';
  renderAside();
 }
 function focusAction(action,id){$('[data-action="'+action+'"][data-category="'+id+'"]')?.focus();}
 function openEditor(id){
  const row=$('.fc-category-row[data-category="'+id+'"]');if(row.querySelector('.fc-edit-form'))return;
  const form=el('div','fc-inline-form fc-edit-form');const label=el('label','fc-field','Category name');
  const input=el('input');input.type='text';input.value=model.category(id).name;input.maxLength=70;input.dataset.editor=id;label.append(input);
  form.append(label,actionButton('Save name','save-edit',id,'fc-secondary'),actionButton('Cancel','cancel-edit',id));row.append(form);input.focus();input.select();
 }
 function renderAside(){
  const [label,title,copy]=sides[page];$('#fc-aside-label').textContent=label;$('#fc-aside-title').textContent=title;$('#fc-aside-copy').textContent=copy;
  const c=page===3?model.categories.find(x=>x.id===focusedCategory):null;
  $('#fc-evidence').hidden=!c;
  if(c){$('#fc-aside-copy').textContent='Examples for '+c.name+', based on the area you chose.';const list=$('#fc-example-files');list.replaceChildren();(examples[c.origin]||['Sample_document.pdf']).forEach(name=>list.append(el('li','',name)));}
 }
 function renderScan(){
  const paused=model.scanStatus==='paused',complete=model.scanStatus==='complete',stopped=model.scanStatus==='stopped';
  const names=['Reading your folders','Checking confirmed categories','Keeping sensitive material held'];
  $('#fc-scan-status').textContent=complete?(isMacApp()?'Scan finished':'Preview scan complete'):stopped?'Scan did not finish':paused?'Scan paused':names[Math.min(model.scanPhase,2)];
  const progress=$('#fc-scan-progress');if(complete){progress.max=1;progress.value=1;}else progress.removeAttribute('value');
  progress.style.animationPlayState=paused?'paused':'running';progress.setAttribute('aria-label',paused?'Local scan paused':complete?'Preview scan complete':'Local scan in progress');
  $$('[data-phase]').forEach(li=>{const n=Number(li.dataset.phase);li.classList.toggle('is-active',!complete&&n===model.scanPhase);li.classList.toggle('is-done',complete||n<model.scanPhase);});
  renderFooter();
 }
 function countText(value,one,many){return value+' '+(value===1?one:many);}
 function renderBriefing(){
  const hasFolders=model.access==='granted'&&model.folders.length>0;
  const counts=briefing&&briefing.complete?briefing:null;
  if(counts&&typeof counts.found==='number'){
   $('#fc-found-copy').textContent=countText(counts.found,'file indexed.','files indexed.');
   $('#fc-found-state').textContent=String(counts.found);
   $('#fc-briefing-subline').textContent='Counts are from the scan of your folders.';
  }else{
   $('#fc-found-copy').textContent=hasFolders?'File names and totals will appear here.':'Choose a folder in Settings when you are ready.';
   $('#fc-found-state').textContent=hasFolders?'Awaiting results':'No folders chosen';
   $('#fc-briefing-subline').textContent=hasFolders?'Result fields stay empty until a real scan finishes.':'No folders chosen. You can add them later.';
  }
  if(counts&&typeof counts.unplaced==='number')$('#fc-unplaced-copy').textContent=countText(counts.unplaced,'file is unplaced.','files are unplaced.');
  else $('#fc-unplaced-copy').textContent=model.confirmed().length?'Files without a confirmed category stay here.':'Readable items start unplaced. Sensitive material stays held.';
  $('#fc-left-copy').textContent=model.leaveAlone.length?model.leaveAlone.join(', '):'No folders or topics excluded.';
  const tags=$('#fc-confirmed-tags');tags.replaceChildren();const confirmed=model.confirmed();if(!confirmed.length)tags.textContent='None confirmed';else confirmed.forEach(c=>tags.append(el('span','fc-confirmed-tag',c.name)));
  $('#fc-answers-note').textContent=answersNote;
 }
 function renderWorkspace(body){
  const outline=$('#fc-outline');
  const text=body&&body.outline&&String(body.outline).trim();
  outline.textContent=text||'No proposal yet.';
  const review=$('#fc-review-files');review.replaceChildren();
  const files=(body&&body.review)||[];
  files.forEach(file=>{
   const item=el('li');
   item.append(el('b',null,file.name||file.path||'File'));
   review.append(item);
  });
  $('#fc-review-empty').hidden=files.length>0;
  const empty=$('#fc-empty-folders');empty.replaceChildren();
  const folders=(body&&body.emptyFolders)||[];
  folders.forEach(folder=>{
   const item=el('li');
   item.append(el('b',null,folder.name||folder.path));
   const button=actionButton('Remove','remove-empty');
   button.dataset.path=folder.path;
   item.append(button);
   empty.append(item);
  });
  $('#fc-empty-none').hidden=folders.length>0;
 }
 function renderFooter(){
  $('#fc-back').disabled=page===0;
  const next=$('#fc-next');next.disabled=false;
  const labels=['Allow folder access','Continue','Review categories','Save choices & scan',model.scanStatus==='complete'||model.scanStatus==='stopped'?'View briefing':model.scanStatus==='paused'?'Resume scan':'Pause scan','Open workspace','Return to briefing'];
  next.textContent=labels[page];
  if(page===0){next.disabled=model.folders.length===0;next.textContent=model.access==='denied'?'Try folder access again':'Allow folder access';}
 }
 function renderNavigation(){
  $$('[data-step]').forEach(button=>{
   const n=Number(button.dataset.step);button.disabled=n>furthest||(n===4&&!model.answersReady)||(n===5&&model.scanStatus!=='complete'&&model.scanStatus!=='stopped');
   if(n===page)button.setAttribute('aria-current','step');else button.removeAttribute('aria-current');
   const mark=button.querySelector('.fc-step-mark');if(mark)mark.textContent=n<page?'✓':String(n+1);
  });
 }
 function go(n){
  if(n===4&&!model.answersReady)return;
  if(n===5&&model.scanStatus!=='complete'&&model.scanStatus!=='stopped')return;
  if(page===4&&n!==4)stopTimer();
  if(n<=3&&page>=4)model.invalidate();
  page=n;furthest=Math.max(furthest,Math.min(n,5));
  root.classList.toggle('is-folder-screen',n===0);
  $$('[data-page]').forEach(section=>section.hidden=Number(section.dataset.page)!==n);
  $('#fc-window-title').textContent=n===0?'File Companion':'File companion · '+(steps[n]||'Workspace handoff');
  if(n===1)renderProfile();if(n===2)renderAreas();if(n===3){model.propose();renderCategories();}if(n===4)renderScan();if(n===5)renderBriefing();if(n===6)loadWorkspace();
  renderAside();renderFooter();renderNavigation();say(steps[n]||'Workspace handoff');
  if(n===4&&model.scanStatus==='running')scheduleScan();
 }
 function closeModal(run=false){
  const fn=run?modalConfirm:modalCancel;$('#fc-modal').hidden=true;$('.fc-window').inert=false;modalConfirm=null;modalCancel=null;
  if(fn)fn();if(previousFocus?.isConnected)previousFocus.focus();
 }
 function openModal(title,copy,primary,secondary,onConfirm,onCancel){
  previousFocus=document.activeElement;$('#fc-dialog-title').textContent=title;$('#fc-dialog-copy').textContent=copy;
  $('#fc-dialog-primary').textContent=primary;$('#fc-dialog-secondary').textContent=secondary;
  modalConfirm=onConfirm;modalCancel=onCancel;$('#fc-modal').hidden=false;$('.fc-window').inert=true;$('#fc-dialog-primary').focus();
 }
 async function persistSnapshot(snapshot){
  if(isMacApp()){
   const body=await callNative('saveAnswers',snapshot);
   answersNote=body&&body.ok?'Answers saved on this Mac. Counts stay empty until a real scan finishes.':(body&&body.error)||'Answers were not saved.';
   return body;
  }
  if(location.protocol==='file:')return null;
  const timer=new AbortController();
  const kill=setTimeout(()=>timer.abort(),4000);
  try{
   const response=await fetch('answers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(snapshot),signal:timer.signal});
   const body=await response.json();
   answersNote=body&&body.ok?'Answers saved on this Mac. Counts stay empty until a real scan finishes.':'';
   return body;
  }catch(error){return null;}
  finally{clearTimeout(kill);}
 }
 async function next(){
  if(page===0){
   if(!model.folders.length)return;
   const allowCopy=isMacApp()
    ?'File Companion will read '+model.folders.join(', ')+'. Your files stay where they are. Nothing is moved or renamed.'
    :'In the Mac app, this asks permission to read '+model.folders.join(', ')+'.\n\nThis preview does not read your files.';
   openModal('Allow folder access?',allowCopy,isMacApp()?'Allow':'Allow in preview','Don’t allow',()=>{model.grantAccess();$('#fc-access-error').hidden=true;go(1);},()=>{model.denyAccess();$('#fc-access-error').hidden=false;renderFooter();say('Folder access denied.');});
  }else if(page===1){if(model.profile===null)model.setProfile('blank');go(2);
  }else if(page===2){model.propose();go(3);
  }else if(page===3){if(model.access==='denied'||(model.folders.length&&model.access!=='granted')){go(0);say('Allow access to your chosen folders before scanning.');return;}model.finishAnswers();const saved=await persistSnapshot(root.setupSnapshot());if(isMacApp()&&!(saved&&saved.ok)){say(answersNote||'The scan did not start.');return;}model.startScan();go(4);
  }else if(page===4){if(model.scanStatus==='complete'||model.scanStatus==='stopped'){go(5);}else if(model.scanStatus==='paused'){model.resumeScan();renderScan();if(model._pausedBody){const body=model._pausedBody;model._pausedBody=null;finishNativeScan(body);}else scheduleScan();}else{model.pauseScan();stopTimer();renderScan();}}
  else if(page===5)go(6);else go(5);
 }
 root.addEventListener('click',event=>{
  const button=event.target.closest('button');if(!button||!root.contains(button)||button.disabled)return;
  if(button.id==='fc-next'){next();return;}if(button.id==='fc-back'){go(Math.max(0,page-1));return;}
  if(button.id==='fc-dialog-primary'){closeModal(true);return;}if(button.id==='fc-dialog-secondary'){closeModal(false);return;}
  if(button.dataset.step!==undefined){go(Number(button.dataset.step));return;}
  const id=button.dataset.category;
  switch(button.dataset.action){
   case 'remove-empty':{
    const folderPath=button.dataset.path;
    if(!folderPath||!isMacApp())break;
    openModal('Remove this empty folder?','It has no files on disk. It is removed only if you say yes.','Yes','No',async()=>{
     const body=await callNative('removeEmpty',{path:folderPath,confirm:'yes',snapshot:root.setupSnapshot()});
     if(body&&body.error)say(body.error);
     loadWorkspace();
    },()=>{});
    break;
   }
   case 'skip-folders':model.skipAccess();go(1);break;
   case 'read-details':openModal('What exactly do we read?','Names, locations, file types and eligible file contents in the folders you choose.\n\nWe keep your structure as metadata in the app. Sensitive finance, identity, medical and legal material stays held and is never sent to a model.','Got it','Back',()=>{},()=>{});break;
   case 'settings-help':openModal('Allow folder access in System Settings','In the Mac app, this opens System Settings. Allow File companion to read your chosen folders, then return here and try again.','Got it','Back',()=>{},()=>{});break;
   case 'focus-category':focusedCategory=id;$$('.fc-category-row').forEach(row=>row.classList.toggle('is-focused',row.dataset.category===id));renderAside();break;
   case 'confirm':model.confirm(id);focusedCategory=id;renderCategories();focusAction('confirm',id);say(model.category(id).name+' confirmed.');break;
   case 'refuse':model.refuse(id);focusedCategory=id;renderCategories();focusAction('refuse',id);say(model.category(id).name+' refused.');break;
   case 'restore':model.restore(id);focusedCategory=id;renderCategories();focusAction('confirm',id);say(model.category(id).name+' restored as a suggestion.');break;
   case 'edit-category':openEditor(id);break;
   case 'save-edit':{const input=$('[data-editor="'+id+'"]');if(!input.value.trim()){input.setCustomValidity('Enter a category name.');input.reportValidity();return;}model.edit(id,input.value);renderCategories();focusAction('confirm',id);say('Category name saved. Confirm it to use it.');break;}
   case 'cancel-edit':$('.fc-category-row[data-category="'+id+'"] .fc-edit-form').remove();focusAction('edit-category',id);break;
   case 'add-category':$('#fc-add-form').hidden=false;$('#fc-add-input').focus();break;
   case 'cancel-add':$('#fc-add-form').hidden=true;break;
   case 'save-category':{const input=$('#fc-add-input');const c=model.addCategory(input.value);if(!c){input.setCustomValidity('Enter a category name.');input.reportValidity();return;}input.setCustomValidity('');input.value='';$('#fc-add-form').hidden=true;focusedCategory=c.id;renderCategories();focusAction('confirm',c.id);say('Category added as a suggestion.');break;}
  }
 });
 root.addEventListener('change',event=>{
  const input=event.target;
  if(input.name==='folder'||input.id==='fc-other-check')syncFolders();
  else if(input.name==='profile'){model.setProfile(input.value);renderProfile();renderAreas();}
  else if(input.name==='area'){model.setAreas($$('input[name=area]:checked').map(x=>x.value));renderAreas();}
  else if(input.id==='fc-leave-check'){const checked=input.checked;$('#fc-leave-field').hidden=!checked;model.setLeaveAlone(checked?$('#fc-leave-input').value:'');}
 });
 root.addEventListener('input',event=>{
  const input=event.target;
  if(input.id==='fc-other-input')syncFolders();
  else if(input.id==='fc-leave-input')model.setLeaveAlone(input.value);
  else if(input.id==='fc-person-input')model.setPerson(input.value);
  else if(input.id==='fc-school-input')model.setSchool(input.value);
  else for(const key of ['courses','companies','projects'])if(input.id==='fc-'+key+'-input')model.setDetail(key,input.value);
  if(input.setCustomValidity)input.setCustomValidity('');
 });
 root.addEventListener('keydown',event=>{
  if(!$('#fc-modal').hidden){
   if(event.key==='Escape'){event.preventDefault();closeModal(false);}
   if(event.key==='Tab'){const first=$('#fc-dialog-secondary'),last=$('#fc-dialog-primary');if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}}
  }
 });
 $$('button,label').forEach(node=>node.classList.add('cursor-interaction'));
 // Readable design handoff; no engine or operating-system calls.
 root.setupSnapshot=()=>model.answers();
 root.previewScreen=(screen,scenario='first-run')=>{
  stopTimer();model=new SetupModel();page=0;focusedCategory=null;answersNote='';briefing=null;nativeFlight=null;
  $$('input[type=checkbox],input[type=radio]').forEach(input=>input.checked=false);
  $$('input[type=text]').forEach(input=>input.value='');
  $('#fc-access-error').hidden=true;$('#fc-other-field').hidden=true;$('#fc-leave-field').hidden=true;
  if(screen>=2||scenario==='all-refused'){
   model.setFolders(['Documents','Downloads']);model.grantAccess();model.setProfile('student');model.setAreas(['Courses','Applications','Recruiting','Projects']);model.propose();
   focusedCategory=model.categories[0]?.id;
   if(scenario==='all-refused')model.categories.forEach(c=>model.refuse(c.id));
  }
  if(scenario==='access-denied'){model.setFolders(['Documents']);model.denyAccess();$('input[value=Documents]').checked=true;$('#fc-access-error').hidden=false;screen=0;}
  if(scenario==='blank'){model.setProfile('blank');model.setAreas([]);model.propose();}
  if(screen>=4&&scenario!=='no-folders'){if(scenario!=='all-refused'&&model.categories.length)model.confirm(model.categories[0].id);model.finishAnswers();model.startScan();if(screen>=5){while(model.scanStatus==='running')model.advanceScan();}else model.pauseScan();}
  if(scenario==='no-folders'){model.skipAccess();model.finishAnswers();model.startScan();while(model.scanStatus==='running')model.advanceScan();screen=5;}
  furthest=Math.min(screen,5);go(screen);
 };
 if(isMacApp())root.classList.add('is-mac-app');
 go(0);
}
