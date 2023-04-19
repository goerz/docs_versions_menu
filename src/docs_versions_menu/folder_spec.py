"""Parser for folder specifications."""
from collections import OrderedDict
from functools import partial

from pyparsing import (
    Forward,
    Group,
    Literal,
    Optional,
    ParseException,
    Word,
    ZeroOrMore,
    alphanums,
    delimitedList,
    nums,
    oneOf,
)

from .parse_version import parse_version


def _parse_folder_spec(spec, groups, sort_key):
    """Parse the folder specification into a nested list.

    Args:
        spec (str): folder specification
        groups (dict): map of group name to list of folders in group
        sort_key (callable): map of folder name to sortable object.

    Returns:
        list: list of parsed tokens

    Raises:
        ValueError: if `spec` cannot be parsed.
    """
    group_names = list(groups.keys())

    def convert_to_slice(parse_string, loc, tokens):
        """Convert SliceSpec tokens to slice instance."""
        parts = "".join(tokens[1:-1]).split(':')
        if len(parts) == 1:
            i = int(parts[0])
            if i == -1:
                return slice(i, None, None)
            else:
                return slice(i, i + 1, None)
        else:
            parts += [''] * (3 - len(parts))  # pad to length 3
            start, stop, step = (int(v) if len(v) > 0 else None for v in parts)
            return slice(start, stop, step)

    def convert_to_callable_filter(parse_string, loc, tokens):
        """Convert ConditionSpec to a callable filter.

        The returned filter takes a single argument `folder` and return True if
        the `folder` passes the filter.
        """
        op, arg = tokens[0], tokens[1]

        def _filter(folder, _op, _list):
            folder = parse_version(folder)
            _list = [parse_version(v) for v in _list]
            if _op == 'in':
                return folder in _list
            elif _op == 'not in':
                return folder not in _list
            elif _op == '<=':
                return all([folder <= v for v in _list])
            elif _op == '<':
                return all([folder < v for v in _list])
            elif _op == '==':
                return all([folder == v for v in _list])
            elif _op == '!=':
                return all([folder != v for v in _list])
            elif _op == '>=':
                return all([folder >= v for v in _list])
            elif _op == '>':
                return all([folder > v for v in _list])
            else:  # pragma: nocover
                raise ValueError("Unknown operator: %r" % _op)

        if isinstance(arg, str):
            _list = [arg]
        else:
            _list = _resolve_folder_spec(
                [arg.asList()], groups, sort_key=sort_key
            )
        return partial(_filter, _op=op, _list=_list)

    Int = Word(nums + "-", nums)
    Colon = Literal(':')

    SliceSpec = (
        "["
        + Optional(Int)
        + Optional(Colon + Optional(Int))
        + Optional(Colon + Optional(Int))
        + "]"
    ).setParseAction(convert_to_slice)

    LogicalOperator = (
        Literal('in')
        | Literal('not in')
        | Literal('<=')
        | Literal('<')
        | Literal('==')
        | Literal('!=')
        | Literal('>=')
        | Literal('>')
    )

    GroupName = Group("<" + oneOf(group_names, caseless=True) + ">")
    FolderName = Word(alphanums, alphanums + ".-_+")

    ParenthesizedListSpec = Forward()
    ConditionSpec = Forward()

    ParenthesizedListSpec <<= Group(
        "("
        + delimitedList(GroupName | FolderName | ParenthesizedListSpec)
        + ZeroOrMore(ConditionSpec)
        + ")"
        + Optional(SliceSpec)
    )

    ConditionSpec <<= LogicalOperator + (
        FolderName | GroupName | ParenthesizedListSpec
    )
    ConditionSpec = ConditionSpec.setParseAction(convert_to_callable_filter)

    ListSpec = delimitedList(GroupName | FolderName | ParenthesizedListSpec)

    Spec = ListSpec | ParenthesizedListSpec

    if spec.strip() == '':
        return []
    try:
        return Spec.parseString(spec, parseAll=True).asList()
    except ParseException as exc:
        raise ValueError(
            "Invalid specification (marked '*'): %r" % exc.markInputline('*')
        )


def resolve_folder_spec(spec, groups, *, sort_key=None):
    """Convert folder specification into list of folder names.

    Args:
        spec (str): folder specification
        groups (dict): map of group name to list of folders in group
        sort_key (None or callable): map of folder name to sortable object. If
            None, sorting will be done according to PEP440
    """
    if sort_key is None:
        sort_key = parse_version
    spec_list = _parse_folder_spec(spec, groups, sort_key=sort_key)
    return _resolve_folder_spec(spec_list, groups, sort_key)


def _resolve_folder_spec(spec_list, groups, sort_key):
    """Recursively implement :func:`resolve_folder_spec`.

    Compared to :func:`resolve_folder_spec`, this receives a list of parsed
    tokens `spec_list` (as returned by :func:`_parse_folder_spec`) instead of a
    single string `spec`.
    """
    folders = []
    for item in spec_list:
        if isinstance(item, str):
            if item in groups['all']:
                folders.append(item)
        elif isinstance(item, list):
            if item[0] == '<':
                existing = set(folders)
                name = item[1]
                for folder in sorted(groups[name], key=sort_key):
                    if folder not in existing:
                        folders.append(folder)
            elif item[0] == '(':
                if isinstance(item[-1], slice):
                    _slice = item[-1]
                    sub_specs = item[1:-2]
                    _sort_if_no_slice = lambda v: 0  # do not sort
                else:  # no slice
                    _slice = slice(None)
                    sub_specs = item[1:-1]
                    _sort_if_no_slice = sort_key
                filters = []
                while callable(sub_specs[-1]):
                    filters.append(sub_specs.pop())
                folders.extend(
                    sorted(
                        [
                            folder
                            for folder in _resolve_folder_spec(
                                sub_specs, groups, sort_key
                            )
                            if all(filter(folder) for filter in filters)
                        ],
                        key=_sort_if_no_slice,
                    )[_slice]
                )
        else:  # pragma: no cover
            # it should be impossible to get here, assuming a correct parser
            raise TypeError("Unexpected folder specification item: %r" % item)
    return list(OrderedDict.fromkeys(folders))  # remove duplicates
