import time

from google.cloud import translate
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from src.utilities import constants, sken_logger
import spacy
import subprocess

logger = sken_logger.get_logger("sentence_services")

try:
    nlp = spacy.load("en_core_web_sm")
except OSError as e:
    logger.info("language model not present downloading it")
    subprocess.run(["python3", "-m ","spacy" ,"download en_core_web_sm"],
                   stdout=subprocess.PIPE)
    nlp = spacy.load("en_core_web_sm")

client = translate.TranslationServiceClient()
parent = client.location_path(constants.fetch_constant("translate_project_id"), "global")
target_laguages = [item.language_code for item in
                   client.get_supported_languages(parent).languages[:constants.fetch_constant("translation_depth")]]


def praphrase_sentence(text):
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
    print(sentences)
    threads = len(sentences) + 1 if len(sentences) < multiprocessing.cpu_count() else multiprocessing.cpu_count() - 1
    with ThreadPoolExecutor(max_workers=threads) as exe:
        future = exe.map(praphrase_sentence, sentences)
    return [{"original_sentence": sentences[i], "generated_sentences": list(set(item))} for i, item in
            enumerate(future)]


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


if __name__ == "__main__":
    s = time.time()
    x = get_extracted_sentences("hello this is andy from India")
    print(x)
    print("tIME={}".format(time.time() - s))
