"""Generate reproducible synthetic media fixtures; never uses real learner data."""
from pathlib import Path
import subprocess,json,hashlib,wave,struct,math
from PIL import Image, ImageDraw, ImageFont

def main():
    B=Path(__file__).resolve().parents[3]/'private/edu_last_exam_full_coverage_v1';p=B/'stimuli/37';ref=B/'reference/37';ref.mkdir(parents=True,exist_ok=True)
    
    p.mkdir(parents=True,exist_ok=True)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i',"flite=text='The blue cup is on the desk.':voice=slt",'-af','apad=whole_dur=6','-t','6','-ar','16000','-ac','1',str(p/'speech.wav')],check=True)
    with wave.open(str(p/'speech.wav'),'rb') as w:params=w.getparams()
    with wave.open(str(p/'silence.wav'),'wb') as w:
     w.setparams(params);w.writeframes(bytes(params.nframes*params.nchannels*params.sampwidth))
    
    for i,amount in enumerate([20,40,60]):
     y=390-amount*4
     ticks=''.join(f'<line x1="267" y1="{390-a*4}" x2="292" y2="{390-a*4}" stroke="#203D39" stroke-width="2"/><text x="310" y="{397-a*4}" font-size="20">{a}</text>' for a in [0,20,40,60,80])
     svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 640 480"><rect width="640" height="480" fill="#F3F6EF"/><g font-family="DejaVu Sans" fill="#203D39"><text x="42" y="45" font-size="25">SYNTHETIC OBSERVATION · mL</text><rect x="170" y="60" width="120" height="330" rx="4" fill="white" stroke="#203D39" stroke-width="3"/><rect x="173" y="{y}" width="114" height="{390-y}" fill="#64AFA3"/>{ticks}<text x="375" y="170" font-size="40">{amount} mL</text><text x="375" y="220" font-size="24">{i*2}–{i*2+2} s</text><text x="42" y="450" font-size="18">Illustration only · not a real learner experiment</text></g></svg>'''
     (p/f'frame_{i}.svg').write_text(svg)
     im=Image.new('RGB',(640,480),'#F3F6EF');draw=ImageDraw.Draw(im)
     font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
     draw.text((42,18),'SYNTHETIC OBSERVATION · mL',font=font(25),fill='#203D39')
     draw.rectangle((170,60,290,390),fill='white',outline='#203D39',width=3)
     draw.rectangle((173,y,287,389),fill='#64AFA3')
     for a in [0,20,40,60,80]:
      yy=390-a*4;draw.line((267,yy,292,yy),fill='#203D39',width=2);draw.text((310,yy-11),str(a),font=font(20),fill='#203D39')
     draw.text((375,130),str(amount)+' mL',font=font(40),fill='#203D39');draw.text((375,200),str(i*2)+'–'+str(i*2+2)+' s',font=font(24),fill='#203D39')
     draw.text((42,430),'Illustration only · not a real learner experiment',font=font(18),fill='#203D39')
     im.save(p/f'frame_{i}.png')
    concat=''.join(f"file '{(p/f'frame_{i}.png').as_posix()}'\nduration 2\n" for i in range(3))+f"file '{(p/'frame_2.png').as_posix()}'\n"
    (p/'frames.txt').write_text(concat)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(p/'frames.txt'),'-vf','fps=10,tpad=stop_mode=clone:stop_duration=1','-t','6','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(p/'cylinder.mp4')]
    subprocess.run(cmd,check=True)
    manifest={'origin':'locally_generated_synthetic_fixtures','real_student_data':False,'license':'project-authored synthetic materials; flite synthesized speech, no third-party recording','audio_text':'The blue cup is on the desk.','audio_generation':'ffmpeg lavfi flite voice=slt; padded to 6 s; mono PCM16 16000 Hz','video_generation':'three project-authored vector diagrams rasterized by trusted Pillow drawing; ffmpeg concat 10 fps H.264, 6 s','observations':[{'interval_s':[0,2],'volume_ml':20},{'interval_s':[2,4],'volume_ml':40},{'interval_s':[4,6],'volume_ml':60}],'files':{}}
    for f in ['speech.wav','silence.wav','cylinder.mp4']:
     data=(p/f).read_bytes();entry={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
     if f.endswith('.wav'):
      with wave.open(str(p/f),'rb') as w:raw=w.readframes(w.getnframes());entry.update(duration_s=w.getnframes()/w.getframerate(),sample_rate=w.getframerate(),channels=w.getnchannels())
      vals=struct.unpack('<'+'h'*(len(raw)//2),raw);entry['rms']=math.sqrt(sum(v*v for v in vals)/len(vals))
     else:
      info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,width,height,nb_frames','-of','json',str(p/f)]));entry['probe']=info
     manifest['files'][f]=entry
    assert manifest['files']['silence.wav']['rms']==0
    assert manifest['files']['speech.wav']['rms']>10
    (ref/'media_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(manifest['files'],ensure_ascii=False))

if __name__ == "__main__":
    main()
