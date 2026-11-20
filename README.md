# seb-web-configurator

**English** · [Italiano](README.it.md)

A single-page web tool that creates and edits **Safe Exam Browser (SEB) `.seb` configuration files**, entirely in the browser. Nothing is uploaded anywhere. It works the same on macOS, Windows and mobile browsers, so there is no need to open SEB just to build a file.

It works with any online test and was built with one common case in mind: running a **Google Form** in SEB (link, full screen, no other windows or tabs, WiFi control off, quit password), with an **advanced mode** that exposes the settings of SEB itself.

> Unofficial project, not affiliated with ETH Zurich or the SEB project. Settings, defaults, labels and tooltips are derived from the open-source SEB repositories (Windows configurator and macOS preferences).

## Features

- **Simple mode**: test link (a Google Form or any other web address), start in full screen (default on), optional exam password (encrypts the file), optional quit password. The file always blocks new windows and tabs and turns off WiFi controls.
- **Edit link fix**: a `…/edit` link is converted to `…/viewform` automatically.
- **Advanced mode** (switch in the top bar, next to the language switch): 343 settings in 13 tabs, with SEB's own labels and tooltips, a search box and a reset button for each setting. Only the settings you change are written to the file.
  - 99 settings common to Windows and macOS, 67 marked **Windows**, 139 marked **Mac**, 38 marked **iOS**.
  - Editors for the complex settings: permitted and prohibited processes (with SEB's default lists and the Mac-only fields), URL filter rules, proxies, **additional resources** (with embedded files and per-resource URL rules), **embedded certificates** (`.cer`, `.crt`, `.der`, `.pem`, `.p12`), allowed SEB versions, URL filter ignore list, SEB Server configuration and the iOS file types.
- **Open an existing `.seb`** (plain or password-encrypted) to edit it. Stored password hashes are kept; settings the tool does not know are preserved untouched.
- **Italian / English** interface. It follows the browser language (Italian for Italian browsers, English for everyone else) and the switch in the top right is remembered.
- Encryption uses the same scheme SEB expects (RNCryptor v3, prefix `pswd`), implemented with the Web Crypto API.

## Use

Open it online at **https://lucanenni.github.io/seb-web-configurator/**, or open [`docs/index.html`](docs/index.html) in a modern browser, or host the `docs/` folder on any static server. No build step is needed to use it.

1. Paste the test link, choose the options, press **Create the .seb file** (the **Open an existing .seb…** and **Create** buttons are in the top bar).
2. Send `exam.seb` to the students (plus the password, if you set one).
3. Students double-click the file: SEB starts and opens the form.

## Build from source

Requirements: Python 3 and Node 20 or later. The built page is committed in `docs/`, so the schema step is only needed to refresh the settings from newer SEB sources.

```bash
# 1. (optional) regenerate data/schema.json from clones of the SEB repositories
git clone --depth 1 https://github.com/SafeExamBrowser/seb-win-refactoring.git ../seb-win-refactoring
git clone --depth 1 https://github.com/SafeExamBrowser/seb-mac.git ../seb-mac
npm run schema

# 2. build docs/index.html from src/ and data/
npm run build

# 3. run the tests
npm test
```

| Path | Content |
| --- | --- |
| `src/index.template.html` | The whole app (HTML, CSS, JS, both languages) |
| `data/schema.json` | Settings, defaults, labels, tooltips, enumerations |
| `tools/extract_schema.py` | Builds the schema from the SEB sources |
| `tools/build.py` | Injects the schema into the template |
| `docs/index.html` | The single-file result |
| `tests/` | Round trip of the file format, schema checks |

## Limits

- Files encrypted with a certificate cannot be opened. Resource icons and nested sub-resources are not editable: when you open a file they are kept as they are.
- Additional resources are read by SEB for macOS; the current SEB for Windows code does not read them.
- Labels and tooltips are in English, as in SEB.
- Windows-only and Mac-only settings are ignored by the other system.
- The generated files were checked structurally and with a round trip. Always try a file on both systems before an exam.
- SEB cannot trigger Google Forms' **locked mode**, which requires a managed Chromebook. SEB does its own lockdown instead. It does not stop a second physical monitor or device.

## License

[Mozilla Public License 2.0](LICENSE), the same license as SEB. `data/schema.json` contains labels, tooltips and defaults derived from the SEB source code (© ETH Zurich, IT Services, MPL-2.0); see [NOTICE](NOTICE). This project is not affiliated with or endorsed by ETH Zurich or the SEB project.
