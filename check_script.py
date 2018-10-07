import os
import argparse
import re
import json
from typing import Pattern
from copy import deepcopy

tagname_regexp = re.compile("[\w\s]+")
alias_regexp: Pattern[str] = re.compile("~\[[\w\s]+\]")
entity_regexp = re.compile("@\[[\w\s]+\]")


def get_values_till_new_tag(ind, str_data_list):
    """
    Method return all inter-values till new alias\entity\intent flag are reached
    :param ind:
    :param str_data_list:
    :return:
    """
    result_list = []
    for i in range(ind + 1, len(str_data_list)):
        if str_data_list[i].startswith(" " * 4):
            result_list.append(str_data_list[i].lstrip())
        else:
            break
    return result_list


def parse_chatito_to_dict(input_path):
    global tagname_regexp
    intent_variations_dict = dict()
    alias_dict = dict()
    entity_dict = dict()
    with open(input_path) as f:
        cha_list = f.read().split('\n')
        for ind, row in enumerate(cha_list):
            if not row.startswith(' ' * 4):
                if row.startswith('%'):
                    intent_variations_dict[tagname_regexp.findall(row)[0]] = get_values_till_new_tag(ind, cha_list)
                elif row.startswith('~'):
                    alias_dict[tagname_regexp.findall(row)[0]] = get_values_till_new_tag(ind, cha_list)
                elif row.startswith("@"):
                    entity_dict[tagname_regexp.findall(row)[0]] = get_values_till_new_tag(ind, cha_list)
                else:
                    print("[WARNING] There are strange row: {0}".format(ind))

    return intent_variations_dict, alias_dict, entity_dict


def fill_references(value: str, al_refs: list, _alias_dict: dict):
    global tagname_regexp
    _result_value_list = []
    if len(al_refs) > 0:
        for al_val in _alias_dict[tagname_regexp.findall(al_refs[0])[0]]:
            _result_value_list.extend(
                fill_references(value.replace(al_refs[0], al_val), al_refs[1:], _alias_dict))
    else:
        _result_value_list.append(value)
    return _result_value_list


def fill_references_if_needed(values_list, _alias_dict):
    global alias_regexp
    result_list = []
    for value in values_list:
        al_refs = alias_regexp.findall(value)
        # print("ref_check: ", al_refs)
        if len(al_refs) > 0:
            result_list.extend(fill_references(value, al_refs, _alias_dict))
        else:
            result_list.append(value)
    return result_list


def fill_all_sub_aliases(_alias_dict):
    # key_list = list(_alias_dict.keys())
    for alias_key in _alias_dict:
        _alias_dict[alias_key] = fill_references_if_needed(_alias_dict[alias_key], _alias_dict)
    return _alias_dict


def is_alias_correct(_alias_dict):
    al_keys = list(_alias_dict.keys())
    return any([len(it) > 0 for it in
                [set(_alias_dict[al_keys[ind_1]]) & set(_alias_dict[al_keys[ind_2]])
                 for ind_1 in range(len(al_keys))
                 for ind_2 in range(ind_1 + 1, len(al_keys))]
                ])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Script that get .chatito script and warn about it`s all possible vulnerabilities')
    parser.add_argument('--input_path', type=str,
                        help='path to script or folder with scripts')
    parser.add_argument('--mode', help='script mode -- file or dir', choices=['file', 'dir'])

    args = parser.parse_args()
    # print(args.input_path, args.mode)
    int_var_dict, alias_dict, entity_dict = parse_chatito_to_dict(args.input_path)
    # print(json.dumps(alias_dict, indent=2))
    # alias_dict = fill_all_sub_aliases(deepcopy(alias_dict))
    # print(json.dumps(alias_dict, indent=2))
    # assert not is_alias_correct(alias_dict), ""
#     TODO inter-alias duplicating warn
#     TODO intent variations duplicating warn
#     TODO intent variations duplicating reason find allgorithm

