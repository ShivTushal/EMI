from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'GOODGOD97'  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'emi_project'  # Replace with your database name

mysql = MySQL(app)

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        name = request.form.get("name", "")
        return redirect(url_for('calculation', name=name))
    return render_template("home.html")

# Route for the EMI calculation
@app.route('/calculation/<name>', methods=['GET', 'POST'])
def calculation(name):
    if request.method == "POST":
        # Get form data
        obj = request.form.get("Object", "")  # Default to empty string if not provided
        principal = float(request.form.get("principal", 0))
        percentage=request.form["rate"]
        rate = float(request.form.get("rate", 0)) / 12 / 100  # Convert to monthly rate
        tenure_years = int(request.form.get("tenure_years", 0))
        tenure_months = int(request.form.get("tenure_months", 0))
        
        # Calculate total tenure in months
        total_months = (tenure_years * 12) + tenure_months
        
        # EMI calculation formula
        if rate == 0:
            emi = principal / total_months if total_months > 0 else 0
        else:
            emi = (principal * rate * (1 + rate) ** total_months) / ((1 + rate) ** total_months - 1)
        
        # Insert data into MySQL database
        cur = mysql.connection.cursor()
        if obj:  # If 'obj' is provided
            cur.execute("INSERT INTO MEMBERS (OBJECT, AMOUNT, RATE, YEARS, MONTHS, EMI, NAMES) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (obj, principal, percentage, tenure_years, tenure_months, emi, name))
        else:  # If 'obj' is not provided
            cur.execute("INSERT INTO MEMBERS (OBJECT, AMOUNT, RATE, YEARS, MONTHS, EMI, NAMES) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        ("no_name", principal, percentage, tenure_years, tenure_months, emi, name))
        
        mysql.connection.commit()
        cur.close()

        # Render calculation result
        return render_template('calculation.html', emi=emi, name=name)
    
    # Render calculation page without result if GET request
    return render_template('calculation.html', emi=None, name=name)

# Route for the history page
@app.route('/history/<name>')
def history(name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM MEMBERS WHERE NAMES = %s;", (name,))
    details = cur.fetchall()
    cur.close()
    return render_template("history.html", details=details,name=name)

if __name__ == '__main__':
    app.run(debug=True)
