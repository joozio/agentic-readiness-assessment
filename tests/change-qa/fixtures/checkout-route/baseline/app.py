import json

orders = []

def create_order(quantity):
    return {"quantity": quantity}

def application(environ, start_response):
    if environ.get("PATH_INFO") != "/checkout" or environ.get("REQUEST_METHOD") != "POST":
        start_response("404 Not Found", [("Content-Type", "application/json")])
        return [b'{}']
    payload = json.load(environ["wsgi.input"])
    order = {"quantity": payload["quantity"]}
    orders.append(order)
    start_response("201 Created", [("Content-Type", "application/json")])
    return [json.dumps(order).encode()]
