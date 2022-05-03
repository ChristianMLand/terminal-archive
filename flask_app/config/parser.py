from sqlite3 import connect
import requests # not used just yet
from bs4 import BeautifulSoup
import xlsxwriter
from flask_app.config.mysqlconnection import connectToMySQL
import json

def filter_down_tag(tag):
    if tag.strong:
        tag = tag.strong
    if tag.span:
        tag = tag.span
    return tag

#TODO Rewrite all parsers to go straight to db format
'''
{
    "Line" : {
        "ContainerSize: ["Pick", "Drop"],
        "ContainerSize2: ["Pick"]
    },
    "Line2" : {
        "ContainerSize: [],
        "ContainerSize2: ["Pick", "Drop"]
    }
}
'''
def parse_t18_into_dict(soup):
    table = soup.find_all("table")[1]
    rows = table.find_all("tr")
    table_dict = {}
    for i, tr in enumerate(rows):
        if i < 14:# only parse data from the rows we care about
            tds = tr.find_all("td")
            row_data = []
            for j, td in enumerate(tds):
                td_str = ''
                if td.p:
                    p_list = []
                    for p in td.find_all("p"):
                        p = filter_down_tag(p)# catch inner tags if they exist and filter them out
                        p_str = p.decode_contents()
                        p_str = p_str.split("<")[0]
                        p_list.append(p_str)
                    td_str = ''.join(p_list)
                td = filter_down_tag(td)
                if td.span:
                    td = td.span
                if not td_str:
                    td_str = td.decode_contents()
                td_str = td_str.replace('\xa0', "").replace("\n", "").strip()# discard any uneccessary special characters
                if j == 0:
                    lines = td_str.split('/')
                    for line in lines:
                        table_dict[line] = row_data
                else:
                    row_data.append(td_str)
    return format_table_dict(table_dict)

def parse_t30_into_dict(soup):
    pass

def parse_t5_into_dict(soup):
    tables = soup.find_all("table")
    drop_types = []
    pick_types = []
    table_dict = {}
    for i, row in enumerate(tables[1].find_all("tr")):
        tds = row.find_all("td")
        if i == 0:
            for td in tds[1:]:
                drop_types.append(td.h2.decode_contents())
        else:
            data = {
                "Pick" : [],
                "Drop" : []
            }
            for j, td in enumerate(tds[1:]):
                td = filter_down_tag(td.h3)
                if td.decode_contents() == "OPEN":
                    data['Drop'].append(drop_types[j])
            line = filter_down_tag(tds[0].h2)
            table_dict[line.decode_contents()] = data
    for i, row in enumerate(tables[2].find_all("tr")):
        tds = row.find_all("td")
        if i == 0:
            for td in tds[1:]:
                pick_types.append(td.h2.decode_contents())
        else:
            for j, td in enumerate(tds[1:]):
                td = filter_down_tag(td.h3)
                if td.decode_contents() == "OPEN":
                    line = filter_down_tag(tds[0].h2)
                    table_dict[line.decode_contents()]["Pick"].append(pick_types[j])
    return table_dict

def parse_wut_into_dict(soup):
    table = soup.find_all("table")[0]
    rows = table.tbody.find_all("tr")
    table_dict = {}
    types_list = [td.decode_contents() for td in rows[0].find_all("td")[1:]]
    for row in rows[1:]:
        tds = row.find_all("td")
        line = tds[0].decode_contents().strip()
        table_dict[line] = {
            "Pick" : [],
            "Drop" : []
        }
        for i, td in enumerate(tds[1:]):
            if td.decode_contents().strip() == "YES":
                cont_type = types_list[i].replace("Drop","").replace("Pick Up", "").replace("\u2019 ", "").strip()
                if cont_type == "20":
                    cont_type = "20DR"
                if cont_type == "FR" or "OT" in cont_type:
                    cont_type = "Special"
                if cont_type == "Reefer":
                    table_dict[line]["Drop" if i % 2 == 0 else "Pick"].append("20RFR")
                    table_dict[line]["Drop" if i % 2 == 0 else "Pick"].append("40RFR")
                else:
                    table_dict[line]["Drop" if i % 2 == 0 else "Pick"].append(cont_type)
    return table_dict

#TODO figure out way to use same parser for husk and wut
def parse_husky_into_dict(soup):
    table = soup.find_all("table")[2]
    table_dict = {}
    types_list = [th.decode_contents() for th in table.thead.tr.find_all("th")[2:]]
    for row in table.tbody.find_all("tr"):
        tds = row.find_all("td")
        line = tds[1].decode_contents()
        table_dict[line] = {
            "Pick" : [],
            "Drop" : []
        }
        for i, td in enumerate(tds[2:]):
            if td.decode_contents().strip() == "YES":
                cont_type = types_list[i].replace("Drop","").replace("Pick","").replace("' ", "").strip()
                if cont_type == "20":
                    cont_type = "20DR"
                if cont_type == "FR" or "OT" in cont_type:
                    cont_type = "Special"
                if cont_type == "Reefer":
                    table_dict[line]["Drop" if i % 2 == 0 else "Pick"].append("20RFR")
                    table_dict[line]["Drop" if i % 2 == 0 else "Pick"].append("40RFR")
                else:
                    table_dict[line]["Drop" if i % 2 == 0 else "Pick"].append(cont_type)
    return table_dict

def format_table_dict(table_dict):
    new_table = {}
    line_types = None
    for i, line in enumerate(table_dict):
        row = table_dict[line]
        if i == 0:
            line_types = row
        else:
            new_table[line] = { "Pick" : [], "Drop" : [] }
            for j, val in enumerate(row):
                if val == "YES":
                    cont_type = line_types[j].split(" ")[0].replace("'", "")
                    if cont_type == "20":
                        cont_type = "20DR"
                    if cont_type == "Reefer":
                        new_table[line]["Drop" if j % 2 == 0 else "Pick"].append("20RFR")
                        new_table[line]["Drop" if j % 2 == 0 else "Pick"].append("40RFR")
                    else:
                        new_table[line]["Drop" if j % 2 == 0 else "Pick"].append(cont_type)
    return new_table

parsers = {
    "t18" : parse_t18_into_dict,
    "t30" : parse_t30_into_dict,
    "t5" : parse_t5_into_dict,
    "wut" : parse_wut_into_dict,
    "husky" : parse_husky_into_dict
}

def request_terminal(terminal):
    
    if terminal['auth_required']:
        with requests.session() as s:
            s.post(terminal['auth_url'], data={"j_username" : terminal['auth_email'], "j_password" : terminal['auth_password']})
            r = s.get(terminal['data_url'])
    else:
        r = requests.get(terminal['data_url'])
    soup = BeautifulSoup(r.content, "html.parser")
    parsed = parsers[terminal['name']](soup)

    # json_object = json.dumps(parsed, indent = 4)
    # # print(json_object)
    return parsed

def convertToDBFormat(data):
    output = {}
    for line in data:
        output[line] = {}
        for type in data[line]:
            for cont in data[line][type]:
                if cont in output[line]:
                    output[line][cont].append(type)
                else:
                    output[line][cont] = [type]
    return output

def update_db(terminal, data):
    connection = connectToMySQL("terminal_archive")
    query = "SELECT * FROM ssls;"
    ssls = connection.query_db(query)
    query = "SELECT * FROM containers;"
    containers = connection.query_db(query)

    query = '''
            INSERT INTO availabilities
            (terminal_id, ssl_id, container_id, type)
            VALUES
            (%(terminal_id)s, %(ssl_id)s, %(container_id)s, %(types)s);
            '''

    for line in data:
        availability = {"terminal_id" : terminal['id']}
        for ssl in ssls:
            if line == ssl['name']:
                availability['ssl_id'] = ssl['id']
        for cont in data[line]:
            for container in containers:
                if cont in container['size']:
                    availability['container_id'] = container['id']
                    availability['types'] = ','.join(data[line][cont])
            connection.query_db(query, availability)
    connection.connection.close()

def write_to_worksheet(worksheet, formatted_table):
    table_count = 0
    for i, line in enumerate(formatted_table):
        for j, key in enumerate(formatted_table[line]):
            worksheet.write(0, table_count * 2 + i + j, f"{line} {key}")
            for k, val in enumerate(formatted_table[line][key]):
                worksheet.write(k + 1, table_count * 2 + i + j, val)
        table_count += 1

def update_worksheet(table):#update to google doc later
    workbook = xlsxwriter.Workbook("output.xlsx")
    worksheet = workbook.add_worksheet("Pick and Drop")
    print(table)
    write_to_worksheet(worksheet, table)
    workbook.close()

def parse_terminal_and_update_DB(terminal):
    data = request_terminal(terminal)
    if data:
        data = convertToDBFormat(data)
        update_db(terminal, data)
        print(f"parsed {terminal['name']}")
    
def main():
    query = "SELECT * FROM terminals;"
    connection = connectToMySQL("terminal_archive")
    terminals = connection.query_db(query)
    connection.connection.close()

    for terminal in terminals:
        parse_terminal_and_update_DB(terminal)


if __name__ == "__main__":
    main()