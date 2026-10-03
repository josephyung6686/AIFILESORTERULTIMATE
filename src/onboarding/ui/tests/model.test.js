const test=require('node:test');
const assert=require('node:assert/strict');
const SetupModel=require('../source/model.js');

test('first run has no implicit choices and scanning is gated',()=>{
 const m=new SetupModel();
 assert.equal(m.profile,null);assert.deepEqual(m.folders,[]);assert.deepEqual(m.categories,[]);
 assert.equal(m.answers().finished,false);
 assert.throws(()=>m.startScan(),/Finish onboarding/);
});
test('folder selection requires explicit access',()=>{
 const m=new SetupModel();m.setFolders(['Documents']);
 assert.throws(()=>m.finishAnswers(),/Allow folder access/);
 m.denyAccess();assert.throws(()=>m.finishAnswers(),/denied/);
 m.grantAccess();m.finishAnswers();m.startScan();assert.equal(m.scanStatus,'running');
 m.setFolders(['Downloads']);assert.equal(m.answersReady,false);
 assert.throws(()=>m.startScan(),/Finish onboarding/);
});
test('pending and refused categories cannot enter scan answers',()=>{
 const m=new SetupModel();m.skipAccess();m.setProfile('student');m.setAreas(['Courses','Projects','Recruiting']);m.propose();
 assert(m.categories.every(c=>c.status==='pending'));assert.deepEqual(m.answers().categories,[]);
 m.confirm(m.categories[0].id);m.refuse(m.categories[1].id);
 const answers=m.finishAnswers();assert.deepEqual(answers.categories,[{id:m.categories[0].id,name:'Courses'}]);
 assert.equal(answers.refusedCategories[0].name,'Projects');
 m.startScan();assert.equal(m.scanStatus,'running');
});
test('a new category name must be confirmed again',()=>{
 const m=new SetupModel(),c=m.addCategory('Research');m.confirm(c.id);
 m.edit(c.id,'Research');assert.equal(c.status,'confirmed');
 m.edit(c.id,'Lab research');assert.equal(c.status,'pending');assert.deepEqual(m.answers().categories,[]);
 m.refuse(c.id);m.restore(c.id);assert.equal(c.status,'pending');
 assert.equal(m.edit(c.id,' '),false);assert.equal(c.name,'Lab research');
});
test('all refused and blank setups can finish without classification',()=>{
 const m=new SetupModel();m.skipAccess();m.setProfile('student');m.setAreas(['Courses']);m.propose();m.refuse(m.categories[0].id);
 m.finishAnswers();m.startScan();assert.deepEqual(m.answers().categories,[]);
 m.setProfile('blank');m.propose();assert.deepEqual(m.categories,[]);assert.deepEqual(m.areas,[]);
 m.finishAnswers();m.startScan();assert.equal(m.scanStatus,'running');
});
test('exclusions are separate and file handling stays read-only',()=>{
 const m=new SetupModel();m.setLeaveAlone('Taxes, Identity\nMedical');
 assert.deepEqual(m.answers().leaveAlone,['Taxes','Identity','Medical']);assert.deepEqual(m.categories,[]);
 assert.equal(m.answers().unmatched,'unplaced');assert.equal(m.answers().sensitiveMaterial,'held');assert.equal(m.answers().fileOperations,'read-only');
});
test('pause stops progress, completion follows three phases',()=>{
 const m=new SetupModel();m.skipAccess();m.finishAnswers();m.startScan();
 assert.equal(m.advanceScan(),false);assert.equal(m.scanPhase,1);m.pauseScan();
 assert.equal(m.advanceScan(),false);assert.equal(m.scanPhase,1);m.resumeScan();
 assert.equal(m.advanceScan(),false);assert.equal(m.advanceScan(),true);assert.equal(m.scanStatus,'complete');
 m.setDetail('courses','Thermodynamics');assert.equal(m.answersReady,false);assert.equal(m.scanStatus,'idle');
});
test('an unfinished snapshot or missing folder access cannot start a scan',()=>{
 const unfinished=new SetupModel();
 unfinished.setFolders(['Documents']);unfinished.grantAccess();
 assert.equal(unfinished.answers().finished,false);
 assert.throws(()=>unfinished.startScan(),/Finish onboarding/);
 const missing=new SetupModel();
 missing.setFolders(['Documents']);
 assert.equal(missing.answers().folderAccess.state,'not-requested');
 assert.throws(()=>missing.finishAnswers(),/Allow folder access/);
 assert.throws(()=>missing.startScan(),/Finish onboarding/);
 missing.denyAccess();
 assert.throws(()=>missing.finishAnswers(),/denied/);
 assert.throws(()=>missing.startScan(),/Finish onboarding/);
});
