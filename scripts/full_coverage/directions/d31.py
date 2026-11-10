"""Interpret a small Python AST safely: no exec/eval, imports, attributes or I/O."""
from __future__ import annotations
import ast,itertools,math,re
from pathlib import Path

class Unsupported(Exception):pass
class Returned(Exception):
    def __init__(self,value):self.value=value
class ContinueLoop(Exception):pass
class BreakLoop(Exception):pass

class Interpreter:
    def __init__(self,source):
        self.tree=ast.parse(source)
        if len(self.tree.body)!=1 or not isinstance(self.tree.body[0],ast.FunctionDef):raise Unsupported('Submit exactly one function, without imports or top-level execution.')
        self.fn=self.tree.body[0]
        if self.fn.name!='positive_mean' or self.fn.decorator_list or self.fn.args.defaults or self.fn.args.kw_defaults or self.fn.args.vararg or self.fn.args.kwarg or self.fn.args.kwonlyargs or self.fn.args.posonlyargs or len(self.fn.args.args)!=1:raise Unsupported('Function signature must be positive_mean(values), without decorators/defaults.')
        bad=(ast.Import,ast.ImportFrom,ast.Attribute,ast.While,ast.Lambda,ast.ClassDef,ast.With,ast.Try,ast.Global,ast.Nonlocal,ast.Delete,ast.Await,ast.Yield,ast.YieldFrom,ast.AsyncFunctionDef,ast.NamedExpr)
        for node in ast.walk(self.tree):
            if isinstance(node,bad):raise Unsupported('Unsupported syntax: '+type(node).__name__)
            if isinstance(node,ast.Name) and node.id.startswith('__'):raise Unsupported('Private/builtin namespace access is unavailable.')
            if isinstance(node,ast.FunctionDef) and node is not self.fn:raise Unsupported('Nested functions unavailable.')
        self.steps=0
    def tick(self):
        self.steps+=1
        if self.steps>10000:raise Unsupported('AST step budget exceeded.')
    def bounded(self,x):
        if isinstance(x,(int,float)) and not isinstance(x,bool) and (not math.isfinite(x) or abs(x)>10**12):raise Unsupported('Numeric budget exceeded.')
        if isinstance(x,(list,tuple,range,str)) and len(x)>1000:raise Unsupported('Collection budget exceeded.')
        return x
    def expr(self,n,env):
        self.tick()
        if isinstance(n,ast.Constant):
            if not isinstance(n.value,(int,float,bool,str,type(None))):raise Unsupported('Unsupported constant')
            return self.bounded(n.value)
        if isinstance(n,ast.Name):
            if n.id not in env:raise Unsupported('Unknown variable: '+n.id)
            return env[n.id]
        if isinstance(n,(ast.List,ast.Tuple)):
            values=[self.expr(x,env) for x in n.elts];return values if isinstance(n,ast.List) else tuple(values)
        if isinstance(n,ast.BinOp):
            a,b=self.expr(n.left,env),self.expr(n.right,env)
            ops={ast.Add:lambda:a+b,ast.Sub:lambda:a-b,ast.Mult:lambda:a*b,ast.Div:lambda:a/b,ast.FloorDiv:lambda:a//b,ast.Mod:lambda:a%b}
            if type(n.op) not in ops:raise Unsupported('Unsupported operator')
            if isinstance(n.op,ast.Mult) and (isinstance(a,(str,list,tuple)) or isinstance(b,(str,list,tuple))):raise Unsupported('Sequence multiplication unavailable.')
            return self.bounded(ops[type(n.op)]())
        if isinstance(n,ast.UnaryOp):
            a=self.expr(n.operand,env)
            if isinstance(n.op,ast.USub):return self.bounded(-a)
            if isinstance(n.op,ast.UAdd):return self.bounded(+a)
            if isinstance(n.op,ast.Not):return not a
            raise Unsupported('Unsupported unary op')
        if isinstance(n,ast.Compare):
            a=self.expr(n.left,env)
            for op,node in zip(n.ops,n.comparators):
                b=self.expr(node,env);ops={ast.Lt:lambda:a<b,ast.LtE:lambda:a<=b,ast.Gt:lambda:a>b,ast.GtE:lambda:a>=b,ast.Eq:lambda:a==b,ast.NotEq:lambda:a!=b,ast.Is:lambda:a is b,ast.IsNot:lambda:a is not b}
                if type(op) not in ops:raise Unsupported('Unsupported comparison')
                if not ops[type(op)]():return False
                a=b
            return True
        if isinstance(n,ast.BoolOp):
            v=self.expr(n.values[0],env)
            for node in n.values[1:]:
                if isinstance(n.op,ast.And) and not v:return v
                if isinstance(n.op,ast.Or) and v:return v
                v=self.expr(node,env)
            return v
        if isinstance(n,ast.IfExp):return self.expr(n.body if self.expr(n.test,env) else n.orelse,env)
        if isinstance(n,ast.Subscript):
            target=self.expr(n.value,env);index=self.expr(n.slice,env)
            if not isinstance(target,(list,tuple,range,str)):raise Unsupported('Only sequence indexing supported.')
            return target[index]
        if isinstance(n,ast.Call):
            funcs={'len':len,'sum':sum,'range':range,'min':min,'max':max,'abs':abs}
            if not isinstance(n.func,ast.Name) or n.func.id not in funcs or n.keywords:raise Unsupported('Only documented pure builtin calls are supported.')
            args=[self.expr(a,env) for a in n.args]
            return self.bounded(funcs[n.func.id](*args))
        if isinstance(n,(ast.ListComp,ast.GeneratorExp)):
            if len(n.generators)!=1:raise Unsupported('Only a single bounded comprehension generator is supported.')
            g=n.generators[0]
            if g.is_async or not isinstance(g.target,ast.Name):raise Unsupported('Invalid comprehension')
            seq=self.expr(g.iter,env);self.bounded(seq)
            if not isinstance(seq,(list,tuple,range)):raise Unsupported('Only bounded sequence iteration supported.')
            ans=[]
            for val in seq:
                self.tick();scope=dict(env);scope[g.target.id]=val
                if all(self.expr(c,scope) for c in g.ifs):ans.append(self.expr(n.elt,scope))
            return ans
        raise Unsupported('Unsupported expression: '+type(n).__name__)
    def assign(self,target,value,env):
        if not isinstance(target,ast.Name) or target.id.startswith('__'):raise Unsupported('Assignments require ordinary local names.')
        env[target.id]=self.bounded(value)
    def block(self,nodes,env):
        for n in nodes:
            self.tick()
            if isinstance(n,ast.Assign):
                v=self.expr(n.value,env)
                for t in n.targets:self.assign(t,v,env)
            elif isinstance(n,ast.AugAssign):
                self.assign(n.target,self.expr(ast.BinOp(left=n.target,op=n.op,right=n.value),env),env)
            elif isinstance(n,ast.Return):raise Returned(self.expr(n.value,env) if n.value else None)
            elif isinstance(n,ast.If):self.block(n.body if self.expr(n.test,env) else n.orelse,env)
            elif isinstance(n,ast.For):
                seq=self.expr(n.iter,env);self.bounded(seq)
                if not isinstance(seq,(list,tuple,range)):raise Unsupported('Only bounded sequence iteration supported.')
                broken=False
                for v in seq:
                    self.tick();self.assign(n.target,v,env)
                    try:self.block(n.body,env)
                    except ContinueLoop:continue
                    except BreakLoop:broken=True;break
                if not broken:self.block(n.orelse,env)
            elif isinstance(n,ast.Continue):raise ContinueLoop()
            elif isinstance(n,ast.Break):raise BreakLoop()
            elif isinstance(n,ast.Pass):pass
            elif isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):pass
            else:raise Unsupported('Unsupported statement: '+type(n).__name__)
    def run(self,values):
        self.steps=0
        try:self.block(self.fn.body,{self.fn.args.args[0].arg:list(values)})
        except Returned as e:return e.value
        return None

def validate_artifact(response_text,output_dir,prompt_id):
    blocks=re.findall(r'```(?:python|py)\s*([\s\S]*?)```',response_text)
    candidates=[b for b in blocks if re.search(r'def\s+positive_mean\s*\(',b)]
    source=candidates[-1] if candidates else response_text.strip()
    checks=[]
    try:
        evaluator=Interpreter(source)
        samples=[[],[-100,0,100],[1,3],[0,4],[-3,2,8],[100]*20]
        samples.extend(list(t) for n in range(1,5) for t in itertools.product([-2,0,1,3],repeat=n))
        failures=[]
        for values in samples:
            kept=[v for v in values if v>0];expected=sum(kept)/len(kept) if kept else None
            try:
                actual=evaluator.run(values)
                ok=actual is None if expected is None else isinstance(actual,(int,float)) and not isinstance(actual,bool) and math.isfinite(actual) and abs(actual-expected)<1e-9
                if not ok:failures.append({'input':values,'observed':actual,'kind':'wrong_result'})
            except (Unsupported,IndexError,ZeroDivisionError,TypeError,ValueError,OverflowError) as e:failures.append({'input':values,'kind':type(e).__name__,'detail':str(e)})
        passed=not failures;checks=[{'name':'bounded_function_contract','passed':passed,'test_count':len(samples),'failed_count':len(failures)}]
        out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);(out/'positive_mean.py').write_text(source)
        return {'passed':passed,'checks':checks,'public_feedback':'受限解释器合同测试通过。' if passed else '合同测试未通过；示例失败：'+str(failures[:3]),'artifacts':['positive_mean.py'],'semantic_review_required':True,'execution_mode':'restricted_ast_interpretation_no_exec','diagnosis_scored_separately':True}
    except (Unsupported,SyntaxError,ValueError,TypeError,OverflowError) as e:
        return {'passed':False,'checks':checks,'public_feedback':str(e),'semantic_review_required':True,'execution_mode':'restricted_ast_interpretation_no_exec'}
