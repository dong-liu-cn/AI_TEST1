#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
extract_excel_shapes.py
Excelファイル（.xlsx）から図形（Shape）データを抽出し、
画面遷移図などのフローチャートをMermaid記法 + 遷移テーブルに変換する。

使用方法:
    python extract_excel_shapes.py --input "path/to/file.xlsx" [--sheet "画面遷移図"]

依存:
    pip install openpyxl lxml
"""

import argparse
import io
import json
import os
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 修复控制台编码
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf8"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from lxml import etree
except ImportError:
    print("lxmlが必要です: pip install lxml", file=sys.stderr)
    sys.exit(1)

try:
    import openpyxl
except ImportError:
    print("openpyxlが必要です: pip install openpyxl", file=sys.stderr)
    sys.exit(1)


# Excel内部XMLの名前空間
NAMESPACES = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
    'dgm': 'http://schemas.openxmlformats.org/drawingml/2006/diagram',
}


def extract_drawing_xmls(xlsx_path: str) -> Dict[str, bytes]:
    """
    .xlsxファイル（ZIP形式）から、xl/drawings/ 配下のXMLファイルを抽出する。
    
    Returns:
        {ファイル名: XMLバイナリ} の辞書
    """
    drawings = {}
    with zipfile.ZipFile(xlsx_path, 'r') as zf:
        for name in zf.namelist():
            if 'drawings' in name.lower() and name.endswith('.xml'):
                drawings[name] = zf.read(name)
    return drawings


def list_all_internal_files(xlsx_path: str) -> List[str]:
    """
    .xlsxファイル内の全ファイル一覧を返す。
    """
    with zipfile.ZipFile(xlsx_path, 'r') as zf:
        return zf.namelist()


def extract_sheet_drawing_mapping(xlsx_path: str) -> Dict[str, str]:
    """
    シート名 → DrawingファイルのマッピングをRels情報から構築する。
    
    Returns:
        {'Sheet1': 'xl/drawings/drawing1.xml', ...}
    """
    mapping = {}
    
    with zipfile.ZipFile(xlsx_path, 'r') as zf:
        # まずworkbook.xmlからシートID→シート名のマッピングを取得
        wb_xml = zf.read('xl/workbook.xml')
        wb_tree = etree.fromstring(wb_xml)
        
        # シートID→シート名
        sheet_info = {}
        ns_wb = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                 'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
        sheets = wb_tree.findall('.//s:sheet', ns_wb)
        for sheet in sheets:
            name = sheet.get('name')
            rid = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            sheet_info[rid] = name
        
        # workbook.xml.relsからrId→sheetN.xmlのマッピング
        wb_rels_path = 'xl/_rels/workbook.xml.rels'
        if wb_rels_path in zf.namelist():
            rels_xml = zf.read(wb_rels_path)
            rels_tree = etree.fromstring(rels_xml)
            rid_to_sheet_file = {}
            for rel in rels_tree:
                rid = rel.get('Id')
                target = rel.get('Target')
                if target and 'worksheets/' in target:
                    rid_to_sheet_file[rid] = target
            
            # 各シートファイルの.relsからdrawing参照を探す
            for rid, sheet_file in rid_to_sheet_file.items():
                sheet_name = sheet_info.get(rid, sheet_file)
                # sheetN.xml.rels を探す
                sheet_basename = os.path.basename(sheet_file)
                rels_path = f'xl/worksheets/_rels/{sheet_basename}.rels'
                if rels_path in zf.namelist():
                    sheet_rels = zf.read(rels_path)
                    sheet_rels_tree = etree.fromstring(sheet_rels)
                    for rel in sheet_rels_tree:
                        target = rel.get('Target')
                        rel_type = rel.get('Type', '')
                        if target and 'drawing' in rel_type.lower():
                            # 相対パス解決
                            drawing_path = f'xl/drawings/{os.path.basename(target)}'
                            mapping[sheet_name] = drawing_path
    
    return mapping


def parse_shape_info(drawing_xml: bytes) -> List[Dict[str, Any]]:
    """
    Drawing XMLから図形情報を抽出する。
    
    Returns:
        図形情報のリスト。各要素は:
        {
            'id': str,           # 図形ID
            'name': str,         # 図形名
            'text': str,         # 図形内テキスト
            'type': str,         # 'shape', 'connector', 'group', 'picture'
            'preset': str,       # プリセット図形タイプ（rect, flowChartProcess等）
            'position': dict,    # 位置情報 {from_col, from_row, to_col, to_row}
            'connections': list,  # コネクタの接続先情報
        }
    """
    tree = etree.fromstring(drawing_xml)
    shapes = []
    
    # twoCellAnchor（2セル固定）内の図形を探索
    anchors = tree.findall('.//xdr:twoCellAnchor', NAMESPACES)
    anchors += tree.findall('.//xdr:oneCellAnchor', NAMESPACES)
    
    for anchor in anchors:
        # 位置情報取得
        from_elem = anchor.find('xdr:from', NAMESPACES)
        to_elem = anchor.find('xdr:to', NAMESPACES)
        position = {}
        if from_elem is not None:
            col = from_elem.find('xdr:col', NAMESPACES)
            row = from_elem.find('xdr:row', NAMESPACES)
            position['from_col'] = int(col.text) if col is not None and col.text else 0
            position['from_row'] = int(row.text) if row is not None and row.text else 0
        if to_elem is not None:
            col = to_elem.find('xdr:col', NAMESPACES)
            row = to_elem.find('xdr:row', NAMESPACES)
            position['to_col'] = int(col.text) if col is not None and col.text else 0
            position['to_row'] = int(row.text) if row is not None and row.text else 0
        
        # sp（通常図形）
        sp = anchor.find('xdr:sp', NAMESPACES)
        if sp is not None:
            shape_info = _parse_sp(sp, position)
            if shape_info:
                shapes.append(shape_info)
            continue
        
        # cxnSp（コネクタ/矢印）
        cxn_sp = anchor.find('xdr:cxnSp', NAMESPACES)
        if cxn_sp is not None:
            conn_info = _parse_cxn_sp(cxn_sp, position)
            if conn_info:
                shapes.append(conn_info)
            continue
        
        # grpSp（グループ図形）
        grp_sp = anchor.find('xdr:grpSp', NAMESPACES)
        if grp_sp is not None:
            group_shapes = _parse_grp_sp(grp_sp, position)
            shapes.extend(group_shapes)
            continue
        
        # pic（画像）
        pic = anchor.find('xdr:pic', NAMESPACES)
        if pic is not None:
            shapes.append({
                'id': 'pic',
                'name': 'Picture',
                'text': '',
                'type': 'picture',
                'preset': '',
                'position': position,
                'connections': [],
            })
    
    return shapes


def _extract_text_from_element(elem) -> str:
    """
    図形要素からテキストを再帰的に抽出する。
    """
    texts = []
    # a:t (テキスト)要素を探す
    for t in elem.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'):
        if t.text:
            texts.append(t.text.strip())
    return ' '.join(texts)


def _parse_sp(sp, position: dict) -> Optional[Dict[str, Any]]:
    """
    通常図形（sp）をパースする。
    """
    # nvSpPr（非ビジュアルプロパティ）
    nv_sp_pr = sp.find('xdr:nvSpPr', NAMESPACES)
    if nv_sp_pr is None:
        nv_sp_pr = sp.find('{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}nvSpPr')
    
    shape_id = ''
    shape_name = ''
    if nv_sp_pr is not None:
        c_nv_pr = nv_sp_pr.find('xdr:cNvPr', NAMESPACES)
        if c_nv_pr is None:
            c_nv_pr = nv_sp_pr.find('{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}cNvPr')
        if c_nv_pr is not None:
            shape_id = c_nv_pr.get('id', '')
            shape_name = c_nv_pr.get('name', '')
    
    # spPr（図形プロパティ）からプリセットタイプを取得
    sp_pr = sp.find('xdr:spPr', NAMESPACES)
    if sp_pr is None:
        sp_pr = sp.find('{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}spPr')
    
    preset = ''
    if sp_pr is not None:
        prst_geom = sp_pr.find('.//a:prstGeom', NAMESPACES)
        if prst_geom is not None:
            preset = prst_geom.get('prst', '')
    
    # テキスト抽出
    text = _extract_text_from_element(sp)
    
    return {
        'id': shape_id,
        'name': shape_name,
        'text': text,
        'type': 'shape',
        'preset': preset,
        'position': position,
        'connections': [],
    }


def _parse_cxn_sp(cxn_sp, position: dict) -> Optional[Dict[str, Any]]:
    """
    コネクタ（cxnSp）をパースする。矢印の接続先IDを取得。
    """
    nv_cxn = cxn_sp.find('xdr:nvCxnSpPr', NAMESPACES)
    if nv_cxn is None:
        nv_cxn = cxn_sp.find('{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}nvCxnSpPr')
    
    conn_id = ''
    conn_name = ''
    connections = []
    
    if nv_cxn is not None:
        c_nv_pr = nv_cxn.find('xdr:cNvPr', NAMESPACES)
        if c_nv_pr is None:
            c_nv_pr = nv_cxn.find('{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}cNvPr')
        if c_nv_pr is not None:
            conn_id = c_nv_pr.get('id', '')
            conn_name = c_nv_pr.get('name', '')
        
        # cNvCxnSpPr内の接続情報
        c_nv_cxn = nv_cxn.find('xdr:cNvCxnSpPr', NAMESPACES)
        if c_nv_cxn is None:
            c_nv_cxn = nv_cxn.find('{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}cNvCxnSpPr')
        
        if c_nv_cxn is not None:
            # stCxn（開始接続）
            st_cxn = c_nv_cxn.find('a:stCxn', NAMESPACES)
            if st_cxn is not None:
                connections.append({
                    'type': 'start',
                    'target_id': st_cxn.get('id', ''),
                    'idx': st_cxn.get('idx', ''),
                })
            # endCxn（終了接続）
            end_cxn = c_nv_cxn.find('a:endCxn', NAMESPACES)
            if end_cxn is not None:
                connections.append({
                    'type': 'end',
                    'target_id': end_cxn.get('id', ''),
                    'idx': end_cxn.get('idx', ''),
                })
    
    # コネクタ上のテキスト（ラベル）
    text = _extract_text_from_element(cxn_sp)
    
    return {
        'id': conn_id,
        'name': conn_name,
        'text': text,
        'type': 'connector',
        'preset': '',
        'position': position,
        'connections': connections,
    }


def _parse_grp_sp(grp_sp, position: dict) -> List[Dict[str, Any]]:
    """
    グループ図形を再帰的にパースする。
    """
    shapes = []
    
    # グループ内のsp
    for sp in grp_sp.findall('.//xdr:sp', NAMESPACES):
        info = _parse_sp(sp, position)
        if info:
            shapes.append(info)
    
    # グループ内のcxnSp
    for cxn in grp_sp.findall('.//xdr:cxnSp', NAMESPACES):
        info = _parse_cxn_sp(cxn, position)
        if info:
            shapes.append(info)
    
    # グループ内のサブグループ（a:sp / a:cxnSp形式もチェック）
    for sp in grp_sp.findall('.//a:sp', NAMESPACES):
        # drawingML直接の図形
        text = _extract_text_from_element(sp)
        nv = sp.find('a:nvSpPr', NAMESPACES)
        sid = ''
        sname = ''
        if nv is not None:
            cnv = nv.find('a:cNvPr', NAMESPACES)
            if cnv is not None:
                sid = cnv.get('id', '')
                sname = cnv.get('name', '')
        
        preset = ''
        sp_pr = sp.find('a:spPr', NAMESPACES)
        if sp_pr is not None:
            prst = sp_pr.find('.//a:prstGeom', NAMESPACES)
            if prst is not None:
                preset = prst.get('prst', '')
        
        shapes.append({
            'id': sid,
            'name': sname,
            'text': text,
            'type': 'shape',
            'preset': preset,
            'position': position,
            'connections': [],
        })
    
    return shapes


def build_transition_graph(shapes: List[Dict]) -> List[Dict]:
    """
    図形とコネクタの情報から画面遷移グラフを構築する。
    近隣のテキスト図形をトリガーラベルとして推定する機能を含む。
    
    Returns:
        遷移情報リスト [{source, target, label, transition_type}, ...]
    """
    # ID→図形のマッピング（name中の数字でもフォールバック可能にする）
    id_to_shape = {}
    name_num_to_shape = {}  # name中の数字 → shape（フォールバック用）
    connectors = []
    label_shapes = []  # ラベル候補（アクション名等のテキスト図形）
    screen_shapes = []  # 画面名図形
    
    # アクション名のキーワード（ラベルとして使われる図形の特徴）
    action_keywords = ['ボタン', '押下', 'リンク', 'アイコン', 'クリック', '選択', '出力']
    
    import re as _re
    for s in shapes:
        if s['type'] == 'shape' and s['id']:
            id_to_shape[s['id']] = s
            # name末尾の数字をフォールバック用に登録
            nums = _re.findall(r'\d+', s.get('name', ''))
            for n in nums:
                if n not in name_num_to_shape:
                    name_num_to_shape[n] = s
            if s['text']:
                # アクション名かどうかを判定
                is_action = any(kw in s['text'] for kw in action_keywords)
                if is_action:
                    label_shapes.append(s)
                else:
                    # 吹き出し（wedge/callout）はスキップ
                    preset = s.get('preset', '')
                    if 'callout' not in preset.lower() and 'Callout' not in preset:
                        screen_shapes.append(s)
        elif s['type'] == 'connector':
            connectors.append(s)
    
    def _find_nearest_label(conn_pos: dict, used_labels: set) -> str:
        """
        コネクタの位置に最も近いラベル図形を探す。
        コネクタの開始点～終了点の間にあるテキスト図形をラベルとして採用する。
        """
        if not label_shapes:
            return ''
        
        conn_from_row = conn_pos.get('from_row', 0)
        conn_from_col = conn_pos.get('from_col', 0)
        conn_to_row = conn_pos.get('to_row', 0)
        conn_to_col = conn_pos.get('to_col', 0)
        
        # コネクタの中心点
        conn_mid_row = (conn_from_row + conn_to_row) / 2
        conn_mid_col = (conn_from_col + conn_to_col) / 2
        
        best_label = ''
        best_dist = float('inf')
        
        for ls in label_shapes:
            if id(ls) in used_labels:
                continue
            ls_pos = ls['position']
            ls_mid_row = (ls_pos.get('from_row', 0) + ls_pos.get('to_row', 0)) / 2
            ls_mid_col = (ls_pos.get('from_col', 0) + ls_pos.get('to_col', 0)) / 2
            
            # ユークリッド距離
            dist = ((conn_mid_row - ls_mid_row) ** 2 + (conn_mid_col - ls_mid_col) ** 2) ** 0.5
            
            # 距離が近い方を採用（閾値: 15セル以内）
            if dist < best_dist and dist < 15:
                best_dist = dist
                best_label = ls['text']
                best_ls = ls
        
        if best_label:
            used_labels.add(id(best_ls))
        
        return best_label
    
    def _find_nearest_screen(target_id: str, conn_pos: dict) -> Dict:
        """
        コネクタの端点が図形に未接続の場合、位置的に最も近い画面図形を推定する。
        """
        conn_row = conn_pos.get('from_row', 0)
        conn_col = conn_pos.get('from_col', 0)
        
        best_shape = {}
        best_dist = float('inf')
        
        for ss in screen_shapes:
            ss_pos = ss['position']
            ss_mid_row = (ss_pos.get('from_row', 0) + ss_pos.get('to_row', 0)) / 2
            ss_mid_col = (ss_pos.get('from_col', 0) + ss_pos.get('to_col', 0)) / 2
            
            dist = ((conn_row - ss_mid_row) ** 2 + (conn_col - ss_mid_col) ** 2) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best_shape = ss
        
        return best_shape
    
    transitions = []
    used_labels = set()
    
    for conn in connectors:
        start_id = None
        end_id = None
        for c in conn.get('connections', []):
            if c['type'] == 'start':
                start_id = c['target_id']
            elif c['type'] == 'end':
                end_id = c['target_id']
        
        # 接続先の図形を取得（テキスト付きの図形を優先、なければname数字でフォールバック）
        def _resolve_shape(sid):
            if not sid:
                return {}
            s = id_to_shape.get(sid)
            if s and s.get('text', '').strip():
                return s
            # IDの図形にテキストがない場合、name数字でフォールバック
            s2 = name_num_to_shape.get(sid)
            if s2 and s2.get('text', '').strip():
                return s2
            return s or s2 or {}
        
        source = _resolve_shape(start_id)
        target = _resolve_shape(end_id)
        
        # 接続先が見つからない場合、位置から推定
        if not source.get('text') and not start_id:
            source = _find_nearest_screen(start_id, {
                'from_row': conn['position'].get('from_row', 0),
                'from_col': conn['position'].get('from_col', 0),
            })
        if not target.get('text') and not end_id:
            target = _find_nearest_screen(end_id, {
                'from_row': conn['position'].get('to_row', 0),
                'from_col': conn['position'].get('to_col', 0),
            })
        
        source_text = source.get('text', '')
        target_text = target.get('text', '')
        
        if not source_text and not target_text:
            continue  # 両方不明なコネクタはスキップ
        
        # コネクタのテキスト or 近隣テキスト図形からラベルを推定
        label = conn.get('text', '')
        if not label:
            label = _find_nearest_label(conn['position'], used_labels)
        
        # 遷移タイプの推定
        t_type = '画面遷移'
        if 'ダイアログ' in target_text:
            t_type = 'ダイアログ'
        elif '日報' in target_text or 'レポート' in target_text or '帳票' in target_text:
            t_type = '帳票出力'
        elif 'Excel' in label or 'CSV' in label:
            t_type = 'ファイル出力'
        
        transitions.append({
            'source': source_text or f'Shape_{start_id}',
            'target': target_text or f'Shape_{end_id}',
            'label': label,
            'transition_type': t_type,
        })
    
    return transitions


def generate_mermaid(transitions: List[Dict], shapes: List[Dict]) -> str:
    """
    遷移情報からMermaid記法を生成する。
    """
    if not transitions:
        # コネクタ接続情報がない場合、図形テキストのみからフロー推定
        return _generate_mermaid_from_shapes(shapes)
    
    lines = ['```mermaid', 'graph LR']
    
    # ノードID割り当て
    node_ids = {}
    counter = [0]
    
    def get_node_id(name: str) -> str:
        if name not in node_ids:
            node_ids[name] = chr(65 + counter[0])  # A, B, C, ...
            counter[0] += 1
        return node_ids[name]
    
    for t in transitions:
        src_id = get_node_id(t['source'])
        tgt_id = get_node_id(t['target'])
        src_text = t['source'].replace('\n', '<br/>')
        tgt_text = t['target'].replace('\n', '<br/>')
        label = t['label']
        
        if label:
            lines.append(f'    {src_id}[{src_text}] -->|{label}| {tgt_id}[{tgt_text}]')
        else:
            lines.append(f'    {src_id}[{src_text}] --> {tgt_id}[{tgt_text}]')
    
    lines.append('```')
    return '\n'.join(lines)


def _generate_mermaid_from_shapes(shapes: List[Dict]) -> str:
    """
    コネクタ情報がない場合、図形の位置関係からMermaidを生成する。
    テキスト付き図形のみを列挙する。
    """
    text_shapes = [s for s in shapes if s['type'] == 'shape' and s['text'].strip()]
    
    if not text_shapes:
        return '> ※ 図形データからテキストを抽出できませんでした。手動でMermaid記法を作成してください。'
    
    # 位置でソート（行→列）
    text_shapes.sort(key=lambda s: (
        s['position'].get('from_row', 0),
        s['position'].get('from_col', 0)
    ))
    
    lines = ['```mermaid', 'graph LR']
    for i, s in enumerate(text_shapes):
        node_id = chr(65 + i) if i < 26 else f'N{i}'
        text = s['text'].replace('\n', '<br/>')
        lines.append(f'    {node_id}[{text}]')
    
    # 位置関係から接続を推定（左→右、上→下）
    for i in range(len(text_shapes) - 1):
        src_id = chr(65 + i) if i < 26 else f'N{i}'
        tgt_id = chr(65 + i + 1) if (i + 1) < 26 else f'N{i+1}'
        lines.append(f'    {src_id} --> {tgt_id}')
    
    lines.append('```')
    return '\n'.join(lines)


def generate_transition_table(transitions: List[Dict]) -> str:
    """
    遷移情報からMarkdownテーブルを生成する。
    """
    if not transitions:
        return '> ※ 遷移情報を自動抽出できませんでした。'
    
    lines = [
        '| No | 遷移元画面 | トリガー | 遷移先画面 | 遷移タイプ |',
        '|----|-----------|---------|-----------|-----------|',
    ]
    
    for i, t in enumerate(transitions, 1):
        lines.append(
            f'| {i} | {t["source"]} | {t["label"]} | {t["target"]} | {t["transition_type"]} |'
        )
    
    return '\n'.join(lines)


def analyze_excel_file(xlsx_path: str, target_sheet: Optional[str] = None) -> Dict[str, Any]:
    """
    Excelファイルを総合的に分析し、図形データを抽出する。
    
    Args:
        xlsx_path: Excelファイルパス
        target_sheet: 特定シートのみ分析する場合のシート名
    
    Returns:
        分析結果の辞書
    """
    result = {
        'file': xlsx_path,
        'internal_files': [],
        'sheets': [],
        'sheet_drawing_mapping': {},
        'drawings': {},
    }
    
    # 1. 内部ファイル一覧
    result['internal_files'] = list_all_internal_files(xlsx_path)
    
    # 2. シート一覧
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    result['sheets'] = wb.sheetnames
    wb.close()
    
    # 3. シート→Drawing マッピング
    result['sheet_drawing_mapping'] = extract_sheet_drawing_mapping(xlsx_path)
    
    # 4. Drawing XMLの解析
    drawings = extract_drawing_xmls(xlsx_path)
    
    for sheet_name, drawing_path in result['sheet_drawing_mapping'].items():
        if target_sheet and sheet_name != target_sheet:
            continue
        
        if drawing_path in drawings:
            xml_data = drawings[drawing_path]
            shapes = parse_shape_info(xml_data)
            transitions = build_transition_graph(shapes)
            
            result['drawings'][sheet_name] = {
                'drawing_file': drawing_path,
                'shapes': shapes,
                'transitions': transitions,
                'mermaid': generate_mermaid(transitions, shapes),
                'transition_table': generate_transition_table(transitions),
            }
    
    return result


def print_analysis_report(result: Dict[str, Any]):
    """
    分析結果をレポートとして表示する。
    """
    print("=" * 70)
    print(f"Excel図形データ分析レポート")
    print(f"ファイル: {result['file']}")
    print("=" * 70)
    
    print(f"\n■ シート一覧 ({len(result['sheets'])}シート):")
    for i, name in enumerate(result['sheets'], 1):
        has_drawing = '📊 Drawing有' if name in result['sheet_drawing_mapping'] else ''
        print(f"  {i}. {name} {has_drawing}")
    
    print(f"\n■ Drawing関連ファイル:")
    for f in result['internal_files']:
        if 'drawing' in f.lower() or 'chart' in f.lower():
            print(f"  - {f}")
    
    print(f"\n■ シート→Drawing マッピング:")
    for sheet, drawing in result['sheet_drawing_mapping'].items():
        print(f"  {sheet} → {drawing}")
    
    for sheet_name, data in result['drawings'].items():
        print(f"\n{'=' * 70}")
        print(f"■ シート: {sheet_name}")
        print(f"  Drawing: {data['drawing_file']}")
        
        # 図形一覧
        shapes = data['shapes']
        text_shapes = [s for s in shapes if s['type'] == 'shape' and s['text'].strip()]
        connectors = [s for s in shapes if s['type'] == 'connector']
        
        print(f"\n  図形数: {len(shapes)} (テキスト付き: {len(text_shapes)}, コネクタ: {len(connectors)})")
        
        print(f"\n  テキスト付き図形:")
        for s in text_shapes:
            pos = s['position']
            print(f"    - ID:{s['id']} 名前:{s['name']} テキスト:「{s['text']}」")
            print(f"      位置: ({pos.get('from_col','-')},{pos.get('from_row','-')}) → ({pos.get('to_col','-')},{pos.get('to_row','-')})")
            print(f"      プリセット: {s['preset']}")
        
        print(f"\n  コネクタ:")
        for c in connectors:
            conns = c.get('connections', [])
            start = next((x['target_id'] for x in conns if x['type'] == 'start'), '-')
            end = next((x['target_id'] for x in conns if x['type'] == 'end'), '-')
            print(f"    - ID:{c['id']} テキスト:「{c['text']}」 接続: {start} → {end}")
        
        # 遷移情報
        transitions = data['transitions']
        if transitions:
            print(f"\n  遷移情報 ({len(transitions)}件):")
            for t in transitions:
                print(f"    [{t['source']}] --({t['label']})--> [{t['target']}] ({t['transition_type']})")
        
        # Mermaid出力
        print(f"\n  Mermaid記法:")
        print(data['mermaid'])
        
        # テーブル出力
        print(f"\n  遷移テーブル:")
        print(data['transition_table'])


def export_markdown(result: Dict[str, Any], output_path: str):
    """
    分析結果をMarkdownファイルとして出力する。
    """
    lines = []
    
    for sheet_name, data in result['drawings'].items():
        lines.append(f'## {sheet_name}')
        lines.append('')
        
        # 図形テキスト一覧（画面名のみ。アクション名・吹き出しを除外）
        action_kw = ['ボタン', '押下', 'リンク', 'アイコン', 'クリック', '出力']
        screen_shapes = [
            s for s in data['shapes']
            if s['type'] == 'shape' and s['text'].strip()
            and not any(kw in s['text'] for kw in action_kw)
            and 'callout' not in s.get('preset', '').lower()
        ]
        if screen_shapes:
            lines.append('### 画面一覧（図形から抽出）')
            lines.append('')
            lines.append('| No | 画面名 | 図形タイプ |')
            lines.append('|----|--------|-----------|')
            for i, s in enumerate(screen_shapes, 1):
                lines.append(f'| {i} | {s["text"]} | {s["preset"] or "-"} |')
            lines.append('')
        
        # Mermaid
        lines.append('### 遷移図')
        lines.append('')
        lines.append(data['mermaid'])
        lines.append('')
        
        # 遷移テーブル
        lines.append('### 遷移定義テーブル')
        lines.append('')
        lines.append(data['transition_table'])
        lines.append('')
        lines.append('---')
        lines.append('')
    
    content = '\n'.join(lines)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nMarkdown出力完了: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Excel基本設計書から図形（画面遷移図等）を抽出し、Mermaid + 遷移テーブルに変換する',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--input', required=True, help='入力Excelファイルパス')
    parser.add_argument('--sheet', default=None, help='特定シート名を指定（省略時は全シート）')
    parser.add_argument('--output', default=None, help='Markdown出力パス（省略時はコンソール出力のみ）')
    parser.add_argument('--json', default=None, help='JSON出力パス（図形データの生データ）')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"エラー: ファイルが見つかりません: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # 分析実行
    result = analyze_excel_file(args.input, args.sheet)
    
    # コンソールレポート
    print_analysis_report(result)
    
    # Markdown出力
    if args.output:
        export_markdown(result, args.output)
    
    # JSON出力
    if args.json:
        # JSON直列化のため、bytesなどを除外
        json_data = {
            'file': result['file'],
            'sheets': result['sheets'],
            'sheet_drawing_mapping': result['sheet_drawing_mapping'],
            'drawings': {},
        }
        for sheet_name, data in result['drawings'].items():
            json_data['drawings'][sheet_name] = {
                'shapes': data['shapes'],
                'transitions': data['transitions'],
                'mermaid': data['mermaid'],
                'transition_table': data['transition_table'],
            }
        
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"\nJSON出力完了: {args.json}")


if __name__ == '__main__':
    main()