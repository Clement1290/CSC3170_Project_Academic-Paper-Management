from serpapi import GoogleScholarSearch, GoogleSearch
import pandas as pd
import requests
import uuid
import json
import re
import hashlib
from pathlib import Path
from tqdm import tqdm
from urllib.parse import parse_qsl, urlsplit


class Serp(object):
    def __init__(self, api_key):
        """api key of serp api"""
        self.api_key = api_key

    def sengine(self, q):
        """initialize scholar search engine"""
        sengine = GoogleScholarSearch({"q": q, "api_key": self.api_key})
        return sengine

    def gengine(self, q, location="India"):
        """initialize google search engine"""
        gengine = GoogleSearch({"q": q, "location": location, "api_key": self.api_key})
        return gengine

    def write_json(self, data, save_path):
        """Write json data"""

        unique_node_id = str(uuid.uuid4())
        with open(f"{save_path}/{unique_node_id}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return 0

    def to_md5(self, text):
        """text to md5 conversion"""

        m = hashlib.md5()
        m.update(text.encode("utf-8"))
        return m.hexdigest()

    def filter_url(self, results):
        """filter the urls of special text"""

        try:
            fl_result = results["organic_results"]
        except Exception as e:

            print("API limit exhaust")

        related_articles = []
        for result in fl_result:
            # https://regex101.com/r/XuEhoh/1
            related_article = re.search(
                r"q=(.*)\/&scioq", result["inline_links"]["related_pages_link"]
            ).group(1)#提取第一个related pages link
            related_articles.append(related_article)
        return related_articles

    def get_related_pages(self, query):
        """get all related pages of a research
        paper from google scholar"""

        folder_name = self.to_md5(query)
        folder_path = f"Google_data/related_pages/{folder_name}/"
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        seng = self.sengine(query)
        data = seng.get_dict()

        if "error" in data:
            return "API limit exhaust"
        else:
            url = self.filter_url(data)

            all_results = {}
            for single_url in tqdm(url):
                seng = self.sengine(single_url)
                result = self.pagination(seng, None, folder_path)
                all_results[self.to_md5(single_url)] = result
            return all_results

    def google_search(self, query, max_pages):

        folder_name = self.to_md5(query)
        folder_path = f"Google_data/Google_search/{folder_name}/"
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        seng = self.gengine(query)
        result = self.pagination(seng, max_pages, folder_path)
        return result
    
    
    def google_scholar_search(self, q, max_pages):
    
        folder_name = self.to_md5(q)
        folder_path = f"Google_data/Google_Scholar/{folder_name}/"
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        seng        = self.sengine(q)
        result      = self.pagination(seng, max_pages, folder_path)
        return result
    
    def project_google_scholar_search(self, q, max_pages):
    
        folder_name = self.to_md5(q)
        folder_path = f"Google_data/Google_Scholar/{folder_name}/"
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        seng        = self.sengine(q)
        result      = self.project_pagination(seng, max_pages, folder_path)
        return result

    def filter_re(self, res):
        return [k["title"] for k in res["organic_results"]]

    def get_citations(self, query):

        folder_name = self.to_md5(query)
        folder_path = f"Google_data/Citation_data/{folder_name}/"
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        seng = self.sengine(query)
        data = seng.get_dict()
        all_results = {}

        url = [
            links["inline_links"]["cited_by"]["serpapi_scholar_link"]
            for links in data["organic_results"]
        ]
        for paper_ in tqdm(url):
            res = self._req_pagination(paper_, max_pages=None, save_result=folder_path)
            all_results[self.to_md5(paper_)] = res
        return all_results

    def filter_data_(self, result, save_path):
        unique_node_id = str(uuid.uuid4())
        df_result = {"title": [], "link": [], "snippet": []}

        try:
            fl_result = result["organic_results"]
        except Exception as e:
            print("API limit exhaust")

        for single_result in fl_result:
            if "title" in single_result:
                df_result["title"].append(single_result["title"])
            else:
                df_result["title"].append("no_title")

            if "link" in single_result:
                df_result["link"].append(single_result["link"])
            else:
                df_result["link"].append("no_link")

            if "snippet" in single_result:
                df_result["snippet"].append(single_result["snippet"])
            else:
                df_result["snippet"].append("no_snipped")
        small_df = pd.DataFrame(df_result)
        small_df.to_csv(f"{save_path}{unique_node_id}.csv", index=False)
        return small_df
    
    def project_filter_data_(self, result, save_path):
        unique_node_id = str(uuid.uuid4())
        df_result = {"title": [], "link": [], "snippet": [], "summary": [], "author_1":[], "author_1_link":[]
                     , "author_2":[], "author_2_link":[], "author_3":[], "author_3_link":[], "resource":[], "resource_link":[],
                     "cited_number":[], "cited_papers_link":[], "related_papers_link":[],"versions_number":[],"all_versions_link":[]}

        try:
            fl_result = result["organic_results"]
        except Exception as e:
            print("API limit exhaust")

        for single_result in fl_result:
            if "title" in single_result:
                df_result["title"].append(single_result["title"])
            else:
                df_result["title"].append("no_title")

            if "link" in single_result:
                df_result["link"].append(single_result["link"])
            else:
                df_result["link"].append("no_link")

            if "snippet" in single_result:
                df_result["snippet"].append(single_result["snippet"])
            else:
                df_result["snippet"].append("no_snipped")

            if "publication_info" in single_result:
                if "summary" in single_result["publication_info"]:
                    df_result["summary"].append(single_result["publication_info"]["summary"])
                else:
                    df_result["summary"].append("no_summary")
                
                if "authors" in single_result["publication_info"]:
                    if len(single_result["publication_info"]["authors"]) >= 1:
                        df_result["author_1"].append(single_result["publication_info"]["authors"][0]["name"])
                        df_result["author_1_link"].append(single_result["publication_info"]["authors"][0]["link"])
                    else:
                        df_result["author_1"].append("no_author")
                        df_result["author_1_link"].append("no_author_link")
                    
                    if len(single_result["publication_info"]["authors"]) >= 2:
                        df_result["author_2"].append(single_result["publication_info"]["authors"][1]["name"])
                        df_result["author_2_link"].append(single_result["publication_info"]["authors"][1]["link"])
                    else:
                        df_result["author_2"].append("no_author")
                        df_result["author_2_link"].append("no_author_link")
                    
                    if len(single_result["publication_info"]["authors"]) >= 3:
                        df_result["author_3"].append(single_result["publication_info"]["authors"][2]["name"])
                        df_result["author_3_link"].append(single_result["publication_info"]["authors"][2]["link"])
                    else:
                        df_result["author_3"].append("no_author")
                        df_result["author_3_link"].append("no_author_link")
                else:
                    df_result["author_1"].append("no_author")
                    df_result["author_1_link"].append("no_author_link")
                    df_result["author_2"].append("no_author")
                    df_result["author_2_link"].append("no_author_link")
                    df_result["author_3"].append("no_author")
                    df_result["author_3_link"].append("no_author_link")
                    
            else:
                df_result["author_1"].append("no_author")
                df_result["author_1_link"].append("no_author_link")
                df_result["author_2"].append("no_author")
                df_result["author_2_link"].append("no_author_link")
                df_result["author_3"].append("no_author")
                df_result["author_3_link"].append("no_author_link")
                df_result["summary"].append("no_summary")

            if "resources" in single_result:
                if "title" in single_result["resources"][0]:
                    df_result["resource"].append(single_result["resources"][0]["title"])
                else:
                    df_result["resource"].append("no_resource")

                if "link" in single_result["resources"][0]:
                    df_result["resource_link"].append(single_result["resources"][0]["link"])
                else:
                    df_result["resource_link"].append("no_resource_link")
            else:
                df_result["resource"].append("no_resource")
                df_result["resource_link"].append("no_resource_link")

            if "inline_links" in single_result:
                if "cited_by" in single_result["inline_links"]:
                    if "total" in single_result["inline_links"]["cited_by"]:
                        df_result["cited_number"].append(single_result["inline_links"]["cited_by"]["total"])
                    else:
                        df_result["cited_number"].append("no_cited_number")

                    if "link" in single_result["inline_links"]["cited_by"]:
                        df_result["cited_papers_link"].append(single_result["inline_links"]["cited_by"]["link"])
                    else:
                        df_result["cited_papers_link"].append("no_cited_papers_link")
                else:
                    df_result["cited_number"].append("no_cited_number")
                    df_result["cited_papers_link"].append("no_cited_papers_link")

                if "related_pages_link" in single_result["inline_links"]:
                    df_result["related_papers_link"].append(single_result["inline_links"]["related_pages_link"])
                else:
                    df_result["related_papers_link"].append("no_related_pages_link")

                if "versions" in single_result["inline_links"]:
                    if "total" in single_result["inline_links"]['versions']:
                        df_result["versions_number"].append(single_result['inline_links']["versions"]["total"])
                    else:
                        df_result["versions_number"].append("no_versions_number")

                    if "link" in single_result["inline_links"]['versions']:
                        df_result["all_versions_link"].append(single_result['inline_links']["versions"]["link"])
                    else:
                        df_result["all_versions_link"].append("no_all_versions_link")
                else:
                    df_result["versions_number"].append("no_versions_number")
                    df_result["all_versions_link"].append("no_all_versions_link")
            else:
                df_result["versions_number"].append("no_versions_number")
                df_result["all_versions_link"].append("no_all_versions_link")
                df_result["related_papers_link"].append("no_related_pages_link")
                df_result["cited_number"].append("no_cited_number")
                df_result['cited_papers_link'].append("no_cited_papers_link")

        for col in df_result.keys():
            print(col, len(df_result[col]))
        small_df = pd.DataFrame(df_result)
        small_df.to_csv(f"{save_path}{unique_node_id}.csv", index=False)
        
        return small_df

    def _req_pagination(self, url, max_pages=None, save_result="."):

        results = {}
        next_page = True
        page_no = 1
        next_link = url + f"&api_key={self.api_key}"
        all_df = []

        if max_pages:
            while next_page and page_no <= max_pages:

                print(f"Page : {page_no}")
                result = requests.get(next_link).json()

                if "error" in result:
                    break
                else:
                    fil_res = self.filter_data_(result, save_result)
                    all_df.append(fil_res)
                    self.write_json(result, save_result)
                    if "serpapi_pagination" in result:
                        pagination = result["serpapi_pagination"]
                        if "next" in pagination:
                            next_page = True
                            next_link = (
                                pagination["next_link"] + f"&api_key={self.api_key}"
                            )
                        else:
                            next_page = False
                        results[page_no] = result
                        page_no += 1
                    else:
                        break

        else:
            while next_page:
                print(f"Page : {page_no}")
                result = requests.get(next_link).json()

                if "error" in result:
                    break
                else:
                    fil_res = self.filter_data_(result, save_result)

                    all_df.append(fil_res)
                    self.write_json(result, save_result)

                    if "serpapi_pagination" in result:
                        pagination = result["serpapi_pagination"]

                        if "next" in pagination:
                            next_page = True
                            next_link = (
                                pagination["next_link"] + f"&api_key={self.api_key}"
                            )
                        else:
                            next_page = False

                        results[page_no] = result
                        page_no += 1
                    else:
                        break

        all_df = pd.concat(all_df)
        alpha_df = pd.DataFrame(all_df).reset_index(drop=True)
        alpha_df.to_csv(f"{save_result}allcsvs_req_df.csv", index=False)
        return alpha_df

    def pagination(self, cengine, max_pages, save_result="."):

        has_next_page = True
        page_no = 1
        all_result = {}
        all_df = []

        if max_pages:
            while has_next_page and page_no <= max_pages:
                print(f"Page : {page_no}")
                data = cengine.get_dict()

                if "error" in data:
                    break
                else:

                    fil_res = self.filter_data_(data, save_result)

                    all_df.append(fil_res)
                    self.write_json(data, save_result)
                    all_result[page_no] = data
                    page_no += 1

                    if "pagination" in data:
                        has_next_page = data["pagination"]["next"]
                        cengine.params_dict.update(
                            dict(
                                parse_qsl(
                                    urlsplit(
                                        data.get("serpapi_pagination").get("next")
                                    ).query
                                )
                            )
                        )
                    else:
                        break

        else:
            while has_next_page:
                print(f"Page : {page_no}")
                data = cengine.get_dict()

                if "error" in data:
                    break
                else:
                    fil_res = self.filter_data_(data, save_result)

                    all_df.append(fil_res)
                    self.write_json(data, save_result)
                    all_result[page_no] = data

                    page_no += 1

                    if "pagination" in data:
                        has_next_page = data["pagination"]["next"]
                        cengine.params_dict.update(
                            dict(
                                parse_qsl(
                                    urlsplit(
                                        data.get("serpapi_pagination").get("next")
                                    ).query
                                )
                            )
                        )
                    else:
                        break

        all_df = pd.concat(all_df)
        alpha_df = pd.DataFrame(all_df).reset_index(drop=True)
        alpha_df.to_csv(f"{save_result}allcsvs_df.csv", index=False)
        return alpha_df
    
    def project_pagination(self, cengine, max_pages, save_result="."):

        has_next_page = True
        page_no = 1
        all_result = {}
        all_df = []

        if max_pages:
            while has_next_page and page_no <= max_pages:
                print(f"Page : {page_no}")
                data = cengine.get_dict()

                if "error" in data:
                    break
                else:

                    fil_res = self.project_filter_data_(data, save_result)

                    all_df.append(fil_res)
                    #self.write_json(data, save_result)
                    all_result[page_no] = data
                    page_no += 1

                    if "pagination" in data:
                        has_next_page = data["pagination"]["next"]
                        cengine.params_dict.update(
                            dict(
                                parse_qsl(
                                    urlsplit(
                                        data.get("serpapi_pagination").get("next")
                                    ).query
                                )
                            )
                        )
                    else:
                        break

        else:
            while has_next_page:
                print(f"Page : {page_no}")
                data = cengine.get_dict()

                if "error" in data:
                    break
                else:
                    fil_res = self.project_filter_data_(data, save_result)

                    all_df.append(fil_res)
                    #self.write_json(data, save_result)
                    all_result[page_no] = data

                    page_no += 1

                    if "pagination" in data:
                        has_next_page = data["pagination"]["next"]
                        cengine.params_dict.update(
                            dict(
                                parse_qsl(
                                    urlsplit(
                                        data.get("serpapi_pagination").get("next")
                                    ).query
                                )
                            )
                        )
                    else:
                        break

        all_df = pd.concat(all_df)
        alpha_df = pd.DataFrame(all_df).reset_index(drop=True)
        alpha_df.to_csv(f"{save_result}allcsvs_df.csv", index=False)
        return alpha_df
