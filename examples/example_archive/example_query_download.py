from hypernets_api import HYPERNETSAPI

api_token = "<your-api-token>" # generate on https://landhypernet.org.uk/api/token/generate

output_path= "./"

api = HYPERNETSAPI(api_token)


query_dict = {
    "site": "JSIT",
    "product_level": "L2B",
    "start_time": '2025-07-27T09:00:00Z',
    "stop_time": '2025-07-27T10:00:00Z',
}

results = api.query(query_dict)
print(results)
paths = api.download_results(results, output_path=output_path)
print(paths)