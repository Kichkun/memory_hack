from flask import Flask, request, jsonify
from entities import GeneralEntity

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():

    default = 'Empty'
    firstName = request.form.get('firstName', default)
    middleName = request.form.get('middleName', default)
    lastName = request.form.get('lastName', default)
    dateOfBirth = request.form.get('dateOfBirth', default)

    file = request.files["file"]

    if bool(file.filename):
        file_bytes = file.read()
        with open(f"image.jpg","wb") as f:
            f.write(file_bytes)

    entity = GeneralEntity(**{
        "source_url" : "",
        "name" : firstName + " " + middleName + " " + lastName,
        "date" : dateOfBirth,
        "photo_path": "image.jpg"
        
    })

    return jsonify(entity)


if __name__ == "__main__":
    app.run()