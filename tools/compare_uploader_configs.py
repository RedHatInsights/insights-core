#!/usr/bin/env python
'''
Creates the "body" section of the *System Information Collected by Red
Hat Insight* document (https://access.redhat.com/articles/1598863/).
The intent is the output of this script can be simply copy/pasted into
the "body" section of the document with minimal changes.

The new files and removed files data is determined by comparing to the
currently published document.  The only expected manual change to the
text is the replacement of the "DATE" to reflect the date of the
previous publication.

Location of the uploader.json file in puppet source:
https://gitolite.corp.redhat.com/cgit/puppet-cfg/modules/pntcee.git/plain/files/uploader.json?h=devgssci
'''

import subprocess
import json
from jinja2 import Environment, FileSystemLoader
from operator import itemgetter
from os.path import realpath, dirname

import generate_api_config

TEMPLATE = 'bodytemplate.md'

def get_diff(current, latest):

    SECTIONS = ("files", "commands")

    def get_map(doc):
        maps = dict((sec, {}) for sec in SECTIONS)

        for section in maps.keys():
            mapping = maps[section]
            for item in doc[section]:
                cmd_or_file = item[section[:-1]]
                patterns = item["pattern"]
                mapping[cmd_or_file] = patterns

        return maps

    old = get_map(current)
    new = get_map(latest)

    section_map = dict((sec, {}) for sec in SECTIONS)

    for section in SECTIONS:
        old_ = old[section]
        new_ = new[section]

        all_ = set(old_.keys() + new_.keys())
        section_map[section] = groups = {
            "added": [],
            "removed": [],
            "changed": []
        }

        for k in all_:
            if k in old_ and k in new_ and old_[k] != new_[k]:
                groups["changed"].append(k)
            elif k in old_ and k not in new_:
                groups["removed"].append(k)
            elif k in new_ and k not in old_:
                groups["added"].append(k)

    return section_map


def create_doc(current, latest):
    doc = {"all_files": [],
           "all_commands": [],
           "command_patterns": {},
           "file_patterns": {},
           "added_files": [],
           "removed_files": [],
           "changed_files": [],
           "added_commands": [],
           "removed_commands": [],
           "changed_commands": []
    }

    for sec in ("file", "command"):
        for item in sorted(latest["%ss" % sec], key=itemgetter(sec)):
            if item["pattern"]:
                doc["%s_patterns" % sec][item[sec]] = item["pattern"]
            else:
                doc["all_%ss" % sec].append(item[sec])

    for section, groups in get_diff(current, latest).items():
            for group, iterable in groups.items():
                if iterable:
                    doc['%s_%s' % (group, section)] = iterable
    return doc


def render_markdown(document):
    current_dir = dirname(realpath(__file__))
    jinja_env = Environment(loader=FileSystemLoader(current_dir), trim_blocks=True, lstrip_blocks=True)
    template = jinja_env.get_template(TEMPLATE)
    print template.render(doc=document)


def markdown_encode_string(s):
    '''
    Covert any strings that will not render properly in markdown.

    Currently, we just replace newlines that occur in a command (e.g.,
    in the rpm formatting command) with blanks.
    '''
    encoded = s.replace('\n', '')
    return encoded

def markdown_encode(document):
    '''
    Covert the document content to properly render in markdown --- walk
    the document tree, encoding any string types.

    This function assumes the document structure consists of
    dictionaries that may contains strings or lists of strings.  In
    particular, it assumes that the lists do not contain dictionaries.
    '''
    for key, value in document.iteritems():
        if isinstance(value, basestring):
            document[key] = markdown_encode_string(value)
        elif isinstance(value, list):
            newvalue = []
            for s in value:
                newvalue.append(markdown_encode_string(s))
            document[key] = newvalue
        else:
            markdown_encode(value)
    return document

if __name__ == "__main__":
    current = json.loads(subprocess.check_output(
        "curl -s 'https://api.access.redhat.com/r/insights/v1/static/uploader.json'", shell=True))

    gen = generate_api_config.APIConfigGenerator()
    latest = gen.serialize_data_spec()
    doc = create_doc(current, latest)
    encoded_doc = markdown_encode(doc)
    render_markdown(encoded_doc)
