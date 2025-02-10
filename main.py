import requests
import json
import time
import csv
from bs4 import BeautifulSoup as BS
from urllib.parse import quote_plus

class Task1:
    def __init__(self, url, filename, jsonfilename):
        self.url = url
        self.queryFile = filename
        self.queries = None
        self.jsonoutput = jsonfilename
        self.results = {}
    
    def readQueries(self):
        with open(self.queryFile, "r") as f:
            self.queries = [line.strip() for line in f if line.strip()]
    
    def scrapeResults(self):
        for i, query in enumerate(self.queries):
            encoded_query = quote_plus(query)
            queryUrl = f"{self.url}{encoded_query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
            response = requests.get(queryUrl, headers=headers)
            soup = BS(response.text, "html.parser")

            top10Links = []
            for anchor in soup.select("h2.result__title a.result__a")[:10]:
                top10Links.append(anchor["href"])
            
            self.results[query] = top10Links
            print(f"Query {i+1} completed")
            time.sleep(5)

    def saveToJsonFile(self):
        with open(self.jsonoutput, "w") as f:
            json.dump(self.results, f, indent=4)

class Task2:
    def __init__(self, outputfile, googlefile):
        self.outputFile = outputfile
        self.googleFile = googlefile
        self.overlap = {}
        self.spearman = {}
    
    def loadResults(self):
        with open(self.googleFile, "r") as f:
            self.googleResults = json.load(f)
        with open(self.outputFile, "r") as f:
            self.searchEngineResults = json.load(f)

    def calcOverlap(self):
        for i, ((kGoogle, vGoogle), (kSearchEngine, vSearchEngine)) in enumerate(zip(self.googleResults.items(), self.searchEngineResults.items())):
            google = set(vGoogle)
            searchEngine = set(vSearchEngine)
            self.overlap[f"Query {i+1}"] = (len(google.intersection(searchEngine)) / len(google)) * 100
        
        return self.overlap
    
    def computeSpearman(self, google, searchEngine):
        ranks = [(google.index(res) + 1, searchEngine.index(res) + 1) for res in google if res in searchEngine]

        dSquared = sum([(g - s) ** 2 for (g,s) in ranks])
        n = len(ranks)
        rho = 1 - ((6 * dSquared) / (n * (n**2 - 1)))

        return rho

    def calcSpearman(self):
        for i, ((kGoogle, vGoogle), (kSearchEngine, vSearchEngine)) in enumerate(zip(self.googleResults.items(), self.searchEngineResults.items())):
            if self.overlap[f"Query {i+1}"] == 0.0:
                self.spearman[f"Query {i+1}"] = 0
            elif self.overlap[f"Query {i+1}"] == 10.0:
                ranks = [(vGoogle.index(res) + 1, vSearchEngine.index(res) + 1) for res in vGoogle if res in vSearchEngine]
                if ranks[0][0] == ranks[0][1]:
                    self.spearman[f"Query {i+1}"] = 1
                else:
                    self.spearman[f"Query {i+1}"] = 0
            else:
                self.spearman[f"Query {i+1}"] = self.computeSpearman(vGoogle, vSearchEngine)
        
        return self.spearman


def main():
    searchEngineUrl = "https://www.duckduckgo.com/html/?q="
    googleFile = "Google_Result4.json"
    queryFile = "100QueriesSet4.txt"
    # outputJson = "hw1.json"
    outputJson = "hw1.json"
    # task1 = Task1(searchEngineUrl, queryFile, outputJson)
    # task1.readQueries()
    # task1.scrapeResults()
    # task1.saveToJsonFile()

    task2 = Task2(outputJson, googleFile)
    task2.loadResults()
    overlap = task2.calcOverlap()
    spearman = task2.calcSpearman()
    csv_data = [
        ["Queries", "Number of Overlapping Results", "Percent Overlap", "Spearman Coefficient"]
    ]
    avgOverlap, avgSpearman = 0, 0
    for ((k1, v1), (k2, v2)) in zip(overlap.items(), spearman.items()):
        csv_data.append([k1, int(v1/10), v1, v2])
        avgOverlap += int(v1/10)
        avgSpearman += v2
    avgOverlap /= 100
    avgSpearman /= 100
    csv_data.append(["Averages", avgOverlap, round(avgOverlap*10, 2), avgSpearman])

    with open("hw1.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

if __name__ == '__main__':
    main()