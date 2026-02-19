from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "POST":
        data = request.form["data"]
        return f"<h1>SAR Report:</h1><p>{data}</p>"

    return '''
    <h1>SAR Narrative Generator</h1>
    <form method="post">
    Enter Transaction:
    <input name="data">
    <input type="submit">
    </form>
    '''

app.run(debug=True)
