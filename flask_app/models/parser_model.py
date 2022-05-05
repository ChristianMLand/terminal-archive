from abc import ABC,abstractstaticmethod

container_size_aliases = {
    "20" : ["20DR"],
    "Reefer" : ["20RFR", "40RFR"],
    "HT/OT" : ["Special"],
    "FR" : ["Special"],
    "OT" : ["Special"],
    "HT" : ["Special"],
}

#TODO write helper methods for getting container sizes and ssl_names in abc class
#TODO write helper method for getting availability type and storing in info_dict

class TerminalParser(ABC):
    @abstractstaticmethod
    def parse() -> dict:
        ...

    def get_parser(terminal_name) -> 'TerminalParser':
        terminals = {
            "t18" : T18Parser,
            "t30" : T30Parser,
            "t5" : T5Parser,
            "wut" : WUTParser,
            "husky" : HuskyParser
        }
        return terminals[terminal_name]()

class T18Parser(TerminalParser):
    @staticmethod
    def parse(soup):
        data = {}
        table = soup.find_all("table")[1]
        rows = table.find_all("tr")[1:14]
        container_sizes = [td.getText().split(" ")[0].replace("'","").strip() for td in table.tr.find_all("td")[1:]]
        ssl_names = [tr.td.getText().replace("YES","").strip() for tr in rows]
        for i, tr in enumerate(rows):
            info_dict = {}
            for j, td in enumerate(tr.find_all('td')[1:]):
                containers = [container_sizes[j]]
                if containers[0] in container_size_aliases:
                    containers = container_size_aliases[containers[0]]
                for container in containers:
                    if td.getText().strip() == "YES":
                        availability_type = "Pick" if j % 2 else "Drop"
                        for line in ssl_names[i].split('/'):
                            data[line] = info_dict
                        if container in info_dict:
                            info_dict[container].append(availability_type)
                        else:
                            info_dict[container] = [availability_type]
        return data

class T30Parser(TerminalParser):
    @staticmethod
    def parse(soup):
        #TODO build this 
        return {}

class T5Parser(TerminalParser):
    @staticmethod
    def parse(soup):
        data = {}
        tables = soup.find_all("table")
        container_sizes = [td.getText().strip() for td in tables[1].tr.find_all("td")[1:]]
        ssl_names = []
        for x, table in enumerate(tables[1:]):
            rows = table.find_all("tr")[1:]
            for tr in rows:
                line = tr.td.getText().strip()
                if line not in ssl_names:
                    ssl_names.append(line)
            for i, tr in enumerate(rows):
                info_dict = {}
                for j, td in enumerate(tr.find_all("td")[1:]):
                    container = container_sizes[j]
                    line = ssl_names[i]
                    if td.getText().strip() == "OPEN":
                        availability_type = "Pick" if x else "Drop"
                        if line not in data:
                            data[line] = info_dict
                        else:
                            info_dict = data[line]
                        if container in info_dict:
                            info_dict[container].append(availability_type)
                        else:
                            info_dict[container] = [availability_type]
        return data

class WUTParser(TerminalParser):
    @staticmethod
    def parse(soup):
        data = {}
        table = soup.find_all("table")[0].tbody
        rows = table.find_all("tr")[1:]
        container_sizes = [td.getText().replace("’ ","").replace("Pick Up", "").replace("Drop", "").strip() for td in table.tr.find_all("td")[1:]]
        ssl_names = [tr.td.getText().strip() for tr in rows]
        for i, tr in enumerate(rows):
            info_dict = {}
            for j, td in enumerate(tr.find_all("td")[1:]):
                containers = [container_sizes[j]]
                if containers[0] in container_size_aliases:
                    containers = container_size_aliases[containers[0]]
                for container in containers:
                    if td.getText().strip() == "YES":
                        availability_type = "Pick" if j % 2 else "Drop"
                        line = ssl_names[i]
                        data[line] = info_dict
                        if container in info_dict:
                            info_dict[container].append(availability_type)
                        else:
                            info_dict[container] = [availability_type]
        return data

class HuskyParser(TerminalParser):
    @staticmethod
    def parse(soup):
        data = {}
        table = soup.find_all("table")[2]
        rows = table.tbody.find_all("tr")
        container_sizes = [th.getText().replace("' ","").replace("Drop","").replace("Pick","").strip() for th in table.thead.tr.find_all("th")[2:]]
        ssl_names = [tr.find_all("td")[1].getText().strip() for tr in rows]
        for i, tr in enumerate(rows):
            info_dict = {}
            for j, td in enumerate(tr.find_all("td")[2:]):
                containers = [container_sizes[j]]
                if containers[0] in container_size_aliases:
                    containers = container_size_aliases[containers[0]]
                for container in containers:
                    if td.getText().strip() == "YES":
                        availability_type = "Pick" if j % 2 else "Drop"
                        line = ssl_names[i]
                        data[line] = info_dict
                        if container in info_dict:
                            info_dict[container].append(availability_type)
                        else:
                            info_dict[container] = [availability_type]
        return data