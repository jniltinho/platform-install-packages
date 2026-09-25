"""Destructive only to the uniquely named media/user created by this test."""
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

base = os.environ['E2E_BASE_URL'].rstrip('/')
email = os.environ['E2E_EMAIL']
password = Path(os.environ['E2E_PASSWORD_FILE']).read_text().strip()
video = str(Path(os.environ['E2E_VIDEO']).resolve())
shots = Path(os.environ.get('E2E_SCREENSHOTS', '../doc/prints/kaltura-console-go')).resolve()
shots.mkdir(parents=True, exist_ok=True)
session = 'kconsole-e2e-' + uuid.uuid4().hex[:8]
args = ['agent-browser', '--session', session]
if os.environ.get('E2E_CHROME_ARGS'):
    args += ['--args', os.environ['E2E_CHROME_ARGS']]
created_path = None
created_user = None


def ab(*command):
    # Never print command arguments: fill commands can contain a test password.
    result = subprocess.run(args + list(command), capture_output=True, text=True, timeout=65)
    if result.returncode:
        raise RuntimeError('agent-browser ' + command[0] + ' failed: ' + result.stderr[:1000])
    return result.stdout.strip()


def evaluate(js):
    return json.loads(ab('eval', js))


def screenshot(name):
    ab('screenshot', str(shots / name))
    bad = evaluate('JSON.stringify([...document.querySelectorAll("*")].filter(e=>getComputedStyle(e).borderRadius!=="0px").map(e=>e.tagName))')
    assert json.loads(bad) == [], 'Nonzero border radius: ' + bad


def wait_js(js, seconds=30):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if evaluate(js):
            return
        time.sleep(1)
    raise AssertionError('Timed out waiting for page state')


def open_page(path):
    ab('open', base + path)
    wait_js('document.querySelector(".page-transition")?.children.length>0 && !document.querySelector(".page-enter-active,.page-leave-active")')


def browser_api(path, method='GET', body=None):
    return evaluate('''(async()=>{
      const s=await (await fetch('/api/session')).json();
      const r=await fetch('/api'+%s,{method:%s,headers:{'Content-Type':'application/json','X-CSRF-Token':s.csrf},body:%s});
      const data=r.status===204?null:await r.json();return {status:r.status,data};
    })()''' % (json.dumps(path), json.dumps(method), 'undefined' if body is None else json.dumps(json.dumps(body))))

try:
    ab('set', 'viewport', '1280', '900')
    open_page('/login')
    wait_js('document.querySelector("input[type=password]")!==null')
    ab('snapshot', '-i')
    screenshot('01-login.png')
    ab('find', 'label', 'E-mail', 'fill', email)
    ab('find', 'label', 'Senha', 'fill', password)
    ab('find', 'role', 'button', 'click', '--name', 'Entrar')
    ab('wait', '--url', '**/dashboard')
    wait_js('document.querySelectorAll(".stat strong").length===4')
    screenshot('02-dashboard.png')
    open_page('/media')
    wait_js('document.querySelector("table")!==null')
    screenshot('03-library.png')
    open_page('/media/upload')
    ab('snapshot', '-i')
    title = 'Console E2E ' + uuid.uuid4().hex[:10]
    ab('find', 'label', 'Nome', 'fill', title)
    ab('find', 'label', 'Descrição', 'fill', 'Disposable console E2E media')
    ab('upload', 'input[type=file]', video)
    screenshot('04-upload.png')
    # Capture the sending phases independently of browser command latency.
    evaluate('window.__phases=[];window.__phaseObserver=new MutationObserver(()=>{const s=document.querySelector("[aria-live]");if(s&&!window.__phases.includes(s.innerText))window.__phases.push(s.innerText)});window.__phaseObserver.observe(document.body,{childList:true,subtree:true,characterData:true});true')
    ab('find', 'role', 'button', 'click', '--name', 'Enviar')
    ab('wait', '--url', '**/media/0_*')
    created_path = evaluate('location.pathname')
    wait_js('document.querySelector("h1")?.textContent===' + json.dumps(title))
    phases = evaluate('window.__phases')
    assert any('Enviando ao console' in p for p in phases), phases
    assert any('Enviando ao Kaltura' in p for p in phases), phases
    screenshot('05-processing.png')
    wait_js('document.querySelector("video")!==null', seconds=1200)
    playback = evaluate('(async()=>{const v=document.querySelector("video");v.muted=true;await v.play();return {paused:v.paused}})()')
    assert playback['paused'] is False
    seek = evaluate('(async()=>{const r=await fetch(document.querySelector("video").getAttribute("src"),{headers:{Range:"bytes=0-1023"}});return {status:r.status,range:r.headers.get("Content-Range"),bytes:(await r.arrayBuffer()).byteLength}})()')
    assert seek['status'] == 206 and seek['bytes'] == 1024, seek
    screenshot('06-ready-player.png')
    ab('find', 'label', 'Nome', 'fill', title + ' edited')
    ab('find', 'role', 'button', 'click', '--name', 'Salvar')
    wait_js('document.querySelector("h1")?.textContent===' + json.dumps(title + ' edited'))
    screenshot('07-edited.png')
    ab('find', 'role', 'button', 'click', '--name', 'Excluir')
    ab('dialog', 'accept')
    ab('wait', '--url', '**/media')
    assert browser_api(created_path)['status'] == 404
    created_path = None
    open_page('/users')
    ab('snapshot', '-i')
    created_user = 'e2e-' + uuid.uuid4().hex[:8] + '@example.test'
    ab('find', 'label', 'Nome', 'fill', 'E2E viewer')
    ab('find', 'label', 'E-mail', 'fill', created_user)
    ab('find', 'label', 'Senha', 'fill', uuid.uuid4().hex)
    ab('find', 'role', 'button', 'click', '--name', 'Adicionar usuário')
    wait_js('document.querySelector("tbody")?.innerText.includes(' + json.dumps(created_user) + ')')
    # Use only the row matching the generated user, never an existing account.
    evaluate('document.querySelectorAll("tbody tr").forEach(r=>{if(r.innerText.includes(' + json.dumps(created_user) + '))r.id="e2e-user"});true')
    ab('select', '#e2e-user select', 'admin')
    wait_js('document.querySelector("#e2e-user select")?.value==="admin"')
    screenshot('08-users.png')
    # Server-level assertions complement UI state, which updates optimistically.
    account = next(u for u in browser_api('/users')['data'] if u['email'] == created_user)
    assert account['role'] == 'admin'
    ab('click', '#e2e-user button:not(.danger)')
    ab('snapshot', '-i')
    ab('fill', '.section input[type=password]', uuid.uuid4().hex)
    ab('click', '.section button[type=submit], .section button:not([type])')
    wait_js('document.querySelector(".section input[type=password]")===null')
    ab('click', '#e2e-user button.danger')
    ab('dialog', 'accept')
    wait_js('!document.querySelector("tbody")?.innerText.includes(' + json.dumps(created_user) + ')')
    created_user = None
    open_page('/system/health')
    wait_js('document.querySelectorAll("tbody tr").length>=7')
    checks = browser_api('/health')['data']
    assert all(c['ok'] for c in checks), checks
    screenshot('09-health.png')
    ab('select', '[aria-label=Language]', 'en')
    wait_js('document.querySelector("h1")?.textContent==="System health"')
    screenshot('10-english.png')
    ab('select', '[aria-label=Language]', 'pt-BR')
    ab('set', 'viewport', '360', '800')
    for route in ['/dashboard','/media','/media/upload','/users','/system/health']:
        open_page(route)
        wait_js('document.querySelector("h1")!==null')
        assert evaluate('document.documentElement.scrollWidth<=window.innerWidth'), route
        screenshot('mobile-' + route.replace('/', '-') + '.png')
    ab('find', 'role', 'button', 'click', '--name', 'Sair')
    ab('wait', '--url', '**/login')
    assert evaluate('(async()=>{const r=await fetch("/api/session");return r.status})()') == 401
    print('PASS: login, upload phases, READY polling, playback/206, edit/delete, users, health, i18n, radius, mobile, logout')
finally:
    if created_path:
        browser_api(created_path, 'DELETE')
    if created_user:
        for u in browser_api('/users').get('data', []):
            if u['email'] == created_user:
                browser_api('/users/' + str(u['id']), 'DELETE')
    ab('close')
