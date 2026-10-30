'use strict';
const assert=require('assert'),fs=require('fs'),vm=require('vm');
const html=fs.readFileSync(__dirname+'/../examples/cafe_DEMO.html','utf8');
const script=html.slice(html.lastIndexOf('<script>')+8,html.lastIndexOf('</script>'));
const json=html.match(/<script id="rea-payload" type="application\/json">([\s\S]*?)<\/script>/)[1];
class Element {
  constructor(tag='div') {this.tagName=tag;this.textContent='';this.value='';this.disabled=false;this.children=[];this.events={};this.className='';this.dataset={};this.files=[];this.hidden=false;}
  append(...xs){this.children.push(...xs)}
  replaceChildren(...xs){this.children=[...xs]}
  add(x){this.children.push(x)}
  addEventListener(name,fn){this.events[name]=fn}
  click(){if(this.events.click)return this.events.click()}
  async trigger(name,ev){return this.events[name](ev)}
}
const map={};
for(const id of ['rea-payload','app-title','csv-file','export','status','total','category-count','matched','list-count','item-list','details','search','category','sort','prev','next','page-info'])map[id]=new Element();
map['rea-payload'].textContent=json;
const document={body:new Element('body'),documentElement:new Element('html'),getElementById:id=>map[id],createElement:tag=>new Element(tag)};
let requestCount=0;
const context={document,Option:class Option extends Element{constructor(t,v){super('option');this.textContent=t;this.value=v}},
 TextDecoder,Blob,URL:{createObjectURL:()=>{requestCount++;return 'blob:fake'},revokeObjectURL:()=>{}},setTimeout:()=>{},console};
vm.runInNewContext(script,context,{timeout:3000});
assert.equal(map.total.textContent,'4');
assert.equal(map['item-list'].children.length,4);
map.search.value='A002';map.search.trigger('input');assert.equal(map.matched.textContent,'1');
map.search.value='';map.search.trigger('input');
const same=map.total.textContent;
const mk=(name,s)=>{const buf=Buffer.from(s,'utf8');return {name,size:buf.length,arrayBuffer:async()=>buf.buffer.slice(buf.byteOffset,buf.byteOffset+buf.byteLength)}};
(async()=>{
  await map['csv-file'].trigger('change',{target:{files:[mk('bad.csv','id,title,category,price,description\nX1,abc,c,1,z\nX1,def,c,2,z')],value:'a'}});
  assert.equal(map.total.textContent,same);assert(map.status.textContent.startsWith('갱신 실패'));
  await map['csv-file'].trigger('change',{target:{files:[mk('good.csv','description,price,category,id,title\nhello,1500,테스트,Z001,새상품\n')],value:'a'}});
  assert.equal(map.total.textContent,'1');assert.equal(map.matched.textContent,'1');
  assert(map.status.textContent.includes('HTML로 저장'));
  console.log('LITE_VM_UI 7/7 PASS (synthetic DOM harness, NOT a real browser)');
})().catch(e=>{console.error(e);process.exitCode=1});
