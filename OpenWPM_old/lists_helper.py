import json
import os
import xml.etree.ElementTree as ET
import sqlite3
import re
from urlparse import urlparse
import publicsuffix


#Lists folder location
base_folder = os.path.dirname(os.path.realpath(__file__))
resource_folder = os.path.join(base_folder, 'resources/')
#List Paths
chrome_path = os.path.join(resource_folder, 'transport_security_state_static.json')
certs_path = os.path.join(resource_folder, 'transport_security_state_static.certs')
suffix_path = os.path.join(resource_folder, 'effective_tld_names.txt')
everywhere_path = os.path.join(resource_folder, 'HTTPS_Everywhere_Rules/')
top_path = os.path.join(resource_folder, 'top_500_sites.txt')
top_10000_path = os.path.join(resource_folder, 'top_10000_sites.txt')
crawl_db = os.path.abspath(os.path.join(base_folder, '../crawl_db.sqlite'))
top_10000_header_path = os.path.abspath(os.path.join(resource_folder, 'top_10000_headers.sqlite'))
top_million_header_path = os.path.abspath(os.path.join(resource_folder, 'top_million_headers.sqlite'))
preloaded_hsts_header_path = os.path.abspath(os.path.join(resource_folder, 'preloaded_hsts_headers.sqlite'))


class ListHelper:
    def __init__(self):
        self.error = "\n\n\n\n**********ERROR***********\n\n\n\n\n\n\n"
        #These from entire preloaded list
        self.preloaded_list = {}
        self.preloaded_base_domains = {}
        self.pinsets = 0
        self.entries = 0
        self.base_domains = 0
        self.google_base_domains = 0

        #These are pinned
        self.pinned_list = {}
        self.pinned_base_domains_list = {}
        self.pinned_hsts_base_domains_list = {}
        self.entries_pinned = 0
        self.entries_pinned_google = 0
        self.entries_pinned_google_not_hsts = 0
        self.entries_pinned_hsts = 0
        self.pinned_base_domains = 0
        self.pinned_google_base_domains = 0
        self.pinned_not_google_base_domains = 0
        self.pinned_hsts_base_domains = 0

        #HSTS Values
        self.hsts_list = {}
        self.hsts_base_domains_list = {}
        self.entries_hsts = 0
        self.entries_hsts_google = 0
        self.hsts_base_domains = 0

        self.psl = publicsuffix.PublicSuffixList()
        self.suffix_list = {}
        self.everywhere_list = {}
        self.top_500 = {}
        self.top_10000 = {}
        self.top_10000_http_headers = {}
        self.top_10000_https_headers = {}
        self.preloaded_http_headers = {}
        self.preloaded_https_headers = {}
        self.crawl_list = {}
        self.base_folder = base_folder
        self.results_folder = os.path.join(base_folder, 'results/')

        #return paths
        self.top_million_header_path = top_million_header_path
        self.preloaded_hsts_header_path = preloaded_hsts_header_path
        self.certs_path = certs_path

    def parse_json(self, filename):
        """ Parse a JSON file
            First remove comments and then use the json module package
            Comments look like :
                // or /* ...  */ """

        # Regular expression for comments to keep initial json for preloaded list
        comment_re = re.compile(
            '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
            re.DOTALL | re.MULTILINE
        )

        with open(filename) as f:
            content = ''.join(f.readlines())

            ## Looking for comments
            match = comment_re.search(content)
            while match:
                # single line comment
                content = content[:match.start()] + content[match.end():]
                match = comment_re.search(content)

            # Return json file
            return json.loads(content)

    def get_hsts_list(self):
        if self.hsts_list == {}:
            self.get_preloaded_list()
        return self.hsts_list

    def get_preloaded_list(self, filename=None):
        if self.preloaded_list == {}:
            #chrome_data = open(chrome_path)
            #chrome_list = json.load(chrome_data)
            if filename:
                chrome_list = self.parse_json(filename)
            else:
                chrome_list = self.parse_json(chrome_path)
            #chrome_data.close()

            #The Chrome list is broken into two lists:
            #chrome_list['pinsets'] with attributes {name, static_spki_hashes[]}
            #chrome_list['entries'] with attributes {name, include_subdomains, mode, pins}
            # *only name is in every chrome_list['entries'], other 3 optional

            #Turn the json list into a dictionary by domain
            self.pinsets = len(chrome_list['pinsets'])

            self.entries = len(chrome_list['entries'])
            for site in chrome_list['entries']:
                #Handle Total
                self.preloaded_list[site['name']] = {}
                self.preloaded_list[site['name']]['include_subdomains'] = site.get('include_subdomains', False)
                self.preloaded_list[site['name']]['mode'] = site.get('mode', False)
                self.preloaded_list[site['name']]['pins'] = site.get('pins', False)
                base_domain = self.domain(site['name'])
                if not self.preloaded_base_domains.get(base_domain):
                    self.preloaded_base_domains[base_domain] = True
                    if site.get('pins') == 'google':
                            self.google_base_domains += 1
                #Handle Pinning
                if site.get('pins'):
                    self.pinned_list[site['name']] = {}
                    self.pinned_list[site['name']]['include_subdomains'] = site.get('include_subdomains', False)
                    self.pinned_list[site['name']]['mode'] = site.get('mode', False)
                    self.pinned_list[site['name']]['pins'] = site.get('pins', False)
                    if site.get('pins') == 'google':
                        self.entries_pinned_google += 1
                    base_domain = self.domain(site['name'])
                    if not self.pinned_base_domains_list.get(base_domain):
                        self.pinned_base_domains_list[base_domain] = True
                        if site.get('pins') == 'google':
                            self.pinned_google_base_domains += 1
                        else:
                            self.pinned_not_google_base_domains += 0
                    if site.get('mode'):
                        self.entries_pinned_hsts += 1
                        if site.get('pins') == 'google':
                            self.entries_hsts_google += 1
                        if not self.pinned_hsts_base_domains_list.get(base_domain):
                            self.pinned_hsts_base_domains_list[base_domain] = True
                    else:
                        if site.get('pins') == 'google':
                            self.entries_pinned_google_not_hsts += 1
                #Handle HSTS
                if site.get('mode'):
                    self.hsts_list[site['name']] = {}
                    self.hsts_list[site['name']]['include_subdomains'] = site.get('include_subdomains', False)
                    self.hsts_list[site['name']]['mode'] = site.get('mode', False)
                    self.hsts_list[site['name']]['pins'] = site.get('pins', False)
                    base_domain = self.domain(site['name'])
                    if not self.hsts_base_domains_list.get(base_domain):
                        self.hsts_base_domains_list[base_domain] = True

            #Set Values
            self.base_domains = len(self.preloaded_base_domains)
            self.entries_pinned = len(self.pinned_list)
            self.pinned_base_domains = len(self.pinned_base_domains_list)
            self.entries_hsts = len(self.hsts_list)
            self.hsts_base_domains = len(self.hsts_base_domains_list)
            self.pinned_hsts_base_domains = len(self.pinned_hsts_base_domains_list)
        return self.preloaded_list

    def get_public_suffix_list(self):
        if self.suffix_list == {}:
            #The suffix list is a list of the suffixes. Some lines are commented with '\\'.
            #Ignore those lines
            suffix_file = open(suffix_path, 'r')
            for line in suffix_file:
                if line[0:2] != '//':
                    self.suffix_list[line[0:-1]] = True
        return self.suffix_list

    def get_https_everywhere_list(self):
        if self.everywhere_list == {}:
            file_list = os.listdir(everywhere_path)
            for file in file_list:
                try:
                    tree = ET.parse(everywhere_path + file)
                    root = tree.getroot()
                    for target in root.findall('target'):
                        self.everywhere_list[target.get('host')] = True
                except ET.ParseError:
                    continue
        return self.everywhere_list

    def get_top_500(self):
        if self.top_500 == {}:
            top_file = open(top_path, 'r')
            for line in top_file:
                for item in line.split('\r'):
                    self.top_500[item] = True
        return self.top_500

    def get_top_10000(self):
        if self.top_10000 == {}:
            top_10000_file = open(top_10000_path, 'r')
            for line in top_10000_file:
                self.top_10000[line.strip()] = True
        return self.top_10000

    def get_crawl_list(self):
        if self.crawl_list == {}:
            conn = sqlite3.connect(crawl_db)
            c = conn.execute('SELECT crawl_url FROM Resource_Loads_Static')
            extension_data = c.fetchall()
            for row in extension_data:
                temp = row[0].lower().strip()
                if temp[-1:] != '/':
                    temp += '/'
                if not self.crawl_list.get(temp, False):
                    self.crawl_list[temp] = True

            dynamic = False
            if dynamic:
                c = conn.execute('SELECT crawl_url FROM Resource_Loads_Dynamic')
                extension_data2 = c.fetchall()
                for row in extension_data2:
                    temp = row[0].lower().strip()
                    if temp[-1:] == '/':
                        temp == temp[:-1]
                    if not self.crawl_list.get(temp, False):
                        self.crawl_list[temp] = True
        return self.crawl_list

    def get_headers(self, database_path, table_name):
        header_list = {}
        conn = sqlite3.connect(database_path)
        sql_statement = "SELECT url, https, status_code, status_text, " \
                        "sts, location, error, key_pin, cookies, key_pin_report_only FROM %s" % table_name
        c = conn.execute(sql_statement)
        data = c.fetchall()
        for row in data:
            header_list[row[0]] = {}
            header_list[row[0]]['https'] = row[1]
            header_list[row[0]]['status_code'] = row[2]
            header_list[row[0]]['status_text'] = row[3]
            header_list[row[0]]['sts'] = row[4]
            header_list[row[0]]['location'] = row[5]
            header_list[row[0]]['error'] = row[6]
            header_list[row[0]]['pin'] = row[7]
            header_list[row[0]]['set-cookie'] = row[8]
            header_list[row[0]]['public-key-pins-report-only'] = row[9]
        return header_list

#this is only because the preloaded headers do not include the public-key-pins-report-only option.
#I would need to re-pull this for those sites
    def get_headers_old(self, database_path, table_name):
        header_list = {}
        conn = sqlite3.connect(database_path)
        sql_statement = "SELECT url, https, status_code, status_text, " \
                        "sts, location, error, key_pin, cookies FROM %s" % table_name
        c = conn.execute(sql_statement)
        data = c.fetchall()
        for row in data:
            header_list[row[0]] = {}
            header_list[row[0]]['https'] = row[1]
            header_list[row[0]]['status_code'] = row[2]
            header_list[row[0]]['status_text'] = row[3]
            header_list[row[0]]['sts'] = row[4]
            header_list[row[0]]['location'] = row[5]
            header_list[row[0]]['error'] = row[6]
            header_list[row[0]]['pin'] = row[7]
            header_list[row[0]]['set-cookie'] = row[8]
            header_list[row[0]]['public-key-pins-report-only'] = False
        return header_list

    def get_top_million_http_headers(self):
        return self.get_headers(top_million_header_path, "HTTP_Headers")

    def get_top_million_https_headers(self):
        return self.get_headers(top_million_header_path, "HTTPS_Headers")

    def get_preloaded_http_headers(self):
        if self.preloaded_http_headers == {}:
            self.preloaded_http_headers = self.get_headers_old(preloaded_hsts_header_path, "HTTP_Headers")
        return self.preloaded_http_headers

    def get_preloaded_https_headers(self):
        if self.preloaded_https_headers == {}:
            self.preloaded_https_headers = self.get_headers_old(preloaded_hsts_header_path, "HTTPS_Headers")
        return self.preloaded_https_headers

    #already urlparsed link, path only
    def check_if_link(self, url):
        if '.' in url:
            end = url.rsplit(".", 1)[1]
            if end == "xpi" or end == "jpg" or end == "exe" or end == "zip" or end == "msi" or end == "png"\
                    or end == "gz" or end == "git" or end == "jz" or end == "txt":
                return False
            #elif end == "html" or end == "py" or end == "php" or end == "htm" or end == "jspa" or end == "jsp" \
            #        or end == "org" or end == "net" or end == "xhtml":
            #    return True
            #else:
            #    print(end)
        return True

    def check_common_domain(self, domain_url, resource_url=None):
        if resource_url is None:
            first_domain = self.domain(domain_url[0])
            second_domain = self.domain(domain_url[1])
        else:
            first_domain = self.domain(domain_url)
            second_domain = self.domain(resource_url)
        if (first_domain is not None) and (first_domain == second_domain):
            return True
        else:
            return False

    def check_if_in_preloaded_list(self, url):
        #First check exact domain
        if self.preloaded_list == {}:
            self.get_preloaded_list()
        #Done checking original domain, now check subdomains
        if self.preloaded_list.get(url, False):
            return ['Domain', url]
        temp_url = url
        subdomain = True
        while subdomain:
            if '.' in temp_url:
                temp_url = temp_url.split('.', 1)[1]
                if (temp_url == 'com') or (temp_url == 'net') or (temp_url == 'org'):
                    #Break while because simply an ending
                    subdomain = False
                else:
                    if self.preloaded_list.get(temp_url, False):
                        return ['SubDomain', temp_url]
            else:
                #Break while because no more subdomains ('.').
                subdomain = False
        #Check if shares a base domain
        if self.preloaded_base_domains.get(self.domain(url), False):
            return ['BaseDomain', self.domain(url)]
        else:
            return ["Not in List", url]

    def check_https_everywhere_list(self, url):
        if self.everywhere_list == {}:
            self.get_https_everywhere_list()
        if self.everywhere_list.get(url, False):
            return True
        temp_url = url
        domain_remaining = True
        while domain_remaining:
            if '.' in temp_url:
                temp_url = temp_url.split('.', 1)[1]
                if self.everywhere_list.get('*.' + temp_url, False):
                    return True
            else:
                #Break while because no more subdomains ('.').
                domain_remaining = False
        return False

    def url_format(self, url):
        if url[-1:] != '/':
            return url + '/'
        return url

    def my_parse(self, url):
        temp_url = url.lower().strip()
        if temp_url[-1:] != '/':
            temp_url += '/'
        return urlparse(temp_url)

    def domain(self, url):
        #This returns TLD + 1 if exists, else the
        return self.psl.get_public_suffix(url)

    def output_preloaded_test_sites_list(self):
        if self.preloaded_list == {}:
            self.get_preloaded_list()
        f = open(os.path.abspath(os.path.join(base_folder, '../preloaded_site_list')), 'w')
        for domain in sorted(self.preloaded_list.iteritems(), reverse=True):
            f.write(domain[0] + '\n')
        f.close()

    #Quick output of all sites in list for testing
    def output_logged_test_sites_list(self):
        f = open(os.path.abspath(os.path.join(base_folder, '../preloaded_not_logged_site_list')), 'w')
        f2 = open(os.path.abspath(os.path.join(base_folder, '../preloaded_logged_site_list')), 'w')
        for domain, value in sorted(self.preloaded_list.items()):
            if not value['pins'] or value['pins'].startswith("tor") or value['pins'].startswith("crypt") \
                    or value['pins'].startswith("lava"):
                f.write(domain + '\n')
            else:
                f2.write(domain + '\n')
        f.close()
        f2.close()
        print("done outputing sites")

    def output_google_test_sites(self):
        f = open(os.path.abspath(os.path.join(base_folder, '../preloaded_google_site_list')), 'w')
        for domain, value in sorted(self.preloaded_list.iteritems()):
            if value['pins'] and value['pins'] == 'google':
                if not domain.startswith('google.'):
                    print(value['pins'], domain)
                    f.write(domain + '\n')
        f.close()

    def get_certs_dict(self):
        f = open(certs_path + 'parsed', 'r')
        certs_dict = dict()
        name = ""
        for line in f:
            if line[0:3] == 'sha':
                certs_dict[name] = line[5:].strip()
            else:
                name = line.strip()
        return certs_dict

    def get_hash_dict(self, sha_256 = False):
        f = open(certs_path + 'parsed', 'r')
        hash_dict = dict()
        name = ""
        for line in f:
            if line[0:4] == 'sha1':
                hash_dict[line[5:].strip()] = dict()
                hash_dict[line[5:].strip()]['name'] = name
                hash_dict[line[5:].strip()]['match'] = False
            elif sha_256 and line[0:4] == 'sha2':
                hash_dict[line[5:].strip()] = dict()
                hash_dict[line[5:].strip()]['name'] = name
                hash_dict[line[5:].strip()]['match'] = False
            else:
                name = line.strip()
        return hash_dict

    #This method is the initial testing method (compares the values)
    def test(self, output_string, expected_output_string, input_value, index):
        if output_string == expected_output_string:
            print(index),
            print("P,"),
        else:
            print('\n'),
            print(index),
            print(input_value),
            print(". should be :"),
            print(expected_output_string),
            print(". but instead is: "),
            print(output_string),
            print(".")

    #More general testing (opens test file and runs each line as a test)
    def run_test(self, test_list, test_function):
        test_f = open(test_list, 'r')
        index = 0
        for line in test_f:
            if line[0:2] != '//':
                temp = line.rstrip().rsplit(', ', 1)
                if temp[1] == 'None':
                    temp[1] = None
                elif temp[1] == 'True':
                    temp[1] = True
                elif temp[1] == 'False':
                    temp[1] = False
                #handle if input is an array
                if ', ' in temp[0]:
                    temp[0] = temp[0].split(', ')
                self.test(test_function(temp[0]), temp[1], temp[0], index)
                index += 1

    #The tests for common domain, everywhere, etc.
    def generalized_testing(self):
        test_folder = os.path.join(resource_folder, 'testing/')
        domain_test_list = os.path.join(test_folder, 'domain_test_list.txt')
        common_domain_test_list = os.path.join(test_folder, 'common_domain_test_list.txt')
        everywhere_test_list = os.path.join(test_folder, 'everywhere_test_list.txt')
        self.get_preloaded_list()
        psl = self.get_public_suffix
        self.run_test(domain_test_list, psl)
        self.run_test(domain_test_list, self.domain)
        print("\nrunning test2")
        self.run_test(common_domain_test_list, self.check_common_domain)
        print("\nrunning test3")
        self.run_test(everywhere_test_list, self.check_https_everywhere_list2)
        self.get_crawl_list()


if __name__ == "__main__":
    LH = ListHelper()
    LH.get_preloaded_list()
    #LH.output_preloaded_test_sites_list()
    #LH.output_logged_test_sites_list()