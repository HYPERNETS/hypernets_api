from hypernets_api import HYPERNETSAPI

api_token = "<your-api-token>" # generate on https://landhypernet.org.uk/api/token/generate
api_token = "95atDYbhe4y9CzEtbsmeRilMl7b-XqnOUqCMr2P_FkI"

output_path= "./"

api = HYPERNETSAPI(api_token)

query_dict = {"site":"GHNA",
        "product_level":"L2A_REF",
        "start_time": "2023-10-31T08:00:00Z",
        "stop_time": "2023-11-01T08:00:00Z",
}

results = api.query(query_dict)
print(results)
#paths = api.download_results(results, output_path=output_path)


