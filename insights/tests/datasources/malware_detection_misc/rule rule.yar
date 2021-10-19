rule Rule
/*
   Strings to trigger matches in the tests/matching_entity and tests/another\ matching_entity files
   Output from this rule against those files should look like CONTRIVED_SCAN_OUTPUT in tests/test_parse_scan_output.py
   This file is also used in tests for testing rules files with spaces in them
*/
{
    meta:
        description = "Strings to trigger matches in the test/*matching_entity files"

    strings:
        $match0 = "string match in the file \"matching_entity\""
        $match1 = "another string match in matching_entity"
        $match2 = "string with different types of quotes 'here' and \"here\""
        $match3 = "string match containing error scanning but it's ok because its not in a rule line"

        $grep1 = "contains ="
        $grep2 = "contains .+"
        $grep3 = "contains \""
        $grep4 = "contains '"
        $grep5 = "contains ()[]"
        $grep6 = "contains {"
        $grep7 = "contains ^$"

    condition:
        any of them
}
