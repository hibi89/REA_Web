"use strict";
// Deterministic CSV parser and inert JSON checks from the restored Lite HTML.
const fs=require("node:fs"),assert=require("node:assert/strict");
const html=fs.readFileSync(__dirname+"/../rea/lite_assets/template.html","utf8");
const js=html.split("<script>")[1].split("</script>")[0];
const section=js.slice(js.indexOf(" function csvRows"),js.indexOf(" function categories"));
assert(section.includes("function parseCsv"),"missing CSV parser");
const schema=["id","title","category","price","description"];
const mapping={id:"id",title:"title",category:"category"};
const canonical=[...schema];
const {parseCsv}=Function("schema","mapping","canonical","MAX_ROWS","MAX_COLS",
    "const norm=v=>v.trim();"+section+" return {parseCsv};")(
      schema,mapping,canonical,10000,20);
let n=0;
const good=(s,f)=>{f(parseCsv(s));n++};
const bad=s=>{assert.throws(()=>parseCsv(s));n++};
good("id,title,category,price,description\nX1,\"상품,하나\",커피,100,\"첫\n줄\"\n",v=>assert.equal(v[0].title,"상품,하나"));
good("\ufeffid,title,category,price,description\r\nX1,하나,커피,100,설명\r\n",v=>assert.equal(v[0].id,"X1"));
good("description,category,price,title,id\n설명,도구,500,드릴,X5",v=>assert.equal(v[0].title,"드릴"));
good("id,title,category,price,description\n X1 , 하나 , 분류 , 900 , 값 \n",v=>assert.equal(v[0].description,"값"));
bad("id,title,category,price,description\nX1,a,z,1,b\nX1,b,z,2,b");
bad('id,title,category,price,description\nX1,"unclosed,z,1,b');
bad("id,title,category,price,description\nX1,a,z,1");
bad("id,title,category,price,description\nX1,a,z,1,b,extra");
bad("id,title,title,price,description\nX1,a,z,1,b");
bad("id,title,category,price,description\nX1,,z,1,b");
bad("id,title,category,price,description\nX1,a,,1,b");
bad("id,title,category,price,description\nX1,a,z,1,b\nX2,a,z,2,\0");
bad('id,title,category,price,description\nX1,a,z,1,b\nX2,a,z,2,"c"illegal');
bad("id,title,category,price,description\n");
const safePart=js.slice(js.indexOf(" function safeJson"),js.indexOf(" function saveHtml"));
const {safeJson}=Function(safePart+" return {safeJson};")();
const threat="</script><img src=x onerror=alert(1)>&";
const escaped=safeJson({threat});
assert(!escaped.includes("</script>"));
assert.equal(JSON.parse(escaped).threat,threat);n++;
console.log("REA Lite CSV & escaping: "+n+"/"+n+" PASS");
