import ts from 'typescript';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const root=process.argv[2];
const files=execFileSync('git',['-c','core.fsmonitor=false','-C',root,'ls-files','-co','--exclude-standard','--','*.ts','*.tsx','*.js','*.jsx'],{encoding:'utf8'}).trim().split('\n').filter(Boolean);
const icons=new Map(), unsupported=[];
function add(name,file,local,count){
 const value=icons.get(name)??{name,usage_count:0,import_count:0,files:[]};
 value.usage_count+=count; value.import_count++;
 value.files.push({file,local,usage_count:count});icons.set(name,value);
}
for(const file of [...new Set(files)].sort()){
 const full=path.join(root,file);if(!fs.existsSync(full))continue;
 const source=ts.createSourceFile(file,fs.readFileSync(full,'utf8'),ts.ScriptTarget.Latest,true,file.endsWith('x')?ts.ScriptKind.TSX:undefined);
 for(const statement of source.statements){
  if(!ts.isImportDeclaration(statement)||statement.moduleSpecifier.text!=='lucide-react')continue;
  const clause=statement.importClause;if(!clause||clause.isTypeOnly)continue;
  if(clause.namedBindings&&ts.isNamedImports(clause.namedBindings)){
   for(const el of clause.namedBindings.elements){
    if(el.isTypeOnly||['LucideIcon','LucideProps','IconNode'].includes((el.propertyName??el.name).text))continue;
    const local=el.name.text,name=(el.propertyName??el.name).text;let count=0;
    function walk(n){
     if(n===statement)return;
     if(ts.isIdentifier(n)&&n.text===local){
      if(!(ts.isPropertyAccessExpression(n.parent)&&n.parent.name===n)&&!(ts.isPropertyAssignment(n.parent)&&n.parent.name===n))count++;
     }
     ts.forEachChild(n,walk);
    }
    walk(source);add(name,file,local,count);
   }
  }else if(clause.namedBindings&&ts.isNamespaceImport(clause.namedBindings)){
   const local=clause.namedBindings.name.text;const counts=new Map();
   function walk(n){if(ts.isPropertyAccessExpression(n)&&ts.isIdentifier(n.expression)&&n.expression.text===local)counts.set(n.name.text,(counts.get(n.name.text)??0)+1);ts.forEachChild(n,walk);}
   walk(source);for(const [name,count] of counts)add(name,file,`${local}.${name}`,count);
   unsupported.push({file,kind:'namespace import; statically named members counted; computed members need manual review'});
  }else unsupported.push({file,kind:'default import needs manual review'});
 }
}
console.log(JSON.stringify({method:'TypeScript AST import bindings and identifier references (imports excluded; static occurrence counts, not runtime executions)',files_scanned:files.length,icons:[...icons.values()].sort((a,b)=>a.name.localeCompare(b.name)),manual_review:unsupported}));
