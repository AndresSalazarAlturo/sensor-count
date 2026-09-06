import functions_framework
from flask import Flask, jsonify, request
from google.api_core.exceptions import NotFound
from google.cloud import firestore

COLLECTION = "rooms"

app = Flask(__name__)

# Created once at module scope so it survives between invocations on a warm
# instance. Building it per-request would pay the connection setup cost every time.
db = firestore.Client()


def get_json_body():
    """Request payload as a dict, whether it arrived as a JSON body or a query string."""
    if request.method == "GET":
        return request.args.to_dict()
    # silent=True returns None on malformed JSON or a missing Content-Type header
    # instead of raising a 400 that Flask would render as HTML.
    data = request.get_json(silent=True)

    if data is None:
        return {}

    return data


@app.before_request
def handle_preflight():
    # The browser sends an OPTIONS preflight before a cross-origin POST. It must be
    # answered without running the route body. Flask only auto-handles OPTIONS when
    # the route doesn't list it explicitly, and ours do, so we short-circuit here.
    if request.method == "OPTIONS":
        return "", 204


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/increment_count", methods=["GET", "POST", "OPTIONS"])
def increment_count():
    data = get_json_body()
    room_uid = data.get("uid")
    if not isinstance(room_uid, str) or not room_uid.strip():
        return jsonify(success=False, error="Missing or invalid 'uid'"), 400

    room_uid = room_uid.strip()
    doc_ref = db.collection(COLLECTION).document(room_uid)

    try:
        # Increment() is applied server-side by Firestore, so two sensors firing
        # at once can't clobber each other the way a read-then-write would.
        # update() (rather than set(merge=True)) is deliberate: it raises NotFound
        # on a missing document instead of silently creating one.
        doc_ref.update({"count": firestore.Increment(1)})
    except NotFound:
        return jsonify(success=False, error=f"Room '{room_uid}' not found"), 404

    # Costs an extra read, but the client asked for the new value back.
    new_count = doc_ref.get().get("count")

    return jsonify(success=True, room_uid=room_uid, count=new_count), 200


@app.route("/get_count", methods=["GET", "POST", "OPTIONS"])
def get_count():
    data = get_json_body()
    room_uid = data.get("uid")
    if not isinstance(room_uid, str) or not room_uid.strip():
        return jsonify(success=False, error="Missing or invalid 'uid'"), 400

    room_uid = room_uid.strip()
    snapshot = db.collection(COLLECTION).document(room_uid).get()

    # A read of a missing document doesn't raise — it returns a snapshot with
    # exists=False, so this check is what produces the 404 here (unlike the write
    # path, where update() raises NotFound for us).
    if not snapshot.exists:
        return jsonify(success=False, error=f"Room '{room_uid}' not found"), 404

    count = snapshot.to_dict().get("count", 0)

    return jsonify(success=True, room_uid=room_uid, count=count), 200


@functions_framework.http
def door_sensor_api(cloud_function_request):
    """Single Cloud Function entry point; hands the request to the Flask app's router."""
    with app.request_context(cloud_function_request.environ):
        return app.full_dispatch_request()
