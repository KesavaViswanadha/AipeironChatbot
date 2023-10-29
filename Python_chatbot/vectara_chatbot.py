""" This is an example of calling Vectara API via python using http/rest as communication protocol.
"""

import argparse
import json
import logging
import requests
import numpy as np
import spacy
from PyPDF2 import PdfReader
import nltk
import sys
import json
import os
import openai
from scipy.spatial import distance
import plotly.express as px
from sklearn.cluster import KMeans
from umap import UMAP
import pinecone

def _get_query_json(customer_id: int, corpus_id: int, query_value: str):
    """ Returns a query json. """
    query = {}
    query_obj = {}

    query_obj["query"] = query_value
    query_obj["num_results"] = 10

    corpus_key = {}
    corpus_key["customer_id"] = customer_id
    corpus_key["corpus_id"] = corpus_id

    query_obj["corpus_key"] = [ corpus_key ]
    query["query"] = [ query_obj ]
    return json.dumps(query)


def query(customer_id: int, corpus_id: int, query_address: str, api_key: str, query: str):
    """This method queries the data.
    Args:
        customer_id: Unique customer ID in vectara platform.
        corpus_id: ID of the corpus to which data needs to be indexed.
        query_address: Address of the querying server. e.g., api.vectara.io
        api_key: A valid API key with query access on the corpus.

    Returns:
        (response, True) in case of success and returns (error, False) in case of failure.

    """
    post_headers = {
        "customer-id": f"{customer_id}",
        "x-api-key": api_key
    }

    response = requests.post(
        f"https://{query_address}/v1/query",
        data=_get_query_json(customer_id, corpus_id, query),
        verify=True,
        headers=post_headers)

    if response.status_code != 200:
        logging.error("Query failed with code %d, reason %s, text %s",
                       response.status_code,
                       response.reason,
                       response.text)
        return response, False
    return response, True


def main(this_question):
    full_ans = query(2120125989, 1, "api.vectara.io", "zqt_fl6OJXFubZFMvUHJWOo3DUoEPbfX82Ff1SXz7w", this_question)
    if not full_ans[1]:
        print("failed.")
    this_ans = full_ans[0].json()
   #print(this_ans)
    with open('output_query_vectara.json', 'w') as f:  # Write the results to a file
        print()
        json.dump(this_ans['responseSet'][0]['response'][0]['text'] + " " + this_ans['responseSet'][0]['response'][1]['text'] + " " + this_ans['responseSet'][0]['response'][2]['text'], f)

if __name__ == "__main__":
    main(sys.argv[1])
    # logging.basicConfig(
    #     format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

    # parser = argparse.ArgumentParser(
    #             description="Vectara rest example (With API Key authentication.")

    # parser.add_argument("--customer-id", type=int, help="Unique customer ID in Vectara platform.")
    # parser.add_argument("--corpus-id",
    #                     type=int,
    #                     help="Corpus ID to which data will be indexed and queried from.")

    # parser.add_argument("--serving-endpoint", help="The endpoint of querying server.",
    #                     default="api.vectara.io")
    # parser.add_argument("--api-key", help="API key retrieved from Vectara console.")
    # parser.add_argument("--query", help="Query to run against the corpus.", default="Test query")

    # args = parser.parse_args()

    # if args:
    #     error, status = query(args.customer_id,
    #                           args.corpus_id,
    #                           args.serving_endpoint,
    #                           args.api_key,
    #                           args.query)
