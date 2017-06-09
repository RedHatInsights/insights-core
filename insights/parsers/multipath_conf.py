from insights.contrib import pyparsing as p
from .. import parser


def create_parser():
    """
    Need to check the specific symbol "/" in attr_value part as well.
    I checked some multipath configuraion files from the sosreport and got
    although there are some more specific symbols like "-%", it is enclosed
    in double quotes and will be accepted. Furthermore, I also checked the
    source code of "device-parser-multipath" and got if the attr_value in
    "multipath.conf" include a "whitespace", it must be enclosed in double
    quotation marks. So, we could just add one more specific symbol "/" to
    check.
    ----------------------------------------------------------
    udev_dir                /dev
    getuid_callout          "/sbin/scsi_id -g -u -s /block/%n"
    ----------------------------------------------------------
    """
    section_name = p.Word(p.alphas + "_")
    attr_name = attr_value = p.Word(p.alphanums + "_/")
    LBRACE, RBRACE = map(p.Suppress, "{}")
    attr = p.Group(attr_name + (attr_value | p.quotedString.setParseAction(p.removeQuotes)))
    attr_list = p.Dict(p.ZeroOrMore(attr))
    simple_section = p.Group(section_name + LBRACE + attr_list + RBRACE)
    complex_section = p.Group(section_name + LBRACE + p.OneOrMore(simple_section) + RBRACE)
    simple_or_complex = p.Dict(simple_section | complex_section)
    my_conf = p.Group(p.ZeroOrMore(simple_or_complex))
    my_conf.ignore("#" + p.restOfLine)
    return my_conf


@parser("multipath.conf")
def multipath(context):
    """
    Return a dict where the keys are the name of sections in multipath
    configuraion file.  If there are subsections, the value is a list of
    dictionaries with parameters as key and value.  Otherwise the value is just
    a single dictionary.

    Configuration File Example::

        defaults {
               path_selector           "round-robin 0"
               user_friendly_names      yes
        }

        multipaths {
               multipath {
                       alias                   yellow
                       path_grouping_policy    multibus
              }
               multipath {
                       wwid                    1DEC_____321816758474
                       alias                   red
              }
        }

        devices {
               device {
                       path_selector           "round-robin 0"
                       no_path_retry            queue
              }
               device {
                       vendor                  1DEC_____321816758474
                       path_grouping_policy    red
              }
        }

        blacklist {
              wwid 26353900f02796769
              devnode "^hd[a-z]"
        }

    Parse Result::

        {
          "blacklist": {
            "devnode": "^hd[a-z]",
            "wwid": "26353900f02796769"
          },
          "devices": [
            {
              "path_selector": "round-robin 0",
              "no_path_retry": "queue"
            },
            {
              "path_grouping_policy": "red",
              "vendor": "1DEC_____321816758474"
            }
          ],
          "defaults": {
            "path_selector": "round-robin 0",
            "user_friendly_names": "yes"
          },
          "multipaths": [
            {
              "alias": "yellow",
              "path_grouping_policy": "multibus"
            },
            {
              "alias": "red",
              "wwid": "1DEC_____321816758474"
            }
          ]
        }
    """
    return create_parser().parseString("\n".join(context.content))[0].asDict()
