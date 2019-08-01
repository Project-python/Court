import requests
import json
import mysql.connector

def zayavy(sud):
    url = "https://if.arbitr.gov.ua/new.php"
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,uk;q=0.2',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://if.arbitr.gov.ua/new.php',
        'Referer': 'https://if.arbitr.gov.ua/sud5010/gromadyanam/csz11/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }


    data = {'q_court_id': str(sud)}
    zapyt = requests.post(url, data, headers=headers)
    content = zapyt.content.decode('windows-1251')
    content_json = json.loads(content)
    try:
        all = []
        for i in content_json:
            tup = (i["date"], i["judge"], i["forma"], i["number"], i["involved"], i["description"], i["courtroom"], str(sud))
            all.append(tup)
        return (all)
    except:
        return ("null")

def sql_q(data):
    sql = ""
    nom = 0
    for key, value in data.items():
        if len(value) < 1:
            continue
        else:
            nom = nom + 1
            if key == "sud" and int(value[0]) == 0:
                if nom == 1:
                    sql = sql + "sud='{}' ".format(str(value[1:4]))
                else:
                    sql = sql + "AND sud='{}' ".format(str(value))
            else:
                if nom == 1:
                    #sql = sql + "{} LIKE '%{}%' ".format(str(key), str(value))
                    sql = sql + "{}='{}' ".format(str(key), str(value))
                else:
                    #sql = sql + "AND {} LIKE '%{}%' ".format(str(key), str(value))
                    sql = sql + "AND {}='{}' ".format(str(key), str(value))

    return("SELECT * FROM sz WHERE {}".format(sql))




def poshuk(data):
    mydb = mysql.connector.connect(
    host="mprojekt.mysql.pythonanywhere-services.com",
    user="mprojekt",
    passwd="19072019a",
    database="mprojekt$mpr")
    mycursor = mydb.cursor()
    sql = sql_q(data)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return (myresult)

t = {'sud': "", 'number': "344/8524/19"}
print(poshuk(t))







