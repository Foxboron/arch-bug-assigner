#!/usr/bin/python

import re
import logging

from requests_toolbelt.multipart.encoder import MultipartEncoder

BUGTRACKER_TO_ARCHWEB = {
    "3548": "bluewind",
    "280": "pierre",
    "2008": "allan",
    "14279": "alucryd",
    "8499": "anatolik",
    "847": "andyrtr",
    "5403": "arojas",
    "15325": "demize",
    "9560": "dvzrv",
    "6879": "eworm",
    "11602": "felixonmars",
    "3741": "foutrelis",
    "5069": "heftig",
    "3799": "jelle",
    "179": "jgc",
    "600": "juergen",
    "4547": "lfleischer",
    "834": "ronald",
    "2264": "remy",
    "8269": "seblu",
    "162": "tpowa",
    "12692": "jleclanche",
    "20134": "ainola",
    "18684": "Alad",
    "10516": "andrewSC",
    "17958": "anthraxx",
    "20102": "Archange",
    "21106": "bastelfreak",
    "24008": "dbermond",
    "4483": "idevolder",
    "7923": "cesura",
    "8307": "bgyorgy",
    "27096": "coderobe",
    "3069": "cbehan",
    "14272": "daurnimator",
    "15325": "demize",
    "27897": "diabonas",
    "2904": "jlichtblau",
    "19965": "eschwartz",
    "25597": "escondida",
    "6879": "eworm",
    "18946": "farseerfc",
    "11602": "felixonmars",
    "27670": "FFY00",
    "25983": "Foxboron",
    "19564": "foxxx0",
    "21474": "freswa",
    "1901": "aginiewicz",
    "20907": "grazzolini",
    "22000": "hashworks",
    "3799": "jelle",
    "3039": "jsteel",
    "5323": "kkeen",
    "22733": "kgizdov",
    "22649": "kpcyrd",
    "4547": "lfleischer",
    "5366": "lcarlier",
    "26921": "maximbaz",
    "4050": "mtorromeo",
    "10649": "muflone",
    "23710": "NicoHood",
    "33432": "orhun",
    "19018": "polyzen",
    "33593": "raster",
    "9172": "rgacogne",
    "22783": "sangy",
    "3843": "schuay",
    "8269": "seblu",
    "1098": "spupykin",
    "16600": "shibumi",
    "4209": "svenstaro",
    "20791": "tensor5",
    "25875": "wild",
    "3712": "xyne",
    "4884": "arodseth",
    "19138": "yan12125",
}

ARCHWEB_TO_BUGTRACKER = {}

for k, v in BUGTRACKER_TO_ARCHWEB.items():
    ARCHWEB_TO_BUGTRACKER[v] = k


BUG_TASK_TYPE = {
        "Bug Report": "1",
        "Feature Request": "2",
        "Support Request": "3",
        "General Gripe": "4",
}

BUG_PROJECT_TYPE = {
        "All Projects": "0",
        "Arch Linux": "1",
        "AUR web interface": "2",
        "Pacman": "3",
        "Community Packages": "5",
        "Release Engineering": "6",
        "Keyring": "7",
        "Arch VM Images": "8",
}

BUG_CATEGORY_TYPE = {
        "Packages": "33",
        "Packages: Testing": "41",
        "Upstream Bugs": "42",
        "Packages: Multilib": "46",
        "Security": "54",
        "Reproducible Builds": "58",
}

BUG_STATUS_TYPE = {
        "Unconfirmed": "1",
        "Assigned": "3",
        "Researching": "4",
        "Waiting on Response": "5",
        "Requires Testing": "6",
        "Unassigned": "7",
}

BUG_SEVERITY_TYPE = {
        "Critical": "5",
        "High": "4",
        "Medium": "3",
        "Low": "2",
        "Very Low": "1",
}

BUG_PRIORITY_TYPE = {
        "Flash": "6",
        "Immediate": "5",
        "Urgent": "4",
        "High": "3",
        "Normal": "2",
        "Low": "1",
}

BUG_OPERATING_SYSTEM_TYPE = {
        "All": "16",
        "x86_64": "18",
}


class Bug(object):
    def __init__(self, session, bug):
        self.session = session
        self.url = 'https://bugs.archlinux.org/task/69474'

    def get_bugreport(self, url):
        soup = self.session.get_soup(url)
        body = soup.html.body
        mains = []
        for main in body.find(headers='assignedto').findAll('a'):
            mains.append(main['href'].split("/")[-1])
        ret = {
                'title': soup.html.title.text, 
                'maintainers': mains,
                'category': body.find(headers='category').text.split()[-1].replace('\\t',''),
            }
        ret["package"] = re.findall(r'\[(.+?)\]', ret["title"])
        soup.decompose()
        return ret

    def do(self, data):
        logging.basicConfig(level=logging.DEBUG)
        multipart_data = MultipartEncoder(data)
        self.session.opener.headers.update({'Content-Type': multipart_data.content_type})
        self.session.opener.post(self.url, data=multipart_data)

    def unassign_bug(self):
        data = [('old_assigned', (None, "25983")),
                ('item_summary', (None, "[go] Test bug")),
                ('action', (None, "details.update")),
                ('edit', (None, "1")),
                ('task_id', (None, "69474")),
                ('edit_start_time', (None, '1612048389')),
                ('project_id', (None, "5")),
                ('task_type', (None, "1")),
                ('product_category', (None, "33")),
                ('item_status', (None, "3")),
                ('old_assigned', (None, "")),
                ('find_user', (None, "")),
                ('operating_system', (None, "16")),
                ('task_severity', (None, "2")),
                ('task_priority', (None, "2")),
                ('reportedver', (None, "0")),
                ('closedby_version', (None, "0")),
                ('percent_complete', (None, "0")),
                ('detailed_desc', (None, "Go is totes broken. Please just use C for everything."))]
        self.do(data)

    def assign_bug(self):
        data = [('old_assigned', (None, "25983")),
                ('rassigned_to[]', (None, "25983")),
                ('item_summary', (None, "[go] Test bug")),
                ('action', (None, "details.update")),
                ('edit', (None, "1")),
                ('task_id', (None, "69474")),
                ('edit_start_time', (None, '1612048389')),
                ('project_id', (None, "5")),
                ('task_type', (None, "1")),
                ('product_category', (None, "33")),
                ('item_status', (None, "3")),
                ('old_assigned', (None, "")),
                ('find_user', (None, "")),
                ('operating_system', (None, "16")),
                ('task_severity', (None, "2")),
                ('task_priority', (None, "2")),
                ('reportedver', (None, "0")),
                ('closedby_version', (None, "0")),
                ('percent_complete', (None, "0")),
                ('detailed_desc', (None, "Go is totes broken. Please just use C for everything."))]
        self.do(data)
