'''
Created by @Soham Pathak
Ping me up :https://www.linkedin.com/in/kaisersoham/ 
Powered by Python,SQlITE3 and Dash
'''

import sqlite3
from sqlite3 import Error
import pandas as pd
import dash
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from collections import Counter
import ast 
import warnings
import joblib

class ModelLogger:

	def __init__(self,path,Flag = False):
		'''
		Modelloger is an opensource model logging and comparision tool .
		Logs are stored in sqlite3 database
		Initialise a modelloger instance by calling the ModelLogger().
		Parameters:
		-----------
        path : <String> Input the path of the database where you want to keep
               the records stored .
               If you already have an exiting modelloger db by the same name than
               modelloger will load it for you if not than it will create a new db.
               To check the schema check ---> table_schema()
        Flag : <boolean> If true than will print out the contents of the db
        Example :
        ---------
        mlog = ModelLogger("c/path/to/db/databasename.db")
        mlog.table_schema()                   
		'''
		self.__set_db(path)
		self.__select_all_tasks(Flag)


	def __create_connection(self):
	    __conn = None
	    try:
	        __conn = sqlite3.connect(self.database)
	        return __conn
	    except Error as e:
	        print(e)

	    return __conn


	def __create_table(self):
	    try:
	        c = self.__conn.cursor()
	        c.execute(self.table_schema)
	        print('Setup Completed ')
	    except Error as e:
	        print(e)


	def __set_db(self,path):
		self.database = path
		self.table_schema = """ CREATE TABLE IF NOT EXISTS models (
	                                        model_id integer PRIMARY KEY,
	                                        model_name text NOT NULL UNIQUE,
	                                        accuracy integer NOT NULL,
	                                        col_num integer NOT NULL,
	                                        features text NOT NULL,
	                                        parameters text NOT NULL,
	                                        model_type text NOT NULL,
	                                        model text NOT NULL,
	                                        cat_col integer NOT NULL,
	                                        cont_col integer NOT NULL,
	                                        train_size integer NOT NULL); """	
	                                    
		self.__conn = self.__create_connection()
		if self.__conn is not None:
			self.__create_table()
        
	        
#########################################################################################	        


	def __likely_cat_cont(self,main_dataa):
	    likely_cat = []
	    likely_cont = []
	    shape = []
	    for var in main_dataa.columns:
	        if (main_dataa[var].nunique()/main_dataa[var].count() < 0.5):
	            likely_cat.append(var)
	        else:
	            likely_cont.append(var)    
	    shape.append(len(likely_cat))
	    shape.append(len(likely_cont))
	    return shape




	def __model_extractor(self,model,save_pickle,model_name):
    	#check the dtype
		try:
			temp = str(model.get_params) 
			temp2 = temp.split('(')[0]
			self.__Model = temp2.split('of')[1]
			temp3 = temp2.split('of')[0]
			self.__Model_type = temp3.split('method')[1].split('.')[0]
			if 'Stacking' in self.__Model:
				st2 = ""
				st1 = temp.split('(')[1:]
				st2 = st2.join(st1)
				st2 = " ".join(st2.split())
				self.__parameters = st2.replace(")>","") 
			else:			    
				parameters = temp.split('(')[1].split(')')[0]
				self.__parameters=parameters.replace("\n                   ","")
			#self.__class_len  = len(model.classes_)
			if(save_pickle == True):
				joblib.dump(model,f'{model_name}.pkl')
		except :
			warnings.warn("Model Unparseable Error - possible reasons /n 1. Passed object is not a model /n 2.Model is not fitted /nModel is not compatable with modelloger /n Check the docs to know more")
			print("Model is not compatable with Modelloger - /n consult the help() section ")


			
		


	def __create_project(self):
		try:
		    sql = ''' INSERT INTO models(model_name,accuracy,col_num,features,parameters,model_type,model,cat_col,cont_col,train_size)
		              VALUES(?,?,?,?,?,?,?,?,?,?) '''


            
		    cur = self.__conn.cursor()
		    cur.execute(sql, self.__project)
		    
		except Error as e:
			if "UNIQUE" in str(e):
				warnings.warn('Input warning - Not Unique Error')
				print('Model Name is not Unique , Please enter a name other than -')
				cur = self.__conn.cursor()
				cur.execute("SELECT model_name FROM models")
				rows = cur.fetchall()
				for row in rows:
					print(row)
			else:
				print(e)

	    #return cur.lastrowid


	def store_model(self,model_name,model,X_train,accuracy,save_pickle=False,Flag = False):	
		'''
           Store the model as fast as you can click
           Compatible with all sklearn models
           Parameters:
           -----------
		   model_name : <string> Give a unique name to your model . If not , it will throw
			           an warning and name of all models that are already been taken with it
		   model : <object>The model object (after calling fit())
		   columns : <dataframe> X_train , Dataframe used to train the model 
			        eg. X_train.columns 
		   accuracy : <int/float value or a function that returns int/float> Scores to measure 
			        the performance eg. rmse , mse , logloss or a custom function that returns a metric.
						Ideally same factor across all models will help gaining insights from summary
		   save_pickle : <boolean> If true than save the model as a pickle file with model_name as the
			            file name . Uses joblib for pickling ,to use it later use joblib.load('name')

		   Flag : <boolean> If true than will print out the contents of the db.

           Example:
           
           gboost = GradientBoostingClassifier()
           gboost.fit(X_train,y_train)
           mlog.store_model('my_model_name',gboost,[feat1,feat2,feat3,feat4],1.0)
           or
           mlog.store_model('my_model_name',gboost,X_train.columns,get_score(gboost),save_pickle = True)

		'''
		self.__model_extractor(model,save_pickle,model_name)
		temp_shape = self.__likely_cat_cont(X_train)
		self.__features = str(list(X_train.columns))
		self.__conn = self.__create_connection()
		self.__train_size = X_train.shape[0]
		self.__col_num = X_train.shape[1]
		if self.__conn is not None:
			with self.__conn:
				self.__project = (model_name,accuracy,self.__col_num,self.__features,self.__parameters,
					            self.__Model_type,self.__Model,temp_shape[0],temp_shape[1],self.__train_size
					            )
				self.__create_project()
				self.__select_all_tasks(Flag)


##########################################################################################


	def __select_all_tasks(self , Flag = False):
	    cur = self.__conn.cursor()
	    cur.execute("SELECT * FROM models")

	    rows = cur.fetchall()
	    temp_list = []
	    for row in rows:
	        temp_list.append(row)
	    #change the order    
	    df = pd.DataFrame(temp_list, columns =['Model id', 'Model Name', 'Score','Num cols', 'Feature List' , 'Parameters','Model_type','Model','NumCat','NumCont','Train size']) 
	    self.__df = df
	    if (Flag == True):
	    	 return df 

	        


	def view_results(self , generate_csv = False ,csv_name = "Model_Report"):
		'''
           Returns mini result in the form of a dataframe
           Parameters:
           ----------
			generate_csv : <boolean> If true than generate the report in the form of a csv
			csv_name : <string> Name of the csv file , default -- Model_Report.csv

           Example : 

           mlog.view_results(True,'my_report')           
		'''

		self.__conn = self.__create_connection()
		if self.__conn is not None:
			with self.__conn:
				temp = self.__select_all_tasks(Flag = True)

		if (generate_csv == True):
			temp.to_csv(f'{csv_name}.csv')				
		return temp			

################################################################################

	def __delete_model_id(self,Model_id):
		try:
			sql = 'DELETE FROM models WHERE model_id=?'
			cur = self.__conn.cursor()
			cur.execute(sql, (Model_id,))
			self.__conn.commit()
			#print(f'entry corresponding to Model Id : {Model_id} removed successfully')
		except Error as e:
			warnings.warn('Delete Model Error')
			print(e)
			



	def __delete_model_name(self,Model_Name):	
		try:
			sql = 'DELETE FROM models WHERE model_name=?'
			cur = self.__conn.cursor()
			cur.execute(sql, (Model_Name,))
			self.__conn.commit()
			#print(f'entry corresponding to Model Name : {Model_Name} removed successfully')
		except Error as e:
			warnings.warn('Delete Model Error')
			print(e)
			

	def delete_all(self,Flag=False):
		'''
		Deletes all model records present in the log . It however doesnot deletes pickle files
		Parameter:
		Flag : <boolean> If true than will print out the contents of the db.

		Example:
		--------

		mlog.delete_all()    

		'''
		try:
			sql = 'DELETE FROM models'
			self.__conn = self.__create_connection()
			if self.__conn is not None:
				with self.__conn:
					cur = self.__conn.cursor()
					cur.execute(sql)
					self.__conn.commit()
					self.__select_all_tasks(Flag)

		except Error as e:
			warnings.warn('Delete Table - Error')
			print(e)


	def info(self):
		print('<---------------model-logger--------------->')
		print("Description : model-logger is a Python library for storing model's profile and rapid inter model comparision./n Powered by dash and SQLITE3, It's compact ,light weight ,interactive yet powerful tool to gain usefull insights. ")
		print('Version : modellogger==0.2.0')
		print('Documentation : https://github.com/SohamPathak/modellogger.github.io')
		print('Requirements docs : https://github.com/SohamPathak/modellogger.github.io/blob/master/requirements.txt ')
		print('Have suggestions ? ping me up -- https://www.linkedin.com/in/kaisersoham/')



	def delete_model(self ,Model_Name = None,Model_id =None,Flag = False):
		'''
		Used to delete specific model  record . Either Model_Name or Model_id (or both) can be used in this case.
		Anyone of those is compulsory.
        Parameters :
		Model_name : <string /optional> name of the model you want to delete
		            --> use view_results() for referece 
		Model_id :<int / optional> id of the model 
		         --> use view_results() for referece
		Flag : <boolean> If true than will print out the contents of the db.
        
        Example:
        --------

        mlog.delete_model(Model_name = "Mymodel")
        mlog.delete_model(Model_id = 1)
		'''
		if((Model_Name ==None) & (Model_id ==None)):
			print('You need to pass either model id or model name')
			return

		self.__conn = self.__create_connection()
		if self.__conn is not None:
			with self.__conn:
				if((Model_Name ==None) & (Model_id !=None)): 
					self.__delete_model_id(Model_id)
				if((Model_Name !=None) & (Model_id ==None)): 
					self.__delete_model_name(Model_Name)

		self.__select_all_tasks(Flag)				


	def __distinct_count(self):
		try:
			sql = 'SELECT COUNT(*) FROM models'
			self.__conn = self.__create_connection()
			if self.__conn is not None:
				with self.__conn:
					cur = self.__conn.cursor()
					cur.execute(sql)
					size = cur.fetchall()
					

		except Error as e:
			warnings.warn('Count - Error')
			print(e)

		return size			


	def __listToString(self,s):  
	    
	    # initialize an empty string 
	    str1 = ""  
	    
	    # traverse in the string   
	    for ele in s:       
	        if (s[-2] == ele):
	            str1 += ele
	            str1 += " and "           
	        else:
	            str1 += ele
	            str1 += ", "            
	    
	    # return string   
	    return str1 


################################################################################
	def model_profiles(self , batch_size = "All" , port = 8050 , debug =False):
	    '''
	    Create a model summary sheet where you can play and gain insights from the different models
	    On calling the function a (dash)flask sever will get started and the url will be displayed . 
	    Use a web browser to view the summary page.
        As long as the server is running you can do dynamic data and graph manupulation .

	    Parameters:
	    ----------
	    batch_size : <int value or "All"> How many entries to consider at once while comparing via graphs
	                 If batch_size less than total number of entries , than it will 
	                 grouped into different pages . Different pages will have different
	                 graphs .
	                 If "All" is used than it will consider all the entries at once
        port:<int value> use to change the port number in which the server is running.
        debug:<boolean> If true than run the server in debug mode

        Note:
        -----
        For jupyter notebook ---> click on kernel/interrupt to stop the server 
        For cmd/anaconda prompt ----> use [ctrl+c] to stop the server .

	    Example:
	    --------

	    ml.model_profiles('All')
	    ml.model_profiles(5)             
	    '''
        
        
	    app = dash.Dash(__name__)
	    app.title = 'Modelloger'

	    self.__debug = debug
	    self.__port = port

	    df = self.__df

	    print("To Stop The Server In Jupyter Notebook Use Kernel Interrupt")

	    if batch_size == "All":
	    	PAGE_SIZE = self.__distinct_count()
	    	PAGE_SIZE = PAGE_SIZE[0][0]
	    	print("Batch Size :",PAGE_SIZE)
	    else :	
	    	PAGE_SIZE = batch_size
	     

	    app.layout = html.Div(
	        style={'backgroundColor': 'rgb(240, 240, 240)'},
	        className="row",
	        children=[
	            html.H1("SUMMARY SHEET",style={
	                                   'textAlign': 'center',
	                                    'color': 'black',
	                                    'font-family': 'sans-serif'}),
	            html.Hr(),
	            html.H1("Summary Data Table",style={
	                                   'textAlign': 'left',
	                                    'color': 'rgb(76, 175, 245)',
	                                    'font-family': 'sans-serif'}),
	            html.Hr(), 
	            html.Div(
	              
	                dash_table.DataTable(
	                    id='table-paging-with-graph',
	                    columns=[
	                        {"name": i, "id": i} for i in df.columns
	                    ],
	                    style_cell_conditional=[
	                    {
	                      'if': {'column_id': c},
	                      'textAlign': 'left'
	                    } for c in df.columns
	                    ],
	                    style_data_conditional=[
	                    {
	                      'if': {'row_index': 'odd'},
	                      'backgroundColor': 'rgb(248, 248, 248)'
	                     }
	                    ],
	                    style_header={
	                    'backgroundColor': 'rgb(230, 230, 230)',
	                    'fontWeight': 'bold',
	                    'border': '1px solid black' 
	                    },
	                    style_cell={ 'border': '1px solid grey' },

	                    page_current=0,
	                    page_size= PAGE_SIZE ,
	                    page_action='custom',

	                    filter_action='custom',
	                    filter_query='',

	                    sort_action='custom',
	                    sort_mode='multi',
	                    sort_by=[]
	                ),
	                style={'height': 275, 'overflowY': 'auto','backgroundColor': 'white'},
	                className='six columns'

	            ),
	            html.Hr(),
	            html.Div(
	                id='table-paging-with-graph-container',
	                className="five columns"
	            )
	        ]
	    )

	    operators = [['ge ', '>='],
	                 ['le ', '<='],
	                 ['lt ', '<'],
	                 ['gt ', '>'],
	                 ['ne ', '!='],
	                 ['eq ', '='],
	                 ['contains '],
	                 ['datestartswith ']]


	    def __split_filter_part(filter_part):
	        for operator_type in operators:
	            for operator in operator_type:
	                if operator in filter_part:
	                    name_part, value_part = filter_part.split(operator, 1)
	                    name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

	                    value_part = value_part.strip()
	                    v0 = value_part[0]
	                    if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
	                        value = value_part[1: -1].replace('\\' + v0, v0)
	                    else:
	                        try:
	                            value = float(value_part)
	                        except ValueError:
	                            value = value_part

	                    # word operators need spaces after them in the filter string,
	                    # but we don't want these later
	                    return name, operator_type[0].strip(), value

	        return [None] * 3


	    @app.callback(
	        Output('table-paging-with-graph', "data"),
	        [Input('table-paging-with-graph', "page_current"),
	         Input('table-paging-with-graph', "page_size"),
	         Input('table-paging-with-graph', "sort_by"),
	         Input('table-paging-with-graph', "filter_query")])
	    def __update_table(page_current, page_size, sort_by, filter):
	        filtering_expressions = filter.split(' && ')
	        dff = df
	        for filter_part in filtering_expressions:
	            col_name, operator, filter_value = __split_filter_part(filter_part)

	            if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
	                # these operators match pandas series operator method names
	                dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
	            elif operator == 'contains':
	                dff = dff.loc[dff[col_name].str.contains(filter_value)]
	            elif operator == 'datestartswith':
	                # this is a simplification of the front-end filtering logic,
	                # only works with complete fields in standard format
	                dff = dff.loc[dff[col_name].str.startswith(filter_value)]

	        if len(sort_by):
	            dff = dff.sort_values(
	                [col['column_id'] for col in sort_by],
	                ascending=[
	                    col['direction'] == 'asc'
	                    for col in sort_by
	                ],
	                inplace=False
	            )

	        return dff.iloc[ 
	            page_current*page_size: (page_current + 1)*page_size
	        ].to_dict('records')


	    @app.callback(
	        Output('table-paging-with-graph-container', "children"),
	        [Input('table-paging-with-graph', "data"),])

	   
	    def __update_graph(rows):
	        dff = pd.DataFrame(rows)
	        if (dff.shape[0] == 0):
	        	
	        	return html.Div([
	        		html.H1("No Entries Found !!",style={
		                                   'textAlign': 'left',
		                                    'color': 'rgb(245, 145, 145)',
		                                    'font-family': 'sans-serif'}),
	        		html.Hr(),])

	        if (dff.shape[0] != 0):
	        	
		        main_list = []
		        same_score = []
		        dublicate_score = []

		        # trace1 = go.Bar(x=dff['Model Name'], y=dff['Num cols'])
		        # trace2 = go.Bar(x=dff['Model Name'], y=dff['Num cols'])


		        for i in dff['Feature List']:
		            temp = ast.literal_eval(i)
		            for t in temp :
		                main_list.append(t)
		        temp_df = pd.DataFrame.from_dict(Counter(main_list), orient='index').reset_index()
		        temp_df = temp_df.rename(columns={'index':'Feature_name', 0:'count'})	

		        tmp = dff.groupby(['Score'])['Model Name'].apply(list).tolist()  
		        tmp2 =dff.groupby(['Score', 'Feature List', 'Parameters','Model_type', 'Model','Train size','Num cols'])['Model Name'].apply(list).tolist()

		        for values in tmp2:
		        	if len(values)>1:
		        		dublicate_score.append(self.__listToString(values)+' have same built and are pontentially duplicate.')



		        for values in tmp:
		        	if len(values)>1:
		        		best = values[0]
		        		for v in values:
		        			if int(dff[dff['Model Name']==v]['Num cols'])<int(dff[dff['Model Name']==best]['Num cols']):
		        				best = v		
		        		same_score.append(self.__listToString(values)+f'have similar score out of which {best} used minimum number of features.')

		        same_score_head = ''	
		        dublicate_head = ''
		        if (len(same_score)>0):	
		        	same_score_head = '⭕ Insights of the models with same score'
		        else:
		        	same_score_head = '✔️ No two models have same score'

		        if (len(dublicate_score)>0):	
		        	dublicate_head = '⭕ Insights of the models that are redundant'
		        else:
		        	dublicate_head = '✔️ No two models have same build'		

		        # print(len(dublicate_score))	        	


		        


		        return html.Div(
		            [   html.H1("Model Vs Score",style={
		                                   'textAlign': 'left',
		                                    'color': 'rgb(76, 175, 245)',
		                                    'font-family': 'sans-serif'}),
		                html.Hr(),


		                dcc.Graph(
		                    id="column",
		                    figure={
		                        "data": [
		                            {
		                                "x": dff["Model Name"],
		                                "y": dff["Score"],
		                                "type": "bar",
		                                "marker": {"color": "#0074D9"},
		                            }
		                        ],
		                        "layout": {
		                            "xaxis": {"automargin": True},
		                            "yaxis": {"automargin": True},
		                            "height": 300,
		                            "margin": {"t": 10, "l": 10, "r": 10},
		                        },
		                    },
		                ),
		                html.Hr(),
		                html.H1("Features Used by Models Vs Count ",style={
		                                   'textAlign': 'left',
		                                    'color': 'rgb(76, 175, 245)',
		                                    'font-family': 'sans-serif'}),
		                html.Hr(),
		                dcc.Graph(
		                    id="column2",
		                    figure={
		                        "data": [
		                            {
		                                "x": temp_df["Feature_name"],
		                                "y": temp_df['count'] ,
		                                "type": "bar",
		                                "marker": {"color": "#a532fc"},
		                            }
		                        ],
		                        "layout": {
		                            "xaxis": {"automargin": True},
		                            "yaxis": {"automargin": True},
		                            "height": 300,
		                            "margin": {"t": 10, "l": 10, "r": 10},
		                        },
		                    },
		                ),
		                html.Hr(),
		                html.H1("Number of Catagorical & continuous Features Per Model",style={
		                                   'textAlign': 'left',
		                                    'color': 'rgb(76, 175, 245)',
		                                    'font-family': 'sans-serif'}),
		                html.Hr(),
		                dcc.Graph(
		                    id="column2",
		                    figure={
		                        "data": [
		                            {
		                                "x": dff["Model Name"],
		                                "y": dff['NumCat'] ,
		                                "type": "bar",
		                                "name":'No. of Catagorical features',
		                                "marker": {"color": "#eb8034"},
		                            },
		                            {
		                                "x": dff["Model Name"],
		                                "y": dff['NumCont'] ,
		                                "name":'No. of Continuous features',
		                                "type": "bar",
		                                "marker": {"color": "#34eb40"},
		                            },

		                        ],
		                        "layout": {
		                            "xaxis": {"automargin": True},
		                            "yaxis": {"automargin": True},
		                            "height": 300,
		                            # "barmode":'stack',
		                            "margin": {"t": 10, "l": 10, "r": 10},
		                        },
		                    },
		                ),



		                html.Hr(),
		                html.H2(same_score_head,style={
		                                   'textAlign': 'left',
		                                    'color': 'rgb(76, 175, 245)',
		                                    'font-family': 'sans-serif'}),		                
                        html.Ul([html.Li(x) for x in same_score]),
		                html.H2(dublicate_head,style={
		                                   'textAlign': 'left',
		                                    'color': 'rgb(76, 175, 245)',
		                                    'font-family': 'sans-serif'}),	

                        html.Ul([html.Li(x) for x in dublicate_score]),
                        html.Hr(),



		            ]
		        )


	    app.run_server(dev_tools_prune_errors=True,debug = self.__debug,port=self.__port)