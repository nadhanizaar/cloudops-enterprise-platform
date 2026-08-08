from flask import Flask, render_template, request, redirect
import pymysql

app = Flask(__name__)

# RDS MySQL Database Connection
db = pymysql.connect(
    host="cloudops-db.cbg8geakmi9v.eu-north-1.rds.amazonaws.com",
    user="admin",
    password="fAcbih-wuqmig-5rohmi",
    database="cloudops"
)


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Test RDS database connection
@app.route("/db-test")
def db_test():
    cursor = db.cursor()
    cursor.execute("SELECT DATABASE();")
    result = cursor.fetchone()
    cursor.close()

    return f"Connected to database: {result[0]}"


# Display all deployments
@app.route("/deployments")
def deployments():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM deployments")
    deployments_data = cursor.fetchall()
    cursor.close()

    return render_template(
        "deployments.html",
        deployments=deployments_data
    )


# View a single deployment
@app.route("/deployments/<int:id>")
def view_deployment(id):
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM deployments WHERE id=%s",
        (id,)
    )

    deployment = cursor.fetchone()
    cursor.close()

    if deployment is None:
        return "Deployment not found", 404

    return f"""
    <h1>Deployment Details</h1>
    <p><strong>ID:</strong> {deployment[0]}</p>
    <p><strong>Project Name:</strong> {deployment[1]}</p>
    <p><strong>Environment:</strong> {deployment[2]}</p>
    <p><strong>Status:</strong> {deployment[3]}</p>
    <br>
    <a href="/deployments">← Back to Deployments</a>
    """


# Add new deployment
@app.route("/add-deployment", methods=["POST"])
def add_deployment():
    project_name = request.form["project_name"]
    environment = request.form["environment"]
    status = request.form["status"]

    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO deployments
        (project_name, environment, status)
        VALUES (%s, %s, %s)
        """,
        (project_name, environment, status)
    )

    db.commit()
    cursor.close()

    return redirect("/deployments")


# Delete deployment
@app.route("/delete-deployment/<int:id>")
def delete_deployment(id):
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM deployments WHERE id=%s",
        (id,)
    )

    db.commit()
    cursor.close()

    return redirect("/deployments")


# Update deployment status
@app.route("/update-status/<int:id>", methods=["POST"])
def update_status(id):
    new_status = request.form["status"]

    cursor = db.cursor()

    cursor.execute(
        "UPDATE deployments SET status=%s WHERE id=%s",
        (new_status, id)
    )

    db.commit()
    cursor.close()

    return redirect("/deployments")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )
