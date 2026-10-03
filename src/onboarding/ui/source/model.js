class SetupModel {
 constructor(){
  this.folders=[];this.access='not-requested';this.profile=null;this.areas=[];
  this.details={courses:'',companies:'',projects:''};this.leaveAlone=[];
  this.personName='';this.school='';
  this.categories=[];this.answersReady=false;
  this.scanStatus='idle';this.scanPhase=0;this.nextId=1;
 }
 invalidate(){this.answersReady=false;this.scanStatus='idle';}
 setFolders(values){this.folders=[...new Set(values.filter(Boolean))];this.access='not-requested';this.invalidate();}
 grantAccess(){this.access=this.folders.length?'granted':'none';this.invalidate();}
 denyAccess(){this.access='denied';this.invalidate();}
 skipAccess(){this.access='none';this.folders=[];this.invalidate();}
 setProfile(value){if(![null,'student','blank'].includes(value))throw Error('Unsupported profile');this.profile=value;if(value!=='student')this.areas=this.areas.filter(x=>x!=='Courses');this.invalidate();}
 setAreas(values){const allowed=this.profile==='student'?['Courses','Applications','Recruiting','Projects']:['Applications','Recruiting','Projects'];this.areas=[...new Set(values.filter(x=>allowed.includes(x)))];this.invalidate();}
 setDetail(key,value){if(!(key in this.details))throw Error('Unknown detail');this.details[key]=String(value);this.invalidate();}
 setLeaveAlone(value){this.leaveAlone=String(value).split(/\n|,/).map(x=>x.trim()).filter(Boolean);this.invalidate();}
 setPerson(value){this.personName=String(value);this.invalidate();}
 setSchool(value){this.school=String(value);this.invalidate();}
 propose(){
  const previous=new Map(this.categories.filter(x=>x.origin!=='custom').map(x=>[x.origin,x]));
  this.categories=[...this.areas.map(name=>previous.get(name)||{id:'c'+this.nextId++,origin:name,name,status:'pending'}),...this.categories.filter(x=>x.origin==='custom')];
  this.invalidate();
 }
 addCategory(name){name=String(name).trim();if(!name)return null;const c={id:'c'+this.nextId++,origin:'custom',name,status:'pending'};this.categories.push(c);this.invalidate();return c;}
 category(id){const c=this.categories.find(x=>x.id===id);if(!c)throw Error('Unknown category');return c;}
 confirm(id){this.category(id).status='confirmed';this.invalidate();}
 refuse(id){this.category(id).status='refused';this.invalidate();}
 restore(id){this.category(id).status='pending';this.invalidate();}
 edit(id,name){name=String(name).trim();if(!name)return false;const c=this.category(id);if(c.name!==name){c.name=name;c.status='pending';this.invalidate();}return true;}
 confirmed(){return this.categories.filter(x=>x.status==='confirmed');}
 finishAnswers(){
  if(this.access==='denied')throw Error('Folder access was denied');
  if(this.folders.length&&this.access!=='granted')throw Error('Allow folder access before scanning');
  this.answersReady=true;
  return this.answers();
 }
 answers(){return {
  schemaVersion:1,finished:this.answersReady,profile:this.profile||'blank',
  folderAccess:{state:this.access,folders:[...this.folders]},
  categories:this.confirmed().map(({id,name})=>({id,name})),
  refusedCategories:this.categories.filter(x=>x.status==='refused').map(({id,name})=>({id,name})),
  context:{...this.details},leaveAlone:[...this.leaveAlone],
  personName:this.personName,school:this.school,
  unmatched:'unplaced',sensitiveMaterial:'held',fileOperations:'read-only'
 };}
 startScan(){if(!this.answersReady)throw Error('Finish onboarding before scanning');if(this.access==='denied')throw Error('Folder access was denied');this.scanStatus='running';this.scanPhase=0;}
 pauseScan(){if(this.scanStatus==='running')this.scanStatus='paused';}
 resumeScan(){if(this.scanStatus==='paused')this.scanStatus='running';}
 advanceScan(){if(this.scanStatus!=='running')return false;this.scanPhase++;if(this.scanPhase>=3){this.scanStatus='complete';return true;}return false;}
}
if(typeof module!=='undefined'&&module.exports)module.exports=SetupModel;
