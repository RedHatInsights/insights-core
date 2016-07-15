from falafel.core.plugins import mapper

KEY_WORD_LINE_0 = ["Host", "Channel", "Id", "Lun"]
KEY_WORD_LINE_1 = ["Vendor", "Model", "Rev"]
KEY_WORD_LINE_2 = ["Type", "ANSI  SCSI revision"]

@mapper('scsi')
def get_scsi(context):
    """
    Get scsi info from /proc/scsi/scsi, return a array that contain all info from scsi
    Here is some example:
    Input:
    Host: scsi0 Channel: 03 Id: 00 Lun: 00
        Vendor: HP       Model: P420i            Rev: 3.54
        Type:   RAID                             ANSI  SCSI revision: 05

    Output:
    {
        "ansi__scsi_revision": "05",
        "vendor": "HP",
        "rev": "3.54",
        "Host": "scsi0",
        "Channel": "03",
        "model": "P420i",
        "type": "RAID",
        "Id": "00",
        "Lun": "00"
    }

    """
    result = []
    scsi_info = {}
    for line in context.content[1:]:
        if line.startswith("Host"):
            scsi_info = {}
            result.append(scsi_info)
            scsi_info.update(_get_line_dict(line, KEY_WORD_LINE_0))
        elif line.strip().startswith("Vendor"):
            scsi_info.update(_get_line_dict(line, KEY_WORD_LINE_1))
        elif line.strip().startswith("Type"):
            scsi_info.update(_get_line_dict(line, KEY_WORD_LINE_2))
    return result


def _get_line_dict(line, key_word):
    scsi_info = {}
    end = 0
    for i, word in enumerate(key_word):
        start = end if scsi_info else line.index(word)
        start += len(word) + 1
        end = line.index(key_word[i + 1]) if i<len(key_word) -1 else None
        scsi_info[word.lower().replace(" ", "_")] = line[start:end].strip()
    return scsi_info
