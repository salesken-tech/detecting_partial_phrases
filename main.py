from flask import Flask, request, Response, render_template, flash, redirect, send_file
from src.services import sentence_services, match_result
from src.utilities import sken_logger, sken_singleton, db
import jsonpickle
import time

logger = sken_logger.get_logger("main")

sken_singleton.Singletons.get_instance()
db.DBUtils.get_instance()

app = Flask(__name__)


@app.route("/paraphrase_sentences", methods=["POST", "GET"])
def paraphrase():
    sentences = request.args.getlist("sentences")
    if len(sentences) != 0:
        logger.info("Making paraphrases for {} sentences".format(len(sentences)))
        resp = Response(jsonpickle.encode(sentence_services.get_sentences_paraphrase(sentences)),
                        mimetype='application/json')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    else:
        logger.error("Did not receive proper data ")
        resp = Response("!!!!!!Please send proper data!!!!!!!!!",
                        mimetype='application/text')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp


@app.route("/org_signals_paraphrase", methods=["POST", "GET"])
def org_signals_paraphrase():
    org_id = request.args.get("org_id")
    product_id = request.args.get("product_id")
    resp = sentence_services.paraphrase_org_signals(org_id, product_id)


@app.route("/match_playground", methods=["POST", "GET"])
def return_match_result():
    signal = request.form.get("signal")
    snippet = request.form.get("snippet")
    threshold = request.form.get("threshold")
    s = time.time()
    result = match_result.make_result(signal, snippet, threshold)
    logger.info("Time for result={}".format(time.time() - s))
    resp = Response(jsonpickle.encode(result),
                    mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=True)
