from requests import exceptions
import argparse
import requests
import cv2
import os

API_KEY = ""
MAX_RESULTS = 250
GROUP_SIZE = 50

URL = "https://api.bing.microsoft.com/v7.0/images/search"

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--query", required=True, help="Search query to search Bing Image API for")
    ap.add_argument("-o", "--output", required=True, help="Path to output directory of images")
    args = vars(ap.parse_args())

    EXCEPTIONS = {IOError, FileNotFoundError, exceptions.RequestException, exceptions.HTTPError,
                  exceptions.ConnectionError, exceptions.Timeout}

    search_term = args["query"]
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}
    params = {"q": search_term, "offset": 0, "count": GROUP_SIZE}

    print("[INFO] Searching for '{}'".format(search_term))
    search = requests.get(URL, headers=headers, params=params)
    search.raise_for_status()

    results = search.json()
    est_num_results = min(results['totalEstimatedMatches'], MAX_RESULTS)
    print("[INFO] {} total results for '{}'".format(est_num_results, search_term))

    total = 0

    for offset in range(0, est_num_results, GROUP_SIZE):
        print("[INFO] Making request for group {}-{} of {}...".format(offset, offset + GROUP_SIZE, est_num_results))
        params["offset"] = offset
        search = requests.get(URL, headers=headers, params=params)
        search.raise_for_status()
        results = search.json()
        print("[INFO] Saving images for group {}-{} of {}...".format(offset, offset + GROUP_SIZE, est_num_results))

        for v in results["value"]:
            try:
                print("[INFO] Fetching: {}".format(v["contentUrl"]))
                r = requests.get(v["contentUrl"], timeout=30)

                ext = v["contentUrl"][v["contentUrl"].rfind("."):]
                p = os.path.sep.join([args["output"], "{}{}".format(str(total).zfill(8), ext)])

                f = open(p, "wb")
                f.write(r.content)
                f.close()

                image = cv2.imread(p)

                if image is None:
                    print("[INFO] Deleting: {}".format(p))
                    os.remove(p)
                    continue

                total += 1

            except Exception as e:
                if type(e) in EXCEPTIONS:
                    print("[INFO] Skipping: {}".format(v["contentUrl"]))
                    continue
