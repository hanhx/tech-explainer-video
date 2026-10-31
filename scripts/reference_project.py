"""Clone and calibrate the approved reference project; never render inside the Skill.

clone DEST copies pinned source and any locally available narration.
A Git checkout excludes audio/video; visual calibration still works without them.
check DEST --python PY compares fresh rendered keyframes with pinned goldens.
This is environment/baseline reproducibility, not a new-topic quality score.
"""
from pathlib import Path
import argparse,json,hashlib,shutil,subprocess,sys
SKILL=Path(__file__).resolve().parents[1]
CASE=SKILL/'assets/examples/wifi-protocols-v6'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_inputs(folder, manifest):
 missing_audio=[]
 for name,sha in manifest.items():
  path=folder/name
  if not path.is_file() and Path(name).parts[0]=='audio':
   missing_audio.append(name);continue
  if not path.is_file() or digest(path)!=sha:
   raise ValueError(f'Reference input missing or changed: {name}')
 return missing_audio

def clone(dest):
 source=CASE/'project';manifest=json.loads((source/'project-manifest.json').read_text())
 if dest.exists():raise ValueError('Destination already exists; choose a new project directory')
 missing_audio=validate_inputs(source,manifest)
 shutil.copytree(source,dest);(dest/'.local').mkdir()
 return dict(project=str(dest),copied_inputs=len(manifest)-len(missing_audio),missing_local_audio=missing_audio,visual_calibration_available=True,narrated_render_available=not missing_audio,scope='Approved-film reproduction only; redesign story and objects for a new topic')

def check(dest,python):
 pinned=json.loads((CASE/'goldens/manifest.json').read_text());manifest=json.loads((CASE/'project/project-manifest.json').read_text())
 missing_audio=validate_inputs(dest,manifest)
 out=dest/'checks/reference-calibration';out.mkdir(parents=True,exist_ok=True)
 program='''import sys,json\nfrom pathlib import Path\np=Path(sys.argv[1]);sys.path.insert(0,str(p));import scene\nsamples=json.loads(sys.argv[3])\nfor s in samples:\n i=next(i for i,v in enumerate(scene.SHOTS) if v['id']==s['cue']);scene.frame(i,s['phase'],1920,1080).save(Path(sys.argv[2])/s['file'])\n'''
 subprocess.run([python,'-I','-c',program,str(dest),str(out),json.dumps(pinned['samples'])],check=True)
 rows=[dict(cue=s['cue'],file=s['file'],matches=digest(out/s['file'])==s['sha256']) for s in pinned['samples']]
 report=dict(passed=all(s['matches'] for s in rows),samples=rows,missing_local_audio=missing_audio,narrated_render_available=not missing_audio,scope='Exact same-environment reference reproduction; not new-topic comprehension or subjective quality')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['clone','check']);p.add_argument('project',type=Path);p.add_argument('--python',default=sys.executable);a=p.parse_args()
 try:
  result=clone(a.project.resolve()) if a.action=='clone' else check(a.project.resolve(),a.python)
  print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result.get('passed',True) else 1)
 except (OSError,ValueError,subprocess.SubprocessError) as e:p.exit(1,str(e)+'\n')
if __name__=='__main__':main()
