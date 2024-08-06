import psycopg2
from bs4 import BeautifulSoup
import requests
import re
from sklearn.tree import DecisionTreeRegressor

def fetch_data_from_web():
    response = requests.get('https://www.scrapethissite.com/pages/simple/')
    soup = BeautifulSoup(response.text, 'html.parser')
    targets = soup.find_all('div', attrs={'class': 'country'})
    return targets

def parse_country_data(targets):
    country_data = []
    for target in targets:
        c_data = re.sub(r'[\s,\']+|[Capital,Population,Area (km2)]+:', ' ', target.text).strip().split('   ')
        country_data.append((c_data[0], c_data[1], int(c_data[2]), float(c_data[3])))
    return country_data

def insert_data_into_db(country_data):
    cnx = psycopg2.connect(
        database="Learn-ap", user="STU", password="1234", host="localhost", port=5432
    )
    cursor = cnx.cursor()
    for data in country_data:
        cursor.execute(
            "INSERT INTO countries (country_name, capital, population, area) VALUES (%s, %s, %s, %s);",
            data
        )
        cnx.commit()
    cursor.close()
    cnx.close()

def fetch_data_from_db():
    cnx = psycopg2.connect(
        database="Learn-ap", user="STU", password="1234", host="localhost", port=5432
    )
    cursor = cnx.cursor()
    cursor.execute('SELECT * FROM countries')
    cnx.commit()
    countries = cursor.fetchall()
    cursor.close()
    cnx.close()
    return countries

def prepare_data_for_model(countries):
    x = []
    y = []
    for country in countries:
        x.append([float(country[2])])
        y.append(float(country[3]))
    return x, y

def train_model(x, y):
    regressor = DecisionTreeRegressor()
    regressor = regressor.fit(x, y)
    return regressor

def predict_new_data(model, new_data):
    data = []
    prediction = model.predict(new_data)
    for i in prediction:
        data.append(int(i))
    return data

# Main execution
targets = fetch_data_from_web()
country_data = parse_country_data(targets)
insert_data_into_db(country_data)
countries = fetch_data_from_db()
x, y = prepare_data_for_model(countries)
model = train_model(x, y)
new_data = [[456682000],[90000000],[1282550]]
prediction = predict_new_data(model, new_data)

print("inputs",new_data)
print("results",prediction)
