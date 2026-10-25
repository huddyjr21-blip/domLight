#!/usr/bin/python3
"""Sign and prepare a static Fedora repository. Run on the private Fedora signing VM."""
import argparse,datetime,hashlib,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--key',required=True);p.add_argument('rpms',nargs='+',type=Path);a=p.parse_args()
if not re.fullmatch(r'[A-Fa-f0-9]{40,64}',a.key):p.error('Use the full public signing-key fingerprint')
def run(args):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True)
 if r.returncode:raise RuntimeError(str(args)+': '+r.stdout+r.stderr)
 return r.stdout
root=a.root.resolve();repo=root/'fedora/44/noarch';packages=repo/'Packages';packages.mkdir(parents=True,exist_ok=True)
keyfile=root/'RPM-GPG-KEY-cloud-flex'
keyfile.write_text(run(['gpg','--armor','--export',a.key]))
if 'BEGIN PGP PUBLIC KEY BLOCK' not in keyfile.read_text():raise RuntimeError('Public key not exported')
records=[]
with tempfile.TemporaryDirectory(prefix='cloud-flex-sign-',dir=root.parent) as tmp:
 tmp=Path(tmp);tmp.chmod(0o755);db=Path(run(['sudo','mktemp','-d','/var/lib/domlight-verify-XXXXXX']).strip());run(['sudo','chcon','--reference=/usr/lib/sysimage/rpm',db])
 run(['sudo','rpmdb','--dbpath',db,'--initdb']);run(['sudo','rpmkeys','--dbpath',db,'--import',keyfile])
 for source in a.rpms:
  fields=run(['rpm','-qp','--qf','%{NAME}\n%{ARCH}\n%{VERSION}-%{RELEASE}\n',source]).splitlines()
  name,arch,version=fields
  if name not in ['cloud-flex-desktop','cloud-flex-release'] or arch!='noarch':raise RuntimeError('Unexpected package: '+str(fields))
  target=tmp/source.name;shutil.copy2(source,target)
  run(['rpmsign','--define','_openpgp_sign gpg','--define','_openpgp_sign_id '+a.key,'--addsign',target])
  check=run(['sudo','rpmkeys','--dbpath',db,'--checksig',target])
  if 'signatures OK' not in check:raise RuntimeError(check)
  final=packages/(name+'-'+version+'.noarch.rpm')
  # Never replace an already published NEVRA with different bytes.
  if final.exists():
   existing=run(['sudo','rpmkeys','--dbpath',db,'--checksig',final])
   if 'signatures OK' not in existing:raise RuntimeError(existing)
   # Compare RPM payload digests rather than nondeterministic signature timestamps.
   fmt='%{SHA256HEADER}\n%{PAYLOADDIGEST}\n'
   if run(['rpm','-qp','--qf',fmt,final])!=run(['rpm','-qp','--qf',fmt,target]):raise RuntimeError('Bump version/release before replacing '+final.name)
  else:shutil.copy2(target,final)
  records.append({'file':str(final.relative_to(root)),'version':version,'signature':check.strip().split(': ',1)[-1]})
 run(['sudo','rm','-rf','--',db])
 run(['createrepo_c','--update','--retain-old-md','5',repo])
 metadata=repo/'repodata/repomd.xml';signature=metadata.with_suffix('.xml.asc')
 run(['gpg','--batch','--yes','--armor','--local-user',a.key,'--detach-sign','--output',signature,metadata])
 run(['gpg','--verify',signature,metadata])
report={'published_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fingerprint':a.key.upper(),'packages':records}
(root/'release.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
