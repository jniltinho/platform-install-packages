"""Read-only browser checks for route motion; uses the E2E login environment."""
import json
import os
from pathlib import Path
import subprocess
import uuid

base = os.environ['E2E_BASE_URL'].rstrip('/')
args = ['agent-browser', '--session', 'kconsole-motion-' + uuid.uuid4().hex[:8]]
if os.environ.get('E2E_CHROME_ARGS'):
    args += ['--args', os.environ['E2E_CHROME_ARGS']]


def ab(*command):
    result = subprocess.run(args + list(command), capture_output=True, text=True, timeout=65)
    if result.returncode:
        raise RuntimeError('agent-browser ' + command[0] + ' failed: ' + result.stderr[:1000])
    return result.stdout.strip()


def js(script):
    return json.loads(ab('eval', script))


try:
    ab('open', base + '/login')
    ab('wait', '--fn', '!!document.querySelector("input[type=password]")')
    ab('snapshot', '-i')
    ab('find', 'label', 'E-mail', 'fill', os.environ['E2E_EMAIL'])
    ab('find', 'label', 'Senha', 'fill', Path(os.environ['E2E_PASSWORD_FILE']).read_text().strip())
    ab('find', 'role', 'button', 'click', '--name', 'Entrar')
    ab('wait', '--url', '**/dashboard')
    ab('wait', '--fn', '!!document.querySelector(".stat strong")')
    result = js('''(async () => {
      const header = document.querySelector('header');
      const nav = document.querySelector('.tabs');
      const seen = [];
      const positions = [];
      const sample = setInterval(() => positions.push(document.querySelector('footer').getBoundingClientRect().top), 10);
      const observer = new MutationObserver(() => {
        for (const e of document.querySelectorAll('.page-enter-active,.page-leave-active')) {
          seen.push({classes:e.className, duration:getComputedStyle(e).transitionDuration});
        }
      });
      observer.observe(document.querySelector('.content'), {subtree:true,attributes:true,childList:true});
      document.querySelector('.tabs a[href="/media"]').click();
      await new Promise(r => setTimeout(r, 650));
      observer.disconnect(); clearInterval(sample);
      return {seen, footerShift:Math.max(...positions)-Math.min(...positions), path:location.pathname, count:document.querySelectorAll('.page-transition').length,
        stable:header===document.querySelector('header') && nav===document.querySelector('.tabs'),
        opacity:getComputedStyle(document.querySelector('.page-transition')).opacity};
    })()''')
    assert result['path'] == '/media' and result['count'] == 1 and result['stable'], result
    assert result['opacity'] == '1', result
    assert result['footerShift'] < 1, result
    assert any('page-enter-active' in e['classes'] for e in result['seen']), result
    assert any('page-leave-active' in e['classes'] for e in result['seen']), result
    assert all('0.15s' in e['duration'] for e in result['seen']), result
    # Rapid navigation must settle on the final route without stacked/hidden pages.
    result = js('''(async () => {
      for (const path of ['/dashboard','/system/health','/users']) {
        document.querySelector('.tabs a[href="'+path+'"]').click();
        await new Promise(r => setTimeout(r, 40));
      }
      await new Promise(r => setTimeout(r, 650));
      return {path:location.pathname,count:document.querySelectorAll('.page-transition').length,
        opacity:getComputedStyle(document.querySelector('.page-transition')).opacity};
    })()''')
    assert result == {'path': '/users', 'count': 1, 'opacity': '1'}, result
    ab('set', 'media', 'light', 'reduced-motion')
    result = js('''(() => {
      const probe = document.createElement('div');
      probe.className='page-transition page-enter-active page-enter-from';
      document.body.append(probe);
      const s=getComputedStyle(probe);
      const result={reduced:matchMedia('(prefers-reduced-motion: reduce)').matches,
        duration:s.transitionDuration,transform:s.transform,opacity:s.opacity};
      probe.remove();return result;
    })()''')
    assert result == {'reduced': True, 'duration': '0s', 'transform': 'none', 'opacity': '1'}, result
    ab('find', 'role', 'button', 'click', '--name', 'Sair')
    ab('wait', '--url', '**/login')
    print('PASS: route fade/150ms, stable navigation/card/footer, rapid navigation, reduced motion, logout')
finally:
    ab('close')
