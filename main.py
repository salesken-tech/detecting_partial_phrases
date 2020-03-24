from flask import Flask, request, Response, render_template, flash, redirect, send_file
from src.services import sentence_services
from src.utilities import sken_logger
import jsonpickle
logger = sken_logger.get_logger("main")
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=True)
