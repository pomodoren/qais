import pandas as pd
import requests 
import json

BULK_SIZE = 1000
SERVICE_URL = 'http://localhost:5000/api/v1/data'
data_path = 'data.csv'
data_full = pd.read_csv(data_path,header=None)
data_full.columns = ['id','competence','network_ability','promoted']
#data, test = train_test_split(data_full, test_size=0.2)


def stream_bulks(dataset_df, bulk_size=100000):
    """Iterate over bulks of the dataset."""
    for i in range(0,len(dataset_df),bulk_size):
        vals = dataset_df.iloc[i:i+bulk_size]
        yield vals.to_json(orient='records')
        
        
def send_request(data_list):
    response = requests.post(SERVICE_URL, json=json.loads(data_list))
    return response

if __name__ == '__main__':
    # Main loop : iterate on mini-batchs of examples
    for i, json_dicts in enumerate(stream_bulks(data_full, BULK_SIZE)):
        print(i)
        try:
            response = send_request(json_dicts)
        except Exception as e:
            print(i+":\t"+e)
          