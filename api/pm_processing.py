import joblib

def model_extractor(model,save_pickle,model_name):
    values = {
        "model_name":None,
        "accuracy":None,
        "col_num":None,
        "features":None,
        "parameters":None,
        "model_type":None,
        "model":None,
        "train_size":None
    }
    #check the dtype
    try:
        temp = str(model.get_params) 
        values['parameters'] = model.get_params()
        temp2 = temp.split('(')[0]
        values['model'] = temp2.split('of')[1].lstrip(' ')
        temp3 = temp2.split('of')[0]
        values['model_type'] = temp3.split('method')[1].split('.')[0].lstrip(' ')
        #self.__class_len  = len(model.classes_)
        if(save_pickle == True):
            joblib.dump(model,f'{model_name}.pkl')
    except Exception as e:
        print(e)
    return values

def describe_model(
    model_name,
    model,
    X_train,
    accuracy,
    save_pickle=False,
    Flag = False
):
    values = model_extractor(model,save_pickle,model_name)
    values['model_name'] = model_name.lstrip(' ')
    values['accuracy'] = accuracy
    values['col_num'] =  X_train.shape[1]
    values['features'] = str(list(X_train.columns))
    #values['parameters']
    #values['model_type']
    #values['model'] 
    values['train_size'] = X_train.shape[0]
    
    return values