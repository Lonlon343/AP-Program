from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"Message": "Hi World", "Name": "Leon", "Alter": 29}


@app.get("/name/{name}")
def greet_name(name: str):
    return {"Message": f"Hi {name} !"}

@app.get("/age/{age}")
def tell_age(age: int):
    if age == 1:
        return {"Message": f"Du bist {age} Jahr alt! Du bist minderjährig!"}
    if age < 18:
        return {"Message": f"Du bist {age} Jahre alt! Du bist minderjährig!"}
    if age >= 140:
        return NameError
    return {"Message": f"Du bist {age} Jahre alt!"}

@app.get("/add/{num1}/{num2}")
def add_numbers(num1: int, num2: int):
    summe = num1 + num2
    return {"Message": f"Die Summe von {num1} und {num2} ist {summe}!"}