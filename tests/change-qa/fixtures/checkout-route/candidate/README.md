# Order application
Python 3.9+, standard library only. Run `python3 -m unittest discover -s tests -v` from here. The public API is the WSGI callable `app.application`; POST /checkout takes a JSON object with integer quantity. It returns 201 and appends to the in-memory orders list for a valid order. No persistence, external services, or installs. Use a fresh interpreter for isolated state.
