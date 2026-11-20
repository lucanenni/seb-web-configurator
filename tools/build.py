#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
"""Costruisce docs/index.html (file unico) / Builds the single-file docs/index.html."""
import os

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
tpl = open(os.path.join(root, 'src', 'index.template.html'), encoding='utf8').read()
schema = open(os.path.join(root, 'data', 'schema.json'), encoding='utf8').read()
assert tpl.count('/*SCHEMA*/null') == 1, 'segnaposto dello schema non trovato / schema placeholder not found'
out = os.path.join(root, 'docs', 'index.html')
with open(out, 'w', encoding='utf8') as f:
    f.write('<!doctype html>\n' + tpl.replace('/*SCHEMA*/null', schema))
print('scritto / written', os.path.normpath(out), os.path.getsize(out), 'byte')
