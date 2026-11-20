#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
"""Genera data/schema.json dai sorgenti di SEB / Builds data/schema.json from the SEB sources.

Uso / Usage:
    python3 tools/extract_schema.py --seb-win PATH/seb-win-refactoring --seb-mac PATH/seb-mac

Legge il configuratore Windows (SebWindowsConfig) per chiavi, valori predefiniti, etichette e suggerimenti,
e SEB per macOS per sapere quali chiavi esistono anche lì.
"""
import argparse, json, re, os

ap = argparse.ArgumentParser()
ap.add_argument('--seb-win', required=True)
ap.add_argument('--seb-mac', required=True)
ap.add_argument('--out', default=os.path.join(os.path.dirname(__file__), '..', 'data', 'schema.json'))
a = ap.parse_args()

W = os.path.join(a.seb_win, 'SebWindowsConfig') + '/'
rd = lambda p: open(p, encoding='utf8', errors='ignore').read()
cfg = rd(W + 'SEBSettings.cs')
form = rd(W + 'SebWindowsConfigForm.cs')
des = rd(W + 'SebWindowsConfigForm.Designer.cs')
mac = rd(os.path.join(a.seb_mac, 'Classes/ConfigFiles/SEBSettings.m'))
macK = set(re.findall(r'@"([A-Za-z][A-Za-z0-9]+)"', mac))
const = dict(re.findall(r'public const String (Key\w+)\s*=\s*"([A-Za-z0-9]+)"', cfg))

# --- valori predefiniti per gruppo / defaults by group
region = cfg[cfg.index('Default settings for group "General"') - 200:]
group = None
items, order = {}, []
for line in region.splitlines():
    m = re.search(r'Default settings for group "?([^"\n]+)"?', line)
    if m:
        group = m.group(1).strip()
    m = re.search(r'settingsDefault\.Add\(SEBSettings\.(Key\w+),\s*(.*)\);\s*(//.*)?$', line)
    if not m:
        continue
    k, v = m.group(1), m.group(2).strip()
    if k not in const or const[k] in items:
        continue
    if v in ('true', 'false'): t, d = 'bool', v == 'true'
    elif re.fullmatch(r'-?\d+', v): t, d = 'int', int(v)
    elif re.fullmatch(r'-?\d*\.\d+', v): t, d = 'float', float(v)
    elif re.fullmatch(r'"(.*)"', v): t, d = 'string', v[1:-1]
    elif v.startswith('new ListObj'): t, d = 'list', []
    elif v.startswith('new DictObj'): t, d = 'dict', {}
    else: t, d = 'string', None
    items[const[k]] = dict(key=const[k], group=group, type=t, default=d, common=const[k] in macK)
    order.append(const[k])

# --- controlli, etichette, suggerimenti / controls, labels, tooltips
ctrl = {}
for m in re.finditer(r'(\w+)\.(Checked|Text|SelectedIndex|Value)\s*=[^;]*?SEBSettings\.(Key\w+)\]', form):
    c, _, k = m.groups()
    if k in const and const[k] not in ctrl:
        ctrl[const[k]] = c
tips = {m.group(1): m.group(2).replace("\\'", "'").replace('\\n', ' ')
        for m in re.finditer(r'SetToolTip\(this\.(\w+), "((?:[^"\\]|\\.)*)"\)', des)}

def dtext(c):
    m = re.search(r'this\.%s\.Text\s*=\s*"((?:[^"\\]|\\.)*)"' % c, des)
    return m.group(1) if m else None

for k, it in items.items():
    c = ctrl.get(k)
    it['tip'] = tips.get(c) if c else None
    it['label'] = dtext(c) if c and c.startswith(('checkBox', 'radio')) else None

# --- curatela / curation
HIDE = {'originatorVersion', 'sebMode', 'sebConfigPurpose', 'examKeySalt', 'browserURLSalt', 'additionalResources',
        'embeddedCertificates', 'proxies', 'permittedProcesses', 'prohibitedProcesses', 'URLFilterRules',
        'startResource', 'browserUserAgentWinTouchModeIPad', 'browserExamKey'}
WIN_GROUPS = {'Special Keys', 'Function Keys', 'Inside SEB', 'Hooked Keys'}
WIN_KEYS = {'createNewDesktop', 'killExplorerShell', 'enableChromeNotifications', 'enableWindowsUpdate', 'allowStickyKeys',
            'lockScreenBackgroundColor', 'enableCursorVerification', 'enableSessionVerification',
            'disableSessionChangeLockScreen', 'sebServicePolicy', 'sebServiceIgnore', 'enableFindPrinter',
            'setVmwareConfiguration', 'detectStoppedProcess', 'allowFlashFullscreen', 'enableSebBrowser',
            'touchOptimized', 'enableTouchExit', 'browserScreenKeyboard', 'oskBehavior', 'taskBarHeight',
            'allowUserSwitching', 'lockOnMessageSocketClose', 'displayAlwaysOn', 'systemAlwaysOn', 'enablePlugIns', 'enableJava'}
MAC_KEYS = {'minMacOSVersion', 'allowSiri', 'allowDictation', 'forceAppFolderInstall', 'allowUserAppFolderInstall',
            'allowDisplayMirroring', 'allowedDisplaysMaxNumber', 'allowedDisplayBuiltin', 'allowedDisplayBuiltinEnforce',
            'allowedDisplaysIgnoreFailure', 'allowDictionaryLookup', 'enableAppSwitcherCheck', 'showMenuBar'}

F = [[i, 'F%d' % (i + 1)] for i in range(12)]
POS = [[0, 'Left'], [1, 'Center'], [2, 'Right']]
SHOWURL = [[0, 'Never'], [1, 'Only on load error'], [2, 'Before title'], [3, 'Always']]
POLICY = [[0, 'Generally block'], [1, 'Open in same window'], [2, 'Open in new window']]
ENUMS = {
    'exitKey1': F, 'exitKey2': F, 'exitKey3': F,
    'browserViewMode': [[0, 'Use browser window'], [1, 'Use full screen mode']],
    'mainBrowserWindowPositioning': POS, 'newBrowserWindowByLinkPositioning': POS,
    'zoomMode': [[0, 'Use page zoom'], [1, 'Use text zoom']],
    'oskBehavior': [[0, 'Always show'], [1, 'Never show'], [2, 'Auto show']],
    'newBrowserWindowByLinkPolicy': POLICY, 'newBrowserWindowByScriptPolicy': POLICY,
    'newBrowserWindowShowURL': SHOWURL, 'browserWindowShowURL': SHOWURL,
    'chooseFileToUploadPolicy': [[0, 'Manually with file requester'], [1, 'Attempt to upload same file as downloaded before'], [2, 'Only allow to upload same file as downloaded before']],
    'sebServicePolicy': [[0, 'Allow to run SEB without service'], [1, 'Display warning when service is not running'], [2, 'Allow to run SEB only with service']],
    'proxySettingsPolicy': [[0, 'Use system proxy settings'], [1, 'Use SEB proxy settings']],
    'clipboardPolicy': [[0, 'Allow'], [1, 'Block'], [2, 'SEB only']],
    'browserUserAgentWinDesktopMode': [[0, 'Default'], [1, 'Custom']],
    'browserUserAgentWinTouchMode': [[0, 'Default'], [1, 'iPad'], [2, 'Custom']],
    'browserUserAgentMac': [[0, 'Default'], [1, 'Custom']],
}
TABS = [
    ('gen', 'Generali', 'General', ['General']),
    ('cfg', 'File', 'File', ['Config File']),
    ('ui', 'Interfaccia', 'Interface', ['User Interface']),
    ('br', 'Browser', 'Browser', ['Browser']),
    ('dl', 'Download/Upload', 'Download/Upload', ['DownUploads']),
    ('ex', 'Esame', 'Exam', ['Exam']),
    ('res', 'Risorse aggiuntive', 'Additional resources', []),
    ('app', 'Applicazioni', 'Applications', ['Applications']),
    ('net', 'Rete', 'Network', ['Network - Filter', 'Network - Certificates', 'Network - Proxies']),
    ('sec', 'Sicurezza', 'Security', ['Security']),
    ('proc', 'Proctoring e riunioni (Mac)', 'Proctoring and meetings (Mac)', []),
    ('ios', 'Impostazioni iOS', 'iOS settings', []),
    ('keys', 'Tasti e funzioni (Windows)', 'Keys and features (Windows)', ['Special Keys', 'Function Keys', 'Hooked Keys', 'Inside SEB']),
]
g2t = {g: t[0] for t in TABS for g in t[3]}

def human(k):
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', k)
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', s)
    return s[0].upper() + s[1:]

def clean(s):
    if not s:
        return s
    return s.replace('&', '').replace('\\r\\n', ' ').replace("\\'", "'").replace('\\"', '"').strip()

out = []
for k in order:
    i = items[k]
    if k in HIDE or i['group'] not in g2t or i['type'] in ('list', 'dict'):
        continue
    label = clean(i['label']) if i['label'] else human(k)
    e = {'k': k, 'tab': g2t[i['group']], 't': i['type'], 'd': '' if i['default'] is None else i['default'], 'l': label}
    if i['tip']:
        e['h'] = clean(i['tip'])
    if k in ENUMS:
        e['o'] = ENUMS[k]
    if k.startswith('hashed') and k.lower().endswith('password'):
        e['t'] = 'pw'
        e['l'] = {'hashedAdminPassword': 'Administrator password', 'hashedQuitPassword': 'Quit password'}.get(k, label)
    win = i['group'] in WIN_GROUPS or k in WIN_KEYS or bool(re.search(r'Win(?!dow)', k)) or not i['common']
    if win and re.search(r'OSX|Mac', k):
        win = False
    mc = (not win) and (k in MAC_KEYS or bool(re.search(r'OSX|Mac', k)))
    if win: e['p'] = 'w'
    elif mc: e['p'] = 'm'
    out.append(e)

# --- impostazioni presenti solo in SEB per macOS / settings that exist only in SEB for macOS
import glob
import xml.etree.ElementTree as ET

mac_defaults = mac[mac.index('[NSDictionary dictionaryWithObjectsAndKeys:'):]
mac_defaults = mac_defaults[:mac_defaults.index('nil]')]
mac_pairs = re.findall(r'\n\s*(.+?),\s*\n\s*@"([A-Za-z0-9]+)",', mac_defaults)

consts = {}
for hf in glob.glob(os.path.join(a.seb_mac, 'Classes', '**', '*.h'), recursive=True):
    for m in re.finditer(r'\b([A-Za-z_]\w*)\s*=\s*(-?\d+)\b', rd(hf)):
        consts.setdefault(m.group(1), int(m.group(2)))
    for m in re.finditer(r'#define\s+(\w+)\s+(-?\d+(?:\.\d+)?)\b', rd(hf)):
        consts.setdefault(m.group(1), float(m.group(2)) if '.' in m.group(2) else int(m.group(2)))

def mac_default(v):
    v = v.strip()
    if v in ('@YES', '@NO'): return 'bool', v == '@YES'
    m = re.fullmatch(r'\[NSNumber numberWith(?:Long|Integer|Int|UnsignedInteger):\s*(.+)\]', v)
    if m:
        x = m.group(1).strip()
        if re.fullmatch(r'-?\d+', x): return 'int', int(x)
        return ('int', consts[x]) if x in consts else (None, None)
    m = re.fullmatch(r'\[NSNumber numberWithDouble:\s*(-?[\d.]+|\w+)\]', v)
    if m:
        x = m.group(1)
        if re.fullmatch(r'-?[\d.]+', x): return 'float', float(x)
        return ('float', float(consts[x])) if x in consts else (None, None)
    m = re.fullmatch(r'@(-?\d+)', v)
    if m: return 'int', int(m.group(1))
    m = re.fullmatch(r'@(-?\d*\.\d+)', v)
    if m: return 'float', float(m.group(1))
    m = re.fullmatch(r'@"(.*)"', v)
    if m: return 'string', m.group(1)
    return None, None            # array, data, dizionari, costanti: non modificabili qui

XIB_TAB = {'General': 'gen', 'Appearance': 'ui', 'Browser': 'br', 'DownUploads': 'dl', 'Exam': 'exam' and 'ex',
           'Applications': 'app', 'Network': 'net', 'Security': 'sec', 'ConfigFile': 'cfg', 'Resources': 'gen'}
xib = {}
for f in sorted(glob.glob(os.path.join(a.seb_mac, 'Base.lproj', 'Preferences*.xib'))):
    tab = XIB_TAB.get(re.search(r'Preferences(\w+)\.xib', f).group(1))
    for el in ET.parse(f).getroot().iter():
        conn = el.find('connections')
        if conn is None: continue
        for b in conn.findall('binding'):
            m = re.fullmatch(r'values\.org_safeexambrowser_SEB_(\w+)', b.get('keyPath', ''))
            if not m or b.get('name') not in ('value', 'selectedIndex', 'selectedTag', 'selectedValue'): continue
            k = m.group(1)
            if k in xib: continue
            cell = el.find('.//buttonCell')
            title = cell.get('title') if cell is not None else None
            tip = el.get('toolTip')
            if tip is None:
                st = el.find("string[@key='toolTip']")
                tip = st.text if st is not None else None
            opts = None
            if el.tag == 'popUpButton':
                items = [mi for mi in el.iter('menuItem') if not mi.get('isSeparatorItem')]
                opts = [[int(mi.get('tag')) if b.get('name') == 'selectedTag' and mi.get('tag') else i, mi.get('title')]
                        for i, mi in enumerate(items) if mi.get('title')]
            xib[k] = dict(tab=tab, title=title, tip=tip, opts=opts)

# etichette, scelte e schede dalle impostazioni in-app di SEB per iOS / labels and choices from SEB for iOS in-app settings
import plistlib
IOS_TAB = {'Root': 'gen', 'SEBServer': 'gen', 'ConfigFile': 'cfg', 'UserInterface': 'ui', 'Dock': 'ui', 'Browser': 'br',
           'BrowserMediaPlayback': 'br', 'DownUploads': 'dl', 'Exam': 'ex', 'ExamKeys': 'ex', 'Network': 'net',
           'NetworkFilter': 'net', 'NetworkCertificate': 'net', 'Security': 'sec', 'SecurityLegacy': 'sec',
           'SecurityLogging': 'sec', 'RemoteProctoring': 'proc', 'RemoteProctoringFeatures': 'proc', 'AIProctoringSupport': 'proc'}
IOS_PREFIX = 'org_safeexambrowser_SEB_'
ios = {}
for f in sorted(glob.glob(os.path.join(a.seb_mac, 'SEB', 'Resources', 'InAppSettings.bundle', '*.plist'))):
    try:
        d = plistlib.load(open(f, 'rb'))
    except Exception:
        continue
    for sp in d.get('PreferenceSpecifiers', []):
        key = sp.get('Key', '')
        if not key.startswith(IOS_PREFIX): continue
        opts = None
        if sp.get('Titles') and sp.get('Values') and len(sp['Titles']) == len(sp['Values']):
            try: opts = [[int(v), str(tt)] for v, tt in zip(sp['Values'], sp['Titles'])]
            except (ValueError, TypeError): opts = None
        ios.setdefault(key[len(IOS_PREFIX):], dict(title=sp.get('Title'), opts=opts, type=sp.get('Type'),
                                                   tab=IOS_TAB.get(os.path.basename(f)[:-6])))

MAC_HIDE = {'configKeySalt', 'configFileCreateIdentity', 'configFileEncryptUsingIdentity', 'sebServerConfiguration',
            'sebServerFallbackPasswordHash', 'URLFilterIgnoreList', 'downloadFileTypes'}
def mac_tab(k):
    if k in xib and xib[k]['tab']: return xib[k]['tab']
    if re.match(r'(audio|battery)', k): return 'ui'
    if re.match(r'(jitsi|zoom|raiseHand|proctoring|screenProctoring|remoteProctoring|showProctoringView)', k): return 'proc'
    if k == 'logSendingRequiresAdminPassword': return 'sec'
    return 'gen'

have = {e['k'] for e in out} | HIDE | set(const.values())
for v, k in mac_pairs:
    if k in have or k in MAC_HIDE: continue
    x = xib.get(k, {})
    title = clean(x.get('title') or '')
    io = ios.get(k, {})
    is_ios = bool(re.match(r'(mobile|jitsiMeetUserInfoAvatar)', k) or re.search(r'iOS|iPad', k) or re.search(r'\((iOS|iPad)[^)]*\)', title))
    t, d = mac_default(v)
    if t is None: continue
    if not title or title.lower() in ('check', 'radio', 'button'):
        title = clean(io.get('title') or '') or human(k)
    e = {'k': k, 'tab': 'ios' if is_ios else mac_tab(k), 't': t, 'd': d, 'l': title,
         'p': 'i' if is_ios else ('w' if '(Win)' in title else 'm')}
    if x.get('tip'): e['h'] = clean(x['tip'])
    opts = x.get('opts') if x.get('opts') and len(x['opts']) >= 2 else io.get('opts')
    if opts and len(opts) >= 2 and t == 'int': e['o'] = opts
    out.append(e)

def lst(name):
    m = re.search(name + r'\s*=\s*new List<string>\s*\{(.*?)\};', cfg, re.S)
    return re.findall(r'"([^"]+)"', m.group(1))

schema = {'tabs': [[a_, b, c] for a_, b, c, _ in TABS], 'items': out,
          'presetBase': lst('prohibitedProcessesDefault'), 'presetStrict': lst('prohibitedProcessesDefaultStrict')}
with open(a.out, 'w', encoding='utf8') as f:
    json.dump(schema, f, ensure_ascii=False, separators=(',', ':'))
print(len(out), 'impostazioni / settings ->', os.path.normpath(a.out))
