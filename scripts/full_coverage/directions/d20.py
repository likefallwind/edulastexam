"""Trusted RC simulator compiler: bounded arithmetic AST, never model JS execution."""
import ast,bisect,json,math,re
from pathlib import Path

ALLOWED_NAMES={'v','V','R','C','dt'}

def parse(text):
    try:return json.loads(text)
    except (ValueError,TypeError):pass
    for m in re.finditer(r'```(?:json)?\s*([\s\S]*?)```',text):
        try:return json.loads(m.group(1))
        except ValueError:pass
    raise ValueError('Expected JSON simulator configuration.')

def expression(source):
    tree=ast.parse(source,mode='eval')
    assert len(list(ast.walk(tree)))<=60,'Expression too large.'
    def check(n):
        if isinstance(n,ast.Expression):return check(n.body)
        if isinstance(n,ast.Constant):
            assert isinstance(n.value,(int,float)) and not isinstance(n.value,bool) and math.isfinite(n.value) and abs(n.value)<=1e6,'Numeric constant outside contract.'
        elif isinstance(n,ast.Name):assert n.id in ALLOWED_NAMES,'Unknown variable.'
        elif isinstance(n,ast.UnaryOp):assert isinstance(n.op,(ast.UAdd,ast.USub));check(n.operand)
        elif isinstance(n,ast.BinOp):
            assert isinstance(n.op,(ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow)),'Unknown operator.';check(n.left);check(n.right)
            if isinstance(n.op,ast.Pow):assert isinstance(n.right,ast.Constant) and abs(n.right.value)<=8,'Powers need a numeric exponent of magnitude <=8.'
        elif isinstance(n,ast.Call):
            assert isinstance(n.func,ast.Name) and n.func.id=='exp' and len(n.args)==1 and not n.keywords,'Only exp(x) is supported.';check(n.args[0])
        else:raise ValueError('Only bounded arithmetic is allowed.')
    check(tree)
    return tree.body

def calculate(n,values):
    if isinstance(n,ast.Constant):x=float(n.value)
    elif isinstance(n,ast.Name):x=values[n.id]
    elif isinstance(n,ast.UnaryOp):x=calculate(n.operand,values)*(1 if isinstance(n.op,ast.UAdd) else -1)
    elif isinstance(n,ast.Call):
        x=calculate(n.args[0],values);assert abs(x)<=700,'exp argument too large.';x=math.exp(x)
    else:
        a,b=calculate(n.left,values),calculate(n.right,values)
        if isinstance(n.op,ast.Add):x=a+b
        elif isinstance(n.op,ast.Sub):x=a-b
        elif isinstance(n.op,ast.Mult):x=a*b
        elif isinstance(n.op,ast.Div):x=a/b
        else:x=a**b
    assert isinstance(x,(float,int)) and math.isfinite(x) and abs(x)<1e12,'Invalid simulation value.'
    return float(x)

def javascript(n):
    if isinstance(n,ast.Constant):return str(float(n.value))
    if isinstance(n,ast.Name):return n.id
    if isinstance(n,ast.UnaryOp):return '('+('+' if isinstance(n.op,ast.UAdd) else '-')+javascript(n.operand)+')'
    if isinstance(n,ast.Call):return 'Math.exp('+javascript(n.args[0])+')'
    op={ast.Add:'+',ast.Sub:'-',ast.Mult:'*',ast.Div:'/',ast.Pow:'**'}[type(n.op)]
    return '('+javascript(n.left)+op+javascript(n.right)+')'

class Simulator:
    def __init__(self,cfg):
        self.cfg=cfg;self.step=expression(cfg['step_expression']);self.current=expression(cfg['current_expression']);self.R=2000.;self.C=1e-4;self.mode='charge';self.t=0.;self.v=0.;self.history=[(0.,0.)]
        self.sample_dt=cfg['sample_dt'];assert isinstance(self.sample_dt,(int,float)) and not isinstance(self.sample_dt,bool) and .0001<=self.sample_dt<=1,'sample_dt must be within [0.0001,1] seconds.'
        assert isinstance(cfg['preserve_history_on_change'],bool) and isinstance(cfg['reset_restores_defaults'],bool),'History/reset options must be booleans.'
    def values(self,dt=0):return {'v':self.v,'V':10. if self.mode=='charge' else 0.,'R':self.R,'C':self.C,'dt':dt}
    def state(self):return {'time':self.t,'voltage':self.v,'current':calculate(self.current,self.values())}
    def change(self,mode=None,R=None):
        if mode is not None:self.mode=mode
        if R is not None:self.R=float(R)
        if not self.cfg['preserve_history_on_change']:self.history=[(self.t,self.v)]
    def advance(self,dt):
        target=self.t+dt;self.v=calculate(self.step,self.values(dt))
        start_t,start_v=self.history[-1]
        # Interpolate from the actual beginning of this advance using its current parameters.
        count=math.ceil(dt/self.sample_dt);assert count<=100000,'Too many render samples.'
        for j in range(1,count+1):
            elapsed=min(j*self.sample_dt,dt)
            values=self.values(elapsed);values['v']=start_v
            self.history.append((start_t+elapsed,calculate(self.step,values)))
        self.t=target
    def reset(self):
        if self.cfg['reset_restores_defaults']:self.R=2000.;self.mode='charge'
        self.t=0.;self.v=0.;self.history=[(0.,0.)]

def render_html(cfg,step,current):
    template='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>RC教学演示</title><style>body{font:18px system-ui;max-width:900px;margin:25px auto}label{margin:12px}svg{border:1px solid #ccc}button,input,select{font:inherit}pre{white-space:pre-wrap}</style><h1>RC电压与电流</h1><p>电源10V；C=100μF；初始R=2000Ω。切换充放电或电阻不使电容电压瞬变。</p><label>模式<select id="mode"><option value="charge">充电</option><option value="discharge">放电</option></select></label><label>R(Ω)<input id="resistance" type="number" min="1" value="2000"></label><label>推进秒数<input id="dt" type="number" min="0" max="10" step="0.1" value="0.1"></label><button id="advance">推进</button><button id="reset">重置</button><pre id="state"></pre><svg id="plot" width="850" height="360" viewBox="0 0 850 360"><text x="5" y="18">v / V</text><text x="765" y="350">t / s</text><path d="M40 25V320H820" fill="none" stroke="black"/><g id="ticks"></g><polyline id="curve" fill="none" stroke="#126ba3" stroke-width="2"/></svg><script>
const step=(v,V,R,C,dt)=>__STEP__; const current=(v,V,R,C,dt)=>__CURRENT__;
const sampleDt=__SAMPLE__,preserve=__PRESERVE__,restore=__RESTORE__;
let t=0,v=0,R=2000,mode='charge',history=[[0,0]];const C=1e-4;
function target(){return mode==='charge'?10:0;}function update(){const i=current(v,target(),R,C,0);document.querySelector('#state').textContent=JSON.stringify({time:t,voltage:v,current:i},null,2);const maxT=Math.max(2,t);const ticks=document.querySelector('#ticks');ticks.replaceChildren();for(let n=0;n<=5;n++){const ty=document.createElementNS('http://www.w3.org/2000/svg','text');ty.setAttribute('x','7');ty.setAttribute('y',String(325-58*n));ty.setAttribute('font-size','12');ty.textContent=String(2*n);ticks.appendChild(ty);const tx=document.createElementNS('http://www.w3.org/2000/svg','text');tx.setAttribute('x',String(35+156*n));tx.setAttribute('y','338');tx.setAttribute('font-size','12');tx.textContent=(maxT*n/5).toFixed(1);ticks.appendChild(tx);}document.querySelector('#curve').setAttribute('points',history.map(p=>`${40+780*p[0]/maxT},${320-29*p[1]}`).join(' '));document.querySelector('#plot').dataset.samples=String(history.length);}
function change(){mode=document.querySelector('#mode').value;const r=Number(document.querySelector('#resistance').value);if(Number.isFinite(r)&&r>0)R=r;if(!preserve)history=[[t,v]];update();}
function advance(dt){if(!Number.isFinite(dt)||dt<0||dt>10)return;const start=t,old=v,V=target(),n=Math.ceil(dt/sampleDt);if(n>100000)return;for(let j=1;j<=n;j++){const d=Math.min(j*sampleDt,dt);history.push([start+d,step(old,V,R,C,d)]);}v=step(old,V,R,C,dt);t+=dt;update();}
function reset(){t=0;v=0;history=[[0,0]];if(restore){R=2000;mode='charge';document.querySelector('#resistance').value=R;document.querySelector('#mode').value=mode;}update();}
document.querySelector('#mode').addEventListener('change',change);document.querySelector('#resistance').addEventListener('change',change);document.querySelector('#advance').addEventListener('click',()=>advance(Number(document.querySelector('#dt').value)));document.querySelector('#reset').addEventListener('click',reset);window.eduSimulator={advance,reset,change,state:()=>({time:t,voltage:v,current:current(v,target(),R,C,0),history:history.map(p=>p.slice())})};update();</script></html>'''
    return template.replace('__STEP__',javascript(step)).replace('__CURRENT__',javascript(current)).replace('__SAMPLE__',json.dumps(cfg['sample_dt'])).replace('__PRESERVE__',json.dumps(cfg['preserve_history_on_change'])).replace('__RESTORE__',json.dumps(cfg['reset_restores_defaults']))

def validate_artifact(response_text,output_dir,prompt_id):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);checks=[]
    try:
        cfg=parse(response_text);s=Simulator(cfg)
        def check(name,actual,expected,tol=1e-6):checks.append({'id':name,'passed':abs(actual-expected)<=tol,'observed':actual})
        check('reset.time',s.t,0);check('reset.voltage',s.v,0);check('reset.current',s.state()['current'],.005)
        s.advance(.3);check('charge.voltage',s.v,10*(1-math.exp(-1.5)))
        old=list(s.history);before=s.v;s.change('discharge',1000);check('switch.continuity',s.v,before)
        checks.append({'id':'switch.history_preserved','passed':s.history==old});check('discharge.sign',s.state()['current'],-before/1000)
        s.advance(.1);expected=before*math.exp(-1);check('discharge.voltage',s.v,expected)
        s.change(R=4000);s.advance(.2);expected*=math.exp(-.5);check('resistance_change.voltage',s.v,expected)
        s.change('charge');s.advance(.1);expected=10+(expected-10)*math.exp(-.25);check('charge_restart.voltage',s.v,expected)
        s.reset();check('reset_after_changes.current',s.state()['current'],.005);checks.append({'id':'reset.history','passed':s.history==[(0.,0.)]})
        one=Simulator(cfg);one.advance(2);two=Simulator(cfg);two.advance(1);two.advance(1);check('partition_invariance',one.v,two.v)
        xs=[p[0] for p in one.history]
        for t in [.005,.01,.025,.075,.125,.333,.5,1,1.5]:
            k=bisect.bisect_left(xs,t);a,b=one.history[max(0,k-1)],one.history[min(k,len(xs)-1)]
            val=a[1] if a[0]==b[0] else a[1]+(b[1]-a[1])*(t-a[0])/(b[0]-a[0])
            check(f'curve.{t:g}s',val,10*(1-math.exp(-t/.2)),.02)
        (out/'simulator.html').write_text(render_html(cfg,one.step,one.current));(out/'simulation.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n');(out/'history.json').write_text(json.dumps(one.history)+'\n')
        return {'passed':all(c['passed'] for c in checks),'checks':checks,'artifacts':['simulator.html','simulation.json','history.json'],'public_feedback':{'checks':[{'id':c['id'],'passed':c['passed']} for c in checks],'note':'检查基于任务公开的RC关系、连续性、历史保留、重置及0.02V曲线误差要求。'},'scope':'bounded_declarative_simulator; not arbitrary code-agent benchmark'}
    except (ValueError,KeyError,TypeError,AssertionError,ZeroDivisionError,OverflowError,SyntaxError) as exc:
        return {'passed':False,'checks':checks+[{'id':'schema_or_execution','passed':False,'detail':str(exc)}],'public_feedback':str(exc)}
