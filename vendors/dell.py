from vendors import *
import re
import logging
import urllib3
import datetime
import os
from collections import namedtuple
from BeautifulSoup import BeautifulSoup


handler = logging.StreamHandler()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


Bios = namedtuple('Bios', 'version url filename')


class DellBios(BiosUpdater):

    BIOS_BASE = "downloads.dell.com"
    BIOS_PATH = "/published/pages/%s.html"

    BIOS_URL_REGEX = re.compile(r"^/(.*?)\.(EXE|exe)")

    def __init__(self, params, target_path):
        self.target_dir = target_path
        if self.target_dir.endswith("/"):
            self.target_dir = self.target_dir[:-1]
        self.system_ids = params["system_ids"]
        self.folder_map = params["folder_map"]
        self.vendor_name = params["name"]

    def _get_bios_info(self, http_connection, system_id):
        response = http_connection.request(
            "GET", DellBios.BIOS_PATH % system_id)
        soup = BeautifulSoup(response.data)
        entries = soup.find("div", {"id": "Drivers-Category.BI-Type.BIOS"}
                            ).findAll("tr")
        bi = []
        for e in entries:
            b = e.find("a", href=DellBios.BIOS_URL_REGEX)
            if not b:
                continue
            version = str(e.findAll("td")[2].text).lower().strip()
            href = b["href"]
            if version == "":  # Fallback if version column on Dell page empty
                version = href[:href.rfind(".")]
                version = version[-3:].lower()
            filename = "%s-%s.exe" % (system_id, version)
            bi.append(Bios(version, href, filename))
        return bi

    def _loadBios(self, http, bios, folder, data, options, intermediate=False):
        # if not "bios" in data:
        #    data["bios"] = []
        d = {}
        file_name = "%s/%s/%s" % (self.target_dir, folder, bios.filename)
        fn = "%s/%s" % (folder, bios.filename)

        if not (os.path.exists(os.path.dirname(file_name))):
            os.mkdir(os.path.dirname(file_name))
        d["version"] = bios.version
        if not os.path.isfile(file_name):
            bios_file = http.request("GET", bios.url).data
            output = open(file_name, 'wb')
            output.write(bios_file)
            output.close()
            last_changed = datetime.datetime.now().strftime(
                "%d.%m.%Y %H:%M:%S")
            data["last_changed"] = last_changed
            updated = True
        else:
            if "last_changed" not in data:
                data["last_changed"] = "never"
            updated = False
        logger.info(
            "[%s/%s] %s" % ("RQ" if intermediate else "LA",
                            "DL" if updated else "OK", fn))

        d["file"] = fn
        if not intermediate:
            d["latest"] = True
        # if data["bios"]
        data["bios"].append(d)

    def update(self, data):
        # num_sys_ids = len(self.system_ids)
        http = urllib3.HTTPConnectionPool(
            DellBios.BIOS_BASE,
            timeout=urllib3.Timeout(read=20.0), retries=10)
        for sysid in self.system_ids:
            options = {}
            # if entry is not a simple name, but a dictionary
            if type(sysid) is not str:
                key = sysid.keys()[0]
                options = sysid[key]
		if options is None:
			logger.error("Config error at %s" % sysid)
			sys.exit(1)
                sysid = key
            try:
                bioses = self._get_bios_info(http, sysid)
            except Error as e:
                logger.warning("Issue at %s: %s" % sysid, str(e))
                continue

            folder = self._folder_for_sysid(sysid)
            if folder is not None:
                if sysid not in data:
                    data[sysid] = {}
                d = data[sysid]
                d["sysid"] = sysid
                d["bios"] = []
                # file manually downloaded
                if "unmanaged" in options:
                    for item in options["unmanaged"]:
                        try:
                            d["bios"].append(item)
                        except:
                            logger.warning(
                                "Issue reading unmanaged item %s"
                                % sysid)

                manual = False
                # Skip downloading files for entries with manual flag
                if "manual" in options and options["manual"]:
                    manual = True

                if "comment" in options:
                    d["comment"] = options["comment"]

                if "options" in options:
                    d.update(options["options"])

                # load required intermediate versions
                if "requires" in options:
                    if manual:
                        logger.warning(
                            "(%s) Manual + requires not "
                            "allowed together. Skipping..." % sysid)
                    else:
                        req = options["requires"]
                        if type(req) is str:
                            req = [req]
                        for r in req:
                            found = False
                            for b in bioses:
                                if b.version.lower() == r.strip().lower():
                                    self._loadBios(
                                        http, b, folder, d, options, True)
                                    found = True
                                    break
                            if not found:
                                logger.warning(
                                    "No server files for version"
                                    " %s found." % r)

                # load latest bios
                if not manual:
                    self._loadBios(http, bioses[0], folder, d, options)
                d["bios"] = sorted(
                    d["bios"],
                    key=lambda entry: entry["version"])

            else:
                fail("Folder for sys id %s does not exist in mapping" % sysid)

    def _folder_for_sysid(self, sysid):
        for m in self.folder_map:
            if sysid.startswith(m):
                return self.vendor_name + "/" + self.folder_map[m]
        return None
