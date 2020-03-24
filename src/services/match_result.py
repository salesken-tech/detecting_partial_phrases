from src.utilities import constants, sken_logger, sken_singleton
from src.services import sentence_services
from concurrent.futures import ThreadPoolExecutor
import time
import numpy as np

logger = sken_logger.get_logger("match_result")


def make_result(signal, snippet, threshold):
    logger.info("Generating sentences for signal={}".format(signal))
    start = time.time()
    generated_signals = sentence_services.paraphrase_sentence(signal)
    logger.info("Extracting sentences out of {} signals".format(len(generated_signals) + 1))
    with ThreadPoolExecutor(max_workers=len(generated_signals) + 1) as exe:
        future = exe.map(sentence_services.get_extracted_sentences, list(set(generated_signals + [signal])))
    extracted_sentences = []
    for item in future:
        extracted_sentences.extend(item['extracted_sentences'])
    paraphrased_signals = []
    for signal in list(set(generated_signals)):
        paraphrased_signals.append({"signal_tag": "para", "signal": signal})
    extracted_signals = []
    for signal in list(set(extracted_sentences)):
        extracted_signals.append({"signal_tag": "extracted", "signal": signal})
    logger.info("Final signal count={}".format(len(paraphrased_signals) + len(extracted_signals)))
    logger.info("Time for creating signals={}".format(time.time() - start))
    logger.info("Computing vectors")
    start = time.time()
    with ThreadPoolExecutor(max_workers=2) as exe:
        signal_vectors = exe.submit(sken_singleton.Singletons.get_instance().perform_embeddings,
                                    [item["signal"] for item in paraphrased_signals] + [item["signal"] for item in
                                                                                        extracted_signals]).result()
        snippet_vector = exe.submit(sken_singleton.Singletons.get_instance().perform_embeddings,
                                    [snippet]).result()
    logger.info("Time for computing vectores={}".format(time.time() - start))
    para_vectors = signal_vectors[:len(paraphrased_signals)]
    extra_vectors = signal_vectors[len(paraphrased_signals):]
    logger.info("Making results")
    result = []
    for i in range(len(paraphrased_signals)):
        score = np.dot(snippet_vector, para_vectors[i].T) / (
                np.linalg.norm(snippet_vector) * np.linalg.norm(para_vectors[i]))
        if score >= float(threshold):
            result.append({"tag": paraphrased_signals[i]['signal_tag'], "signal": paraphrased_signals[i]['signal'],
                           "snippet": snippet, "score": str(score[0]), "status": "MATCH"})
        else:
            result.append({"tag": paraphrased_signals[i]['signal_tag'], "signal": paraphrased_signals[i]['signal'],
                           "snippet": snippet, "score": str(score[0]), "status": "NO-MATCH"})

    for i in range(len(extracted_signals)):
        score = np.dot(snippet_vector, extra_vectors[i].T) / (
                np.linalg.norm(snippet_vector) * np.linalg.norm(extra_vectors[i]))
        if score >= float(threshold):
            result.append({"tag": extracted_signals[i]['signal_tag'], "signal": extracted_signals[i]['signal'],
                           "snippet": snippet, "score": str(score[0]), "status": "MATCH"})
        else:
            result.append({"tag": paraphrased_signals[i]['signal_tag'], "signal": paraphrased_signals[i]['signal'],
                           "snippet": snippet, "score": str(score[0]), "status": "NO-MATCH"})
    return result
