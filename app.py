from flask import Flask, request, jsonify
import numpy as np
from sentence_transformers import SentenceTransformer
import joblib
import pandas as pd


# New changes 


# Load the models from the files
loaded_lr_model = joblib.load('./model/lr_model.joblib')
loaded_pca = joblib.load('./model/pca.joblib')
loaded_scaler = joblib.load('./model/scaler.joblib')

# Initialize the SentenceTransformer model
model = SentenceTransformer('flax-sentence-embeddings/all_datasets_v4_MiniLM-L6')

# Create a function for prediction
def predict_price(input_data, lr_model, pca, scaler):
    # Prepare the input data
    text_columns = [
        'Package Name', 'Destination', 'Itinerary', 'Places Covered',
        'Hotel Details', 'Airline', 'Sightseeing Places Covered', 'Cancellation Rules'
    ]

    # Initialize an empty DataFrame
    df = pd.DataFrame([input_data])

    # Encode text-based columns and create embeddings
    for column in text_columns:
        df[column + '_embedding'] = df[column].apply(lambda text: model.encode(text))

    # Apply PCA separately to each text embedding column
    n_components = 23  # Adjust the number of components as needed
    text_embeddings_pca = np.empty((len(df), n_components * len(text_columns)))

    for i, column in enumerate(text_columns):
        embeddings = df[column + '_embedding'].values.tolist()
        embeddings_pca = pca.transform(embeddings)
        text_embeddings_pca[:, i * n_components:(i + 1) * n_components] = embeddings_pca

    # Combine text embeddings with other numerical features if available
    numerical_features = [
        'Package Type_Standard', 'Package Type_Premium', 'Package Type_Luxury',
        'Travel_Month', 'Package Type_Budget', 'Package Type_Deluxe',
        'Hotel Ratings', 'Start City_New Delhi', 'Start City_Mumbai',
        'Travel_DayOfWeek', 'Travel_Year'
    ]

    X_numerical = df[numerical_features].values

    # Combine PCA-transformed text embeddings and numerical features
    X = np.hstack((text_embeddings_pca, X_numerical))

    # Scale the data using the same scaler used during training
    X = scaler.transform(X)

    # Make predictions using the trained Linear Regression model
    y_pred = lr_model.predict(X)

    return y_pred[0]



app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def predict():
    return """

    <!DOCTYPE html>
<html>
<head>
    <title>Travel Package Prediction</title>
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background-color: #f9f9f9;
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        h1 {
            color: #007BFF;
            font-size: 36px;
            margin-bottom: 20px;
        }

        form {
            text-align: left;
        }

        input[type="text"],
        input[type="number"] {
            width: 100%;
            padding: 15px;
            margin: 15px 0;
            border: none;
            border-bottom: 2px solid #007BFF;
            font-size: 18px;
            background-color: transparent;
            color: #333;
            transition: border-bottom 0.3s ease;
        }

        input[type="text"]:focus,
        input[type="number"]:focus {
            border-bottom: 2px solid #0056b3;
            outline: none;
        }

        input[type="checkbox"],
        input[type="radio"] {
            margin-right: 10px;
        }

        input[type="submit"] {
            background-color: #007BFF;
            color: #fff;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 20px;
            transition: background-color 0.3s ease;
        }

        input[type="submit"]:hover {
            background-color: #0056b3;
        }

        p#prediction {
            margin-top: 20px;
            font-size: 24px;
            color: #007BFF;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Travel Package Prediction</h1>
        <form action="/predict" method="POST">
            <label for="Package Name">Package Name:</label>
            <input type="text" name="Package Name" placeholder="Custom Package" value="A Grand Week in North East - Lachung Special">

            <label for="Destination">Destination:</label>
            <input type="text" name="Destination" placeholder="Custom Destination" value="Gangtok|Lachung|Gangtok|Darjeeling">

            <label for="Itinerary">Itinerary:</label>
            <input type="text" name="Itinerary" placeholder="Custom Itinerary" value="2N Gangtok . 2N Lachung . 1N Gangtok . 2N Darjeeling">

            <label for="Places Covered">Places Covered:</label>
            <input type="text" name="Places Covered" placeholder="Custom Places" value="Gangtok|Lachung|Gangtok|Darjeeling">

            <label for="Hotel Details">Hotel Details:</label>
            <input type="text" name="Hotel Details" placeholder="Custom Hotel Details" value="Lemon Tree Hotel  Gangtok:4.2|Summit Alpine Resort, Lachung- MMT Holidays Special:4.2|Lemon Tree Hotel  Gangtok:4.4|Ramada by Wyndham Darjeeling Gandhi Road:">

            <label for="Airline">Airline:</label>
            <input type="text" name="Airline" placeholder="Custom Airline" value="Air India|IndiGo">

            <label for="Sightseeing Places Covered">Sightseeing Places Covered:</label>
            <input type="text" name="Sightseeing Places Covered" placeholder="Custom Sightseeing" value="Baba Mandir | MG Road - Walk | Visit to Lake Tsomgo with Yak Safari | Snacks at Changu lake (Winter Special) | Yumthang Valley | Hot Spring">

            <label for="Cancellation Rules">Cancellation Rules:</label>
            <input type="text" name="Cancellation Rules" placeholder="Custom Cancellation Rules" value="Not Available">


            <label for="Package Type_Standard">Package Type_Standard:</label>
            <input type="checkbox" name="Package Type_Standard" value="1" checked>

            <label for="Package Type_Premium">Package Type_Premium:</label>
            <input type="checkbox" name="Package Type_Premium" value="1">

            <label for="Package Type_Luxury">Package Type_Luxury:</label>
            <input type="checkbox" name="Package Type_Luxury" value="1">

            <label for="Travel_Month">Travel Month:</label>
            <input type="number" name="Travel_Month" min="1" max="12" placeholder="Travel Month" value="5">

            <label for="Package Type_Budget">Package Type_Budget:</label>
            <input type="checkbox" name="Package Type_Budget" value="1">

            <label for="Package Type_Deluxe">Package Type_Deluxe:</label>
            <input type="checkbox" name="Package Type_Deluxe" value="1">

            <label for="Hotel Ratings">Hotel Ratings:</label>
            <input type="number" name="Hotel Ratings" placeholder="Hotel Ratings" value="4.5">

            <label for="Start City_New Delhi">Start City_New Delhi:</label>
            <input type="checkbox" name="Start City_New Delhi" value="1">

            <label for="Start City_Mumbai">Start City_Mumbai:</label>
            <input type="checkbox" name="Start City_Mumbai" value="1">

            <label for="Travel_DayOfWeek">Travel Day of Week:</label>
            <input type="number" name="Travel_DayOfWeek" min="0" max="6" placeholder="Travel Day of Week" value="2">

            <label for="Travel_Year">Travel Year:</label>
            <input type="number" name="Travel_Year" min="2023" max="2123" placeholder="Travel Year" value="2023">

            <input type="submit" value="Predict">
        </form>
        <p id="prediction"></p>
    </div>
</body>
</html>


    """


@app.route('/predict', methods=['POST'])
def index():
    if request.method == 'POST':
        # Get input data from the form
        package_name = request.form.get('Package Name')
        destination = request.form.get('Destination')
        itinerary = request.form.get('Itinerary')
        places_covered = request.form.get('Places Covered')
        hotel_details = request.form.get('Hotel Details')
        airline = request.form.get('Airline')
        sightseeing_places = request.form.get('Sightseeing Places Covered')
        cancellation_rules = request.form.get('Cancellation Rules')
        package_standard = int(request.form.get('Package Type_Standard', 0))
        package_premium = int(request.form.get('Package Type_Premium', 0))
        package_luxury = int(request.form.get('Package Type_Luxury', 0))
        travel_month = int(request.form.get('Travel_Month'))
        package_budget = int(request.form.get('Package Type_Budget', 0))
        package_deluxe = int(request.form.get('Package Type_Deluxe', 0))
        hotel_ratings = float(request.form.get('Hotel Ratings'))
        start_city_delhi = int(request.form.get('Start City_New Delhi', 0))
        start_city_mumbai = int(request.form.get('Start City_Mumbai', 0))
        travel_day_of_week = int(request.form.get('Travel_DayOfWeek'))
        travel_year = int(request.form.get('Travel_Year'))

        # Create a dictionary to store the input data
        data = {
            'Package Name': package_name,
            'Destination': destination,
            'Itinerary': itinerary,
            'Places Covered': places_covered,
            'Hotel Details': hotel_details,
            'Airline': airline,
            'Sightseeing Places Covered': sightseeing_places,
            'Cancellation Rules': cancellation_rules,
            'Package Type_Standard': package_standard,
            'Package Type_Premium': package_premium,
            'Package Type_Luxury': package_luxury,
            'Travel_Month': travel_month,
            'Package Type_Budget': package_budget,
            'Package Type_Deluxe': package_deluxe,
            'Hotel Ratings': hotel_ratings,
            'Start City_New Delhi': start_city_delhi,
            'Start City_Mumbai': start_city_mumbai,
            'Travel_DayOfWeek': travel_day_of_week,
            'Travel_Year': travel_year
        }

        # Perform prediction using the custom_input dictionary
        prediction = predict_price(data, loaded_lr_model, loaded_pca, loaded_scaler)//10
        prediction = str(prediction)[-7:]

        return jsonify({'prediction': prediction})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
