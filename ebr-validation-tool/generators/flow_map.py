from __future__ import annotations
import html
import os
import textwrap

from graphviz import Digraph

from parsers.xml_parser import GmbrRecord, Step


STEP_COLORS: dict[str, str] = {
    'StartStepVO':           '#818180',
    'EndStepVO':             '#818180',
    'BasicOperationVO':      '#460073',
    'CommonBFVO':            '#7500C0',
    'SpecDecisionVO':        '#A100FF',
    'MergeVO':               '#C2A3FF',
    'SplittingVO':           '#C2A3FF',
    'SynchronisationVO':     '#E6DCFF',
    'TakeOutBFVO':           '#FF50A0',
    'IdentityCheckBFVO':     '#FF50A0',
    'YieldDeterminationBFVO':'#FF50A0',
    'BundleCreationBFVO':    '#FF50A0',
    'StockCreationBFVO':     '#FF50A0',
    'EqmAllocationBFVO':     '#CFCFCF',
    'EqmDeallocationBFVO':   '#CFCFCF',
    'EqmIdentificationBFVO': '#CFCFCF',
    'GenericLabelPrintBfVO': '#2248FF',
    'SetCxBfVO':             '#2248FF',
}

_START_END = {'StartStepVO', 'EndStepVO'}
_LIGHT_FILLS = {'#E6DCFF', '#C2A3FF', '#CFCFCF'}
_EDGE_COLOR = '#A100FF'
_BG_COLOR = '#F5F5F5'
_WRAP_WIDTH = 22


def _node_id(custom_id: str) -> str:
    return ''.join(c if c.isalnum() else '_' for c in custom_id)


def _esc(text: str) -> str:
    return html.escape(text)


def _wrap_esc(text: str, width: int = _WRAP_WIDTH) -> str:
    lines = textwrap.wrap(text, width) or [text]
    return '<BR ALIGN="CENTER"/>'.join(_esc(line) for line in lines)


def _add_node(dot: Digraph, step: Step) -> None:
    color = STEP_COLORS.get(step.step_type, '#000000')
    nid = _node_id(step.custom_id)
    label_text = _esc(step.description or step.step_type)

    if step.step_type in _START_END:
        dot.node(
            nid,
            label=f'<{label_text}>',
            shape='oval',
            style='filled',
            fillcolor=color,
            fontcolor='white',
            fontname='Arial',
            fontsize='11',
        )
        return

    border_color = '#555555' if color in _LIGHT_FILLS else color
    font_color = 'white' if step.step_type == 'BasicOperationVO' else '#000000'
    fill_color = color if step.step_type == 'BasicOperationVO' else '#FFFFFF'

    label = (
        f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6">'
        f'<TR><TD ALIGN="CENTER"><B>'
        f'<FONT POINT-SIZE="11" COLOR="{font_color}">{_esc(step.custom_id)}</FONT>'
        f'</B></TD></TR>'
        f'<TR><TD ALIGN="CENTER">'
        f'<FONT POINT-SIZE="10" COLOR="{"#CCCCCC" if step.step_type == "BasicOperationVO" else "#666666"}">'
        f'{_wrap_esc(step.description)}'
        f'</FONT></TD></TR>'
        f'</TABLE>>'
    )

    dot.node(
        nid,
        label=label,
        shape='box',
        style='rounded,filled',
        fillcolor=fill_color,
        color=border_color,
        penwidth='2',
        fontname='Arial',
    )


def _build_graph(name: str, title: str, steps: list[Step], links: list[tuple]) -> Digraph:
    dot = Digraph(name=name, comment=title)
    dot.attr(
        rankdir='TB',
        bgcolor=_BG_COLOR,
        pad='0.6',
        nodesep='0.55',
        ranksep='0.7',
        fontname='Arial',
    )
    dot.attr('edge', color=_EDGE_COLOR, arrowhead='normal', penwidth='1.5')

    step_ids = {s.custom_id for s in steps}
    id_map = {s.custom_id: _node_id(s.custom_id) for s in steps}

    for step in steps:
        _add_node(dot, step)

    for source, target in links:
        src = id_map.get(source)
        tgt = id_map.get(target)
        if src and tgt:
            dot.edge(src, tgt)
        else:
            # Fallback: partial suffix match for path-style references
            src_key = next((k for k in step_ids if source.endswith(k) or k.endswith(source)), None)
            tgt_key = next((k for k in step_ids if target.endswith(k) or k.endswith(target)), None)
            if src_key and tgt_key:
                dot.edge(id_map[src_key], id_map[tgt_key])

    return dot


def generate_flow_maps(record: GmbrRecord, output_dir: str = 'output') -> None:
    os.makedirs(output_dir, exist_ok=True)

    overview = _build_graph(
        name='overview',
        title=f'{record.custom_id} – {record.description}',
        steps=record.top_level_steps,
        links=record.top_level_links,
    )
    out = os.path.join(output_dir, 'process_flow_overview')
    overview.render(out, format='png', cleanup=True)
    print(f'  [OK] {out}.png')

    for step in record.top_level_steps:
        if step.step_type != 'BasicOperationVO':
            continue
        if not step.sub_steps:
            print(f'  [SKIP] {step.custom_id} – no sub-steps found')
            continue
        drilldown = _build_graph(
            name=step.custom_id,
            title=f'{step.custom_id} – {step.description}',
            steps=step.sub_steps,
            links=step.sub_links,
        )
        out = os.path.join(output_dir, f'process_flow_{step.custom_id}')
        drilldown.render(out, format='png', cleanup=True)
        print(f'  [OK] {out}.png')
