import argparse
import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Windows: graphviz installer doesn't update PATH in the current session
if sys.platform == 'win32' and not shutil.which('dot'):
    _candidates = [
        r'C:\Program Files\Graphviz\bin',
        r'C:\Program Files (x86)\Graphviz\bin',
    ]
    for _p in _candidates:
        if os.path.isdir(_p):
            os.environ['PATH'] = _p + os.pathsep + os.environ.get('PATH', '')
            break

from parsers.xml_parser import parse
from generators.flow_map import generate_flow_maps


def main() -> None:
    parser = argparse.ArgumentParser(
        description='EBR Validation Tool – PAS-X GMBR XML → validation outputs'
    )
    parser.add_argument(
        'xml_path',
        nargs='?',
        default=None,
        help='Path to PAS-X GMBR XML export',
    )
    parser.add_argument(
        '--input', '-i',
        dest='input_flag',
        default=None,
        help='Path to PAS-X GMBR XML export (alternative to positional arg)',
    )
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory (default: output)',
    )
    args = parser.parse_args()

    xml_path = args.input_flag or args.xml_path or 'input/testxml.xml'
    print(f'Parsing: {xml_path}')
    record = parse(xml_path)

    print(f'Record  : {record.custom_id} – {record.description}')
    print(f'Material: {record.material_name}')
    print(f'Version : {record.version_id}')
    print(f'Status  : {record.current_status}')

    basic_ops = [s for s in record.top_level_steps if s.step_type == 'BasicOperationVO']
    print(f'BasicOperations: {len(basic_ops)}')
    for bo in basic_ops:
        print(f'  {bo.custom_id}: {bo.description} ({len(bo.sub_steps)} sub-steps, {len(bo.sub_links)} links)')

    print('\nGenerating process flow maps...')
    generate_flow_maps(record, output_dir=args.output_dir)

    print(f'\nDone. Outputs in: {args.output_dir}/')


if __name__ == '__main__':
    main()
