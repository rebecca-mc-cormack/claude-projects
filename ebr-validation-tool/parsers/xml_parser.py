from __future__ import annotations
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional


STEP_TYPES = {
    'StartStepVO', 'EndStepVO', 'BasicOperationVO', 'CommonBFVO',
    'SpecDecisionVO', 'MergeVO', 'SplittingVO', 'SynchronisationVO',
    'TakeOutBFVO', 'IdentityCheckBFVO', 'YieldDeterminationBFVO',
    'BundleCreationBFVO', 'StockCreationBFVO', 'EqmAllocationBFVO',
    'EqmDeallocationBFVO', 'EqmIdentificationBFVO', 'GenericLabelPrintBfVO',
    'SetCxBfVO',
}

ACTIVITY_TYPES = {
    'MeasuredValueSpecPropVO', 'FormulaSpecPropVO', 'TextSpecPropVO',
    'DateSpecPropVO', 'AttributiveSpecPropVO', 'ListSpecPropVO',
}


@dataclass
class Activity:
    custom_id: str
    description: str
    activity_type: str
    set_value: Optional[str] = None
    min_tolerance: Optional[str] = None
    max_tolerance: Optional[str] = None
    unit: Optional[str] = None
    formula_text: Optional[str] = None
    criticality: Optional[str] = None


@dataclass
class Step:
    custom_id: str
    description: str
    step_type: str
    activities: list = field(default_factory=list)
    sub_steps: list = field(default_factory=list)
    sub_links: list = field(default_factory=list)


@dataclass
class GmbrRecord:
    custom_id: str
    description: str
    material_name: str
    version_id: str
    current_status: str
    top_level_steps: list = field(default_factory=list)
    top_level_links: list = field(default_factory=list)


def _strip_ns(tag: str) -> str:
    return tag.split('}', 1)[-1] if '}' in tag else tag


def _text(element: ET.Element, tag: str, default: str = '') -> str:
    for child in element:
        if _strip_ns(child.tag) == tag:
            return (child.text or '').strip()
    return default


def _extract_links(parent: ET.Element) -> list:
    links = []
    for child in parent:
        if _strip_ns(child.tag) == 'prodStepLinkCollection':
            for link in child:
                if _strip_ns(link.tag) == 'ProdStepLinkVO':
                    source = _text(link, 'sourceProdStep')
                    target = _text(link, 'targetProdStep')
                    if source and target:
                        links.append((source, target))
            break
    return links


def _extract_unit(element: ET.Element) -> Optional[str]:
    for child in element:
        if _strip_ns(child.tag) == 'unit':
            return _text(child, 'customId') or None
    return None


def _extract_activities(step_el: ET.Element) -> list:
    activities = []
    for child in step_el:
        if _strip_ns(child.tag) != 'specPropCollection':
            continue
        for prop in child:
            tag = _strip_ns(prop.tag)
            if tag not in ACTIVITY_TYPES:
                continue
            act = Activity(
                custom_id=_text(prop, 'customId'),
                description=_text(prop, 'description'),
                activity_type=tag,
                criticality=_text(prop, 'criticality') or None,
            )
            if tag == 'MeasuredValueSpecPropVO':
                act.set_value = _text(prop, 'setValue') or None
                act.min_tolerance = _text(prop, 'minTolerance') or None
                act.max_tolerance = _text(prop, 'maxTolerance') or None
                act.unit = _extract_unit(prop)
            elif tag == 'FormulaSpecPropVO':
                act.formula_text = _text(prop, 'formulaText') or None
                act.unit = _extract_unit(prop)
            activities.append(act)
        break
    return activities


def _extract_steps(parent: ET.Element, allow_basic_ops: bool = True) -> list:
    steps = []
    for child in parent:
        tag = _strip_ns(child.tag)
        if tag not in STEP_TYPES:
            continue
        if tag == 'BasicOperationVO' and not allow_basic_ops:
            continue
        step = Step(
            custom_id=_text(child, 'customId'),
            description=_text(child, 'description'),
            step_type=tag,
            activities=_extract_activities(child),
        )
        if tag == 'BasicOperationVO':
            step.sub_steps = _extract_steps(child, allow_basic_ops=False)
            step.sub_links = _extract_links(child)
        steps.append(step)
    return steps


def _find_gmbr(element: ET.Element) -> Optional[ET.Element]:
    if _strip_ns(element.tag) == 'GenericMasterBatchRecordVO':
        return element
    for child in element:
        result = _find_gmbr(child)
        if result is not None:
            return result
    return None


def parse(xml_path: str) -> GmbrRecord:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    gmbr_el = _find_gmbr(root)
    if gmbr_el is None:
        raise ValueError(
            f"GenericMasterBatchRecordVO not found in {xml_path}. "
            "Ensure the file is a valid PAS-X GMBR export."
        )

    return GmbrRecord(
        custom_id=_text(gmbr_el, 'customId'),
        description=_text(gmbr_el, 'description'),
        material_name=_text(gmbr_el, 'materialName'),
        version_id=_text(gmbr_el, 'versionId'),
        current_status=_text(gmbr_el, 'currentStatus'),
        top_level_steps=_extract_steps(gmbr_el),
        top_level_links=_extract_links(gmbr_el),
    )
