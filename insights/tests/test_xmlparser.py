# -*- coding: UTF-8 -*-
#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from insights.core import XMLParser
from insights.tests import context_wrap


class FakeXmlParserClass(XMLParser):
    def parse_dom(self):
        # default namespace
        xmlns = 'http://people.example.com'
        keyword = '*{%s}%s' % (xmlns, "neighbor[2]")
        tmo_dict = {}
        for n in self.dom.findall(keyword):
            tmo_dict = {n.get("name"): n.get("direction")}
        return tmo_dict

    @property
    def get_neighbors(self):
        return self.get_elements("./country/neighbor")


testdata = """
<?xml version="1.0"?>
<data xmlns:fictional="http://characters.example.com"
       xmlns="http://people.example.com">
    <country name="Liechtenstein">
        <rank updated="yes">2</rank>
        <year>2008</year>
        <gdppc>141100</gdppc>
        <neighbor name="Austria" direction="E"/>
        <neighbor name="Switzerland" direction="W"/>
    </country>
    <country name="Singapore">
        <rank updated="yes">5</rank>
        <year>2011</year>
        <gdppc>59900</gdppc>
        <neighbor name="Malaysia" direction="N"/>
    </country>
    <country name="Panama">
        <rank>68</rank>
        <year>2011</year>
        <gdppc>13600</gdppc>
        <neighbor name="Costa Rica" direction="W"/>
    </country>
</data>
""".strip()


def test_parse():
    ctx = context_wrap(testdata)
    xml = FakeXmlParserClass(ctx)
    assert xml.raw == testdata
    assert len(xml.get_neighbors) == 4
    assert xml.xmlns == "http://people.example.com"
    assert "Costa Rica" not in xml
    assert "Switzerland" in xml
    assert xml.get("Switzerland", "") == "W"
    assert len(xml.get_elements(".//year/..[@name='Singapore']")) == 1
    assert xml.get_elements(".//*[@name='Singapore']/year")[-1].text == '2011'
    assert xml.get_elements(".//neighbor[2]", xmlns="http://people.example.com")[0].get('name') == 'Switzerland'
