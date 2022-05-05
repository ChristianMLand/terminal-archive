from random import choice
import xlsxwriter
# import json

def generate_password():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$-"
    gen_pass = ""
    while len(gen_pass) < 8:
        gen_pass += choice(characters)
    return gen_pass

def write_to_worksheet(data):
    workbook = xlsxwriter.Workbook("flask_app/static/output.xlsx")
    worksheet = workbook.add_worksheet("Search Results")
    border = workbook.add_format({"border" : 1, "align" : "center"})
    gray = workbook.add_format({
        "border" : 1,
        "align" : "center",
        "bg_color" : "gray",
        "font_color" : "white"
    })
    row = {
        "Terminal" : None,
        "SSL" : None,
        "Container Size" : None,
        "Available During" : None,
        "Available For" : None
    }
    for i, key in enumerate(row):
        worksheet.write(0, i, key, gray)
    for i, availability in enumerate(data):
        row['Terminal'] = availability.terminal
        row['SSL'] = availability.ssl
        row['Container Size'] = availability.container
        row['Available During'] = availability.created_at
        row['Available For'] = availability.type
        for j, key in enumerate(row):
            value = str(row[key])
            worksheet.write(i+1, j, value)
            worksheet.set_column(j, j, len(value) + 10, border)
    workbook.close()