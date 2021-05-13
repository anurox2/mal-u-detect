## Mal - U - Detect

### This project was created to complete the requirements for an Indidual Project/Reading course in Spring 2021.
- The project comprises of 3 main parts
    - Machine Learning model (CNN) trained to detect DGA URLs
    - Django server which accepts URL as a parameter and uses the model to predict if the URL is malicious or not.
    - React web server which serves as the frontend

This repo contains only the backend and the ML code.
> - Create and activate a python3 environment
> - Install all the requirements by running `pip -r requirements.txt`
> - Run the backend from inside the `malUdetectBackend` folder using `python manage.py runserver`
> - You will be able to access the URL detection API by hitting `localhost:8000/urlDetector`

Go to the [maludetectfrontend repo](https://github.com/anurox2/mal-u-detect-frontend) here, and get the frontend code. Instructions to run it are in that repo.