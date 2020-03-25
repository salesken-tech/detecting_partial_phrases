import time

from google.cloud import translate
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from src.utilities import constants, sken_logger, db
import spacy
import textacy

logger = sken_logger.get_logger("sentence_services")

nlp = spacy.load("en_core_web_sm")

client = translate.TranslationServiceClient()
parent = client.location_path(constants.fetch_constant("translate_project_id"), "global")
target_laguages = [item.language_code for item in
                   client.get_supported_languages(parent).languages[:constants.fetch_constant("translation_depth")]]


def paraphrase_sentence(text):
    global parent, target_laguages

    def get_the_other(language):
        response = client.translate_text(
            parent=parent,
            contents=[text],
            mime_type='text/plain',  # mime types: text/plain, text/html
            source_language_code='en-IN',
            target_language_code=language)
        translated_text = []
        for translation in response.translations:
            translated_text.append(translation.translated_text)
        return translated_text

    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() - 1) as ex:
        result = ex.map(get_the_other, target_laguages)
    translated_text = []
    for item in result:
        translated_text.extend(item)
    result = []
    for lg, sentence in zip(target_laguages, translated_text):
        response = client.translate_text(
            parent=parent,
            contents=[sentence],
            mime_type='text/plain',  # mime types: text/plain, text/html
            source_language_code=str(lg),
            target_language_code="en")
        for translation in response.translations:
            result.append(translation.translated_text)
    return result


def get_sentences_paraphrase(sentences):
    threads = len(sentences) + 1 if len(sentences) < multiprocessing.cpu_count() else multiprocessing.cpu_count() - 1
    with ThreadPoolExecutor(max_workers=threads) as exe:
        future = exe.map(paraphrase_sentence, sentences)
    return [{"original_sentence": sentences[i], "generated_sentences": list(set(item))} for i, item in
            enumerate(future)]


def paraphrase_org_signals(org_id, product_id):
    sql = "select id,value from facet_signal where facet_signal.org_id=%s and facet_signal.product_id=%s"
    rows, cols = db.DBUtils.get_instance().execute_query(sql, (org_id, product_id), is_write=False, is_return=True)
    if len(rows) > 0:
        signal_ids = []
        signals = []
        for row in rows:
            signal_ids.append(row[cols.index("id")])
            signals.append(row[cols.index("value")])
        logger.info("Generating paraphrases for org={},prod_id={} and no.of signals={}".format(org_id, product_id,
                                                                                               len(signals)))
        paraphrase_dict = get_sentences_paraphrase(signals)
        data = []
        for i, item in enumerate(paraphrase_dict):
            for sentence in item["generated_sentences"]:
                data.append(tuple([sentence, signal_ids[i]]))
        logger.info("Inserting generated signals into db")
        db.DBUtils.get_instance().insert_bulk("generated_facet_signals", "value, facet_signal_id", data,
                                              return_parameter=None)

    else:
        logger.info("Did not find any product_signals for org_id={} and product_id={}".format(org_id, product_id))


def flatten_tree(tree):
    return ''.join([token.text_with_ws for token in list(tree)]).strip()


def get_extracted_sentences(sentence):
    global nlp
    doc = nlp(sentence)
    np = []
    for tok in doc:
        if tok.pos_ == "NOUN":
            np.append(flatten_tree(tok.subtree))
    return {"orignal_sentence": sentence, "extracted_sentences": np}


def make_ngram(sentence):
    if sentence is not None:
        logger.info("Making a total of {}_gram for sentence={}".format(len(sentence.split()),sentence))
        doc = textacy.make_spacy_doc(sentence, lang='en_core_web_sm')
        result = []
        for i in range(len(sentence.split())):
            n_gram = textacy.extract.ngrams(doc, n=i + 1, filter_stops=False)
            result.append({"lenght": str(i + 1), "sentences": [str(item) for item in n_gram]})
        return result
    else:
        logger.info("Please enter proper data")



