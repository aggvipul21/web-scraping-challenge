from flask import Flask,render_template,redirect
import pymongo
import scrape_mars

app=Flask(__name__)

# Create connection variable
conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)

# Connect to a database. Will create one if not already available.
db = client.mars_db

@app.route('/')
def echo():
    mars=list(db.mars_data.find())
    #print("Hello")
    #print(mars)
    #print(mars[3]["MarsFact"])

    #print(mars[4]['HemisphereImage'][0])
    #print(mars.NewsTitle)
    return render_template("index.html",mars_dt=mars)

@app.route('/scrape')
def scrape():
    scrape_mars.scrape()

    # Redirect back to home page
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)